{% extends "common.c" %}

{% block body %}
{% filter section_header %}Exported Function Declarations{% endfilter %}

{% if exported_funcs %}

{% for func in exported_funcs %}
{{ func }};
{% endfor %}
{% endif %}
{% endblock %}
