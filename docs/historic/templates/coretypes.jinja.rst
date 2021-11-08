Core Types
===========

These are the built in field spec types.

{%- macro show_type(type) -%}
{{ type.name }}
{% for _ in range(type.name | length) %}-{% endfor %}

.. automodule:: datagen.supplier.core.{{ type.name }}

{% endmacro %}

{% for type in types -%}
{{ show_type(type) }}
{%- endfor %}