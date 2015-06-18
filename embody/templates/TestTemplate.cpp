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

#include "CppUTest/TestHarness.h"
#include "{{ module_name }}.h"

TEST_GROUP({{ module_name }}Tests) {
    void setup()
    {
    }

    void teardown()
    {
    }
};

TEST({{ module_name }}Tests, DummyTest) {
    FAIL("No tests for module {{ module_name }}");
}
