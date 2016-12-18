#!/usr/bin/env python 
#coding:utf-8

__author__ = 'gkiwi'

from django.db.backends.mysql import schema
from tenants.db.backends.base.schema import SchemaEditorMixin


class DatabaseSchemaEditor(SchemaEditorMixin, schema.DatabaseSchemaEditor):

    def __init__(self, *args, **kwargs):
        super(DatabaseSchemaEditor,self).__init__(*args, **kwargs)