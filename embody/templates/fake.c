#include "{{ fake_include }}"

{% for func in funcs %}
{{ func }} {
}{% if not loop.last %}
{% endif -%}
{% endfor %}
