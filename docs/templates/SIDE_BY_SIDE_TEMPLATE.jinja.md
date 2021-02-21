{% macro show_example(example) -%}
<table>
<tr>
<th>JSON</th>
<th>YAML</th>
</tr>
<tr>
<td>
<pre>
{{ example.json }}
</pre>
</td>
<td>

```yaml
{{ example.yaml }}
```

</td>
</tr>
</table>

{%- endmacro %}
{% for key, example in examples.items() %}
## {{ key }}
{{ show_example(example) }}
{% endfor %}
