{% extends "Common.c" %}

{% block body %}
{% filter section_header %}Static Data{% endfilter %}


{% filter section_header %}Static Function Declarations{% endfilter %}


{% if static_funcs %}
{% for func in static_funcs %}{{ func }};
{% endfor %}

{% endif %}
{% filter section_header %}Exported Function Definitions{% endfilter %}


{% for func in exported_funcs %}
{{ func }} {
}

{% endfor %}
{% filter section_header %}Static Function Definitions{% endfilter %}

{% if static_funcs %}

{% for func in static_funcs %}
{{ func }} {
}
{% if not loop.last %}

{% endif %}
{% endfor %}
{% endif %}
{% endblock %}
