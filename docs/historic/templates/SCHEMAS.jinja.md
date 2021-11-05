Built in Field Spec Type Schemas
================================
{% macro show_schema(schema_info) %}
# <a name="{{ schema_info.tag }}"></a>{{ schema_info.title }}
{% if schema_info.type_names is defined %}
Types covered by schema: `{{ schema_info.type_names }}`
{% endif %}
<details>
  <summary>JSON Schema</summary>

```json
{{ schema_info.schema }}
```
</details>
{% endmacro %}
{% for schema_info in schemas %}
1. [{{ schema_info.title }}](#{{ schema_info.tag }}){%- endfor %}

{% for schema_info in schemas -%}
{{ show_schema(schema_info) }}
{%- endfor %}
