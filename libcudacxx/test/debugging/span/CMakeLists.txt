libcudacxx_add_pretty_printer_test(
  NAME span
  SOURCES source.cu
  CASES
    # gersemi: off
    --case inspect_normal_dynamic 1 span.normal.dynamic normal_dynamic
    --case inspect_normal_static 1 span.normal.static normal_static
    --case inspect_empty_dynamic 1 span.empty.dynamic empty_dynamic
    --case inspect_empty_static 1 span.empty.static empty_static
    --case inspect_single 1 span.single single
    --case inspect_alias 1 span.alias alias
    --case inspect_const 1 span.const const_span
    --case inspect_const_element 1 span.const_element const_element
    --case inspect_pointer_element 1 span.pointer_element pointer_element
    --case inspect_nested 1 span.nested nested
    --case inspect_vector 1 span.vector.0 "span_vector[0]"
    --case inspect_vector 1 span.vector.1 "span_vector[1]"
    --case inspect_before_update 1 span.update.before updated_values
    --case inspect_after_update 1 span.update.after updated_values
    # gersemi: on
)
