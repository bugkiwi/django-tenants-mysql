#!/usr/bin/env python 
#coding:utf-8

__author__ = 'gkiwi'
import warnings
from tenants.utils import get_public_schema_name

class DatabaseWrapperMixin(object):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapperMixin, self).__init__(*args, **kwargs)

        # Use a patched version of the DatabaseIntrospection that only returns the table list for the
        # currently selected schema.
        # self.introspection = DatabaseSchemaIntrospection(self)
        self.set_schema_to_public()

    def set_tenant(self, tenant):
        """
        Main API method to current database schema,
        but it does not actually modify the db connection.
        """
        self.tenant = tenant
        self.schema_name = tenant.schema_name

    def set_schema(self, schema_name):
        """
        Main API method to current database schema,
        but it does not actually modify the db connection.
        """
        self.tenant = FakeTenant(schema_name=schema_name)
        self.schema_name = schema_name

    def set_schema_to_public(self):
        """
        Instructs to stay in the common 'public' schema.
        """
        self.tenant = FakeTenant(schema_name = get_public_schema_name())
        self.schema_name = get_public_schema_name()

    def get_schema_name(self):
        return self._schema_name

    def set_schema_name(self,value):
        self._schema_name = value
        self.schema_name_prefix = value+"$"

    schema_name = property(get_schema_name, set_schema_name)

    def get_schema(self):
        warnings.warn("connection.get_schema() is deprecated, use connection.schema_name instead.",
                      category=DeprecationWarning)
        return self.schema_name

    def get_schemaed_db_table(self, db_table):
        # if db_table.startswith(self.schema_name_prefix):
        #     return db_table
        # else:
        db_table = db_table.split("$")[-1]
        return self.schema_name_prefix+db_table

    def get_pure_db_table(self, db_table):
        return db_table.replace(self.schema_name_prefix,'')

    def schema_exists(self, schema_name):
        raise NotImplementedError("subclasses of DatabaseWrapperMixin may require a schema_exists() method")

class FakeTenant:
    """
    We can't import any db model in a backend (apparently?), so this class is used
    for wrapping schema names in a tenant-like structure.
    """
    def __init__(self, schema_name):
        self.schema_name = schema_name
