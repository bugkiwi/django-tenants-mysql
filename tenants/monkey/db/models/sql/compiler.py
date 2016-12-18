#!/usr/bin/env python 
#coding:utf-8

__author__ = 'gkiwi'
from django.db import connection

__all__ = ['SQLCompiler','SQLInsertCompiler','SQLDeleteCompiler','SQLUpdateCompiler',]

class SQLCompiler(object):

    def get_from_clause(self):
        """
        Returns a list of strings that are joined together to go after the
        "FROM" part of the query, as well as a list any extra parameters that
        need to be included. Sub-classes, can override this to create a
        from-clause via a "select".

        This should only be called after any SQL construction methods that
        might change the tables we need. This means the select columns,
        ordering and distinct must be done first.
        """
        result = []
        params = []
        for alias in self.query.tables:
            if not self.query.alias_refcount[alias]:
                continue
            try:
                from_clause = self.query.alias_map[alias]
            except KeyError:
                # Extra tables can end up in self.tables, but not in the
                # alias_map if they aren't in a join. That's OK. We skip them.
                continue
            clause_sql, clause_params = self.compile(from_clause)
            result.append(clause_sql)
            params.extend(clause_params)
        for t in self.query.extra_tables:
            alias, _ = self.query.table_alias(t)
            # Only add the alias if it's not already present (the table_alias()
            # call increments the refcount, so an alias refcount of one means
            # this is the only reference).
            if alias not in self.query.alias_map or self.query.alias_refcount[alias] == 1:
                #gkiwi
                result.append(', %s' % self.quote_name_unless_alias(self.connection.get_schemaed_db_table(alias)))
        return result, params

class SQLInsertCompiler(object):
    def as_sql(self):
        # We don't need quote_name_unless_alias() here, since these are all
        # going to be column names (so we can avoid the extra overhead).
        qn = self.connection.ops.quote_name
        opts = self.query.get_meta()
        result = ['INSERT INTO %s' % qn(connection.get_schemaed_db_table(opts.db_table))]

        has_fields = bool(self.query.fields)
        fields = self.query.fields if has_fields else [opts.pk]
        result.append('(%s)' % ', '.join(qn(f.column) for f in fields))

        if has_fields:
            value_rows = [
                [self.prepare_value(field, self.pre_save_val(field, obj)) for field in fields]
                for obj in self.query.objs
                ]
        else:
            # An empty object.
            value_rows = [[self.connection.ops.pk_default_value()] for _ in self.query.objs]
            fields = [None]

        # Currently the backends just accept values when generating bulk
        # queries and generate their own placeholders. Doing that isn't
        # necessary and it should be possible to use placeholders and
        # expressions in bulk inserts too.
        can_bulk = (not self.return_id and self.connection.features.has_bulk_insert)

        placeholder_rows, param_rows = self.assemble_as_sql(fields, value_rows)

        if self.return_id and self.connection.features.can_return_id_from_insert:
            params = param_rows[0]
            # gkiwi no need ??
            col = "%s.%s" % (qn(connection.get_schemaed_db_table(opts.db_table)), qn(opts.pk.column))
            result.append("VALUES (%s)" % ", ".join(placeholder_rows[0]))
            r_fmt, r_params = self.connection.ops.return_insert_id()
            # Skip empty r_fmt to allow subclasses to customize behavior for
            # 3rd party backends. Refs #19096.
            if r_fmt:
                result.append(r_fmt % col)
                params += r_params
            return [(" ".join(result), tuple(params))]

        if can_bulk:
            result.append(self.connection.ops.bulk_insert_sql(fields, placeholder_rows))
            return [(" ".join(result), tuple(p for ps in param_rows for p in ps))]
        else:
            return [
                (" ".join(result + ["VALUES (%s)" % ", ".join(p)]), vals)
                for p, vals in zip(placeholder_rows, param_rows)
                ]

class SQLDeleteCompiler(object):

    def as_sql(self):
        """
        Creates the SQL for this query. Returns the SQL string and list of
        parameters.
        """
        assert len([t for t in self.query.tables if self.query.alias_refcount[t] > 0]) == 1, \
            "Can only delete from one table at a time."
        qn = self.quote_name_unless_alias
        db_table = self.query.tables[0]
        schemaed_db_table = connection.get_schemaed_db_table(db_table)
        result = ['DELETE {db_table} FROM {schemaed_db_table} {db_table}'.format(
                schemaed_db_table = qn(schemaed_db_table),
                db_table = qn(db_table)
            )]
        where, params = self.compile(self.query.where)
        if where:
            result.append('WHERE %s' % where)
        return ' '.join(result), tuple(params)

class SQLUpdateCompiler(SQLCompiler):
    def as_sql(self):
        """
        Creates the SQL for this query. Returns the SQL string and list of
        parameters.
        """
        self.pre_sql_setup()
        if not self.query.values:
            return '', ()
        qn = self.quote_name_unless_alias
        db_table = self.query.tables[0]
        schemaed_db_table = connection.get_schemaed_db_table(db_table)
        result = ['UPDATE {schemaed_db_table} {db_table}'.format(
                schemaed_db_table = qn(schemaed_db_table),
                db_table = qn(db_table)
            )]
        result.append('SET')
        values, update_params = [], []
        for field, model, val in self.query.values:
            if hasattr(val, 'resolve_expression'):
                val = val.resolve_expression(self.query, allow_joins=False, for_save=True)
                if val.contains_aggregate:
                    raise FieldError("Aggregate functions are not allowed in this query")
            elif hasattr(val, 'prepare_database_save'):
                if field.remote_field:
                    val = field.get_db_prep_save(
                        val.prepare_database_save(field),
                        connection=self.connection,
                    )
                else:
                    raise TypeError(
                        "Tried to update field %s with a model instance, %r. "
                        "Use a value compatible with %s."
                        % (field, val, field.__class__.__name__)
                    )
            else:
                val = field.get_db_prep_save(val, connection=self.connection)

            # Getting the placeholder for the field.
            if hasattr(field, 'get_placeholder'):
                placeholder = field.get_placeholder(val, self, self.connection)
            else:
                placeholder = '%s'
            name = field.column
            if hasattr(val, 'as_sql'):
                sql, params = self.compile(val)
                values.append('%s = %s' % (qn(name), sql))
                update_params.extend(params)
            elif val is not None:
                values.append('%s = %s' % (qn(name), placeholder))
                update_params.append(val)
            else:
                values.append('%s = NULL' % qn(name))
        if not values:
            return '', ()
        result.append(', '.join(values))
        where, params = self.compile(self.query.where)
        if where:
            result.append('WHERE %s' % where)
        return ' '.join(result), tuple(update_params + params)
