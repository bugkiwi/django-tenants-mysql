#!/usr/bin/env python 
#coding:utf-8

__author__ = 'gkiwi'

from django.db.backends.base import schema
from functools import wraps
from django.db.models.base import ModelBase
from django.db import connection


#method in schema.BaseDatabaseSchemaEditor

class SchemaEditorMixin(object):

    HOOK_METHODS = (
        '_model_indexes_sql',
        'remove_field',
        '_rename_field_sql',
        'delete_model',
        '_delete_constraint_sql',
        '_delete_composed_index',
        '_create_unique_sql',
        'create_model',
        '_create_index_sql',
        '_create_fk_sql',
        '_create_index_name',
        '_constraint_names',
        'column_sql',
        'alter_unique_together',
        '_alter_many_to_many',
        'alter_index_together',
        'alter_field',
        '_alter_field',
        'alter_db_tablespace',
        'alter_db_tablespace',
        'add_field'
    )

    def __getattribute__(self, item):
        _item = super(SchemaEditorMixin, self).__getattribute__(item)
        HOOK_METHODS = object.__getattribute__(self,'HOOK_METHODS')
        if item == 'HOOK_METHODS':
            return HOOK_METHODS

        if item not in HOOK_METHODS:
            return _item
        else:
            def decorator(func):
                @wraps(func)
                def wrapper(*args,**kwargs):
                    schema_name_prefix = connection.schema_name_prefix
                    for arg in args:
                        if isinstance(arg, ModelBase):
                            db_table = arg._meta.db_table
                            arg._meta.db_table = connection.get_schemaed_db_table(db_table)
                    for (k,v) in kwargs.items():
                        if isinstance(v, ModelBase):
                            db_table = v._meta.db_table
                            v._meta.db_table = connection.get_schemaed_db_table(db_table)
                    return func(*args,**kwargs)
                return wrapper
            return decorator(_item)

class BaseDataBaseSchemaEditor(SchemaEditorMixin, schema.BaseDatabaseSchemaEditor):
    pass
