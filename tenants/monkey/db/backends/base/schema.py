#!/usr/bin/env python 
#coding:utf-8

__author__ = 'gkiwi'

from django.db import connection

__all__ = ['BaseDatabaseSchemaEditor',]

class BaseDatabaseSchemaEditor(object):

    def _create_fk_sql(self, model, field, suffix):
        from_table = model._meta.db_table
        from_column = field.column
        to_table = connection.get_schemaed_db_table(field.target_field.model._meta.db_table)
        to_column = field.target_field.column
        suffix = suffix % {
            "to_table": to_table,
            "to_column": to_column,
        }

        return self.sql_create_fk % {
            "table": self.quote_name(from_table),
            "name": self.quote_name(self._create_index_name(model, [from_column], suffix=suffix)),
            "column": self.quote_name(from_column),
            "to_table": self.quote_name(to_table),
            "to_column": self.quote_name(to_column),
        }
