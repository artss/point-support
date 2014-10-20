workers = 1

libs = ['/home/point/core/lib']

domain = 'point.im'

api_slug = 'point-issues'
api_login = ''
api_password = ''

cache_socket = 'tcp://127.0.0.1:16380'
storage_socket = 'unix:///var/run/redis/storage.sock'
pubsub_socket = 'unix:///var/run/redis/pubsub.sock'

db = {
    'host': '127.0.0.1',
    'port': 5432,
    'database': 'point',
    'user': 'point',
    'password': 'point',
    'maxsize': 10
}

template_path = '/home/point/support/templates'

media_root = 'https://i.point.im/m'

lang = 'en'
timezone = 'Europe/Moscow'

actions_interval = 0
edit_expire = 0

logger = 'support'
logformat = u'%(asctime)s %(process)d %(filename)s:%(lineno)d:%(funcName)s %(levelname)s  %(message)s'
logfile = '/home/point/log/support.log'
loglevel = 'error'
logrotate = None
logcount = 7

debug = False

try:
    from settings_local import *
except ImportError:
    pass

