/*
 * Tests for the {{ module_name }} module.{% if project_name %} Part of project {{ project_name }}.{% endif %}

 *
 * Copyright {{ year }} {% if copyright_holder %}
{{ copyright_holder }}{% else %}
{{ author }}{% endif %}

{% if copyright_holder %}
 * Written by {{ author }}
{% endif %}
 */

{% filter section_header %}Includes{% endfilter %}


#include "CppUTest/TestHarness.h"
{% if sys_includes or project_includes %}
{% for include in sys_includes %}
#include <{{ include }}>
{% endfor %}
{% for include in project_includes %}
#include "{{ include }}"
{% endfor %}

{% endif %}
{% filter section_header %}Defines and Types{% endfilter %}


{% filter section_header %}Test Group Definition{% endfilter %}


TEST_GROUP({{ module_name }}Tests) {
    void setup()
    {
    }

    void teardown()
    {
    }
};

{% filter section_header %}Test Definitions{% endfilter %}


TEST({{ module_name }}Tests, DummyTest) {
    FAIL("No tests for module {{ module_name }}");
}
