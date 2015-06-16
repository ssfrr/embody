/*
 * {{ module_name }} module.{% if project_name %} Part of project {{ project_name }}.{% endif %}

 *
 * Copyright {{ year }} {{ author }}
{% if written_by %}
 * Written by {{ written_by }}
{% endif %}
 */

{% if use_include_guard %}
#ifndef {{ filename|include_guard }}
#define {{ filename|include_guard }}

{% endif %}
{% filter section_header %}Includes{% endfilter %}


{% if sys_includes or project_includes %}
{% for include in sys_includes %}
#include <{{ include }}>
{% endfor %}
{% for include in project_includes %}
#include "{{ include }}"
{% endfor %}

{% endif %}
{% filter section_header %}Defines and Types{% endfilter %}


{% if defines %}
{% for name in defines %}
#define {{ name }} {{ defines[name] }}
{% endfor %}

{% endif %}
{% if types %}
{% for type in types %}{{ type }};
{% endfor %}

{% endif %}
{% block body %}
{% endblock %}
{% if use_include_guard %}

#endif // {{ filename|include_guard }}
{% endif %}
