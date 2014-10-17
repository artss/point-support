From @{{author}}: {{tags|join(", ")}}

{{text}}

{% if files %}{% for f in files %}
{{settings.media_root}}/{{f}}
{% endfor %}{% endif %}

https://point.im/{{post_id}}
