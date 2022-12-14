create function debug_fn() returns trigger
    language plpgsql
as
$$

declare
  carriage_return constant varchar(1) = E'\r';
  newline constant varchar(1) = E'\n';
begin
  raise notice 'kajdlaksjdlkasdjlaksd';
  if TG_RELNAME = 'INSERT' or TG_RELNAME = 'UPDATE' then
    return new;
  else
    return old;
end if;
end;

$$;

alter function debug_fn() owner to postgres;

-- grant execute on function dbf_cofk_union_audit_literal_delete(varchar, varchar, integer, text, varchar, text) to editor_role_cofk;

