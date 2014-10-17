"""
Support bot worker
"""
import settings

import os
import gevent
from gevent import monkey; monkey.patch_all()

from geweb import log
from point.util import proctitle
from point.util import cache_get, cache_store
from point.util.redispool import RedisPool
from point.util.env import env
from point.core.user import User, UserNotFound
from point.core.post import PostError, CommentError
from point.app.posts import add_comment
import json
from jinja2 import Environment, FileSystemLoader
from bitbucket.bitbucket import Bitbucket
from bitbucket.issue import Issue

FR_TAGS = set(['feature', 'request', 'feature request', 'featurerequest',
               'reature_request', 'fr', 'enhancement'])
BUG_TAGS = set(['bug', 'report', 'bug report', 'bugreport',
                'bug_report', 'br'])

jinja_env = Environment(loader=FileSystemLoader(settings.template_path))

def template(template_name, **args):
    tmpl = jinja_env.get_template(template_name)
    return tmpl.render(settings=settings, **args)

class SupportWorker(object):
    """SupportWorker class"""
    def __init__(self):
        proctitle('support-worker')
        log.info('support worker started with PID=%s' % os.getpid())

        pool = RedisPool(settings.pubsub_socket)
        pubsub = pool.pubsub()
        pubsub.subscribe(['msg'])

        for msg in pubsub.listen():
            try:
                data = json.loads(msg['data'])
            except TypeError:
                continue
            if data['a'] in ('post', 'post_edited'):
                gevent.spawn(self.handle_post, data)

    def handle_post(self, data):
        """Handle post
        """
        if data['private']:
            return

        if len(data['tags']) == 0 or 'point' not in data['tags']:
            return

        tagset = set(data['tags'])

        if tagset & FR_TAGS:
            issue_type = 'enhancement'
        elif tagset & BUG_TAGS:
            issue_type = 'bug'
        else:
            return

        if cache_get('issue-post:%s' % data['post_id']):
            return

        text = template('report.md', **data)

        args = {
            'kind': issue_type,
            'title': data['text'][:100],
            'content': text,
        }

        bb = Bitbucket(settings.api_login, settings.api_password,
                       settings.api_slug)

        issue = Issue(bb)
        status, resp = issue.create(**args)

        try:
            env.user = User('login', 'support')
        except UserNotFound:
            return

        reply = template('reply.txt', issue=resp['local_id'])

        try:
            add_comment(data['post_id'], None, text=reply,
                        dont_subscribe=True, force=True)
        except (PostError, CommentError), e:
            log.error(e)
            return

        cache_store('issue-post:%s' % data['post_id'], 1,
                    expire=60*60*24)

if __name__ == '__main__':
    SupportWorker()

