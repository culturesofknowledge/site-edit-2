create function dbf_cofk_union_audit_literal_insert(input_table_name character varying, input_key_value_text character varying, input_key_value_integer integer, input_key_decode text, input_column_name character varying, input_new_column_value text) returns void
    language plpgsql
as
$$

declare
  carriage_return constant varchar(1) = E'\r';
  newline constant varchar(1) = E'\n';
begin

  if trim( replace( replace( coalesce( input_new_column_value, '' ), carriage_return, '' ), newline, '' )) > ''
  then

    insert into cofk_union_audit_literal(
      change_type,
      table_name,
      key_value_text      ,
      key_value_integer   ,
      key_decode          ,
      column_name         ,
      new_column_value
    )
    values (
      'New',
      input_table_name          ,
      input_key_value_text      ,
      input_key_value_integer   ,
      input_key_decode          ,
      input_column_name         ,
      input_new_column_value
    );

  end if;

  return;
end;

$$;

alter function dbf_cofk_union_audit_literal_insert(varchar, varchar, integer, text, varchar, text) owner to postgres;

-- grant execute on function dbf_cofk_union_audit_literal_insert(varchar, varchar, integer, text, varchar, text) to editor_role_cofk;

