#!/usr/bin/env python 
#coding:utf-8

__author__ = 'gkiwi'
from django.db.utils import DatabaseError
from django.db.migrations.exceptions import MigrationSchemaMissing


__all__ = ['MigrationRecorder']

class MigrationRecorder(object):
    def ensure_schema(self):
        """
        Ensures the table exists and has the correct schema.
        """
        # If the table's there, that's fine - we've never changed its schema
        # in the codebase.

        # gkiwi #TOPATCH
        from django.db import connection
        db_table = connection.get_schemaed_db_table(self.Migration._meta.db_table)
        # end

        if db_table in self.connection.introspection.table_names(self.connection.cursor()):
            return
        # Make the table
        try:
            with self.connection.schema_editor() as editor:
                editor.create_model(self.Migration)
        except DatabaseError as exc:
            raise MigrationSchemaMissing("Unable to create the django_migrations table (%s)" % exc)
