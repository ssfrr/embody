#include "{{ fake_include }}"

{% for f in funcs %}
{{ f.ret_type }} {{ f.name }}(
    {%- for a in f.args -%}
        {{ a[0] }}{% if a[0][-1] != '*' %} {% endif %}{{ a[1] }}
        {%- if not loop.last %}, {% endif %}
    {%- endfor %}) {
}{% if not loop.last %}
{% endif -%}
{% endfor %}
