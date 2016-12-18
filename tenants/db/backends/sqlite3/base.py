import re
import warnings
from django.conf import settings
try:
    # Django versions >= 1.9
    from django.utils.module_loading import import_module
except ImportError:
    # Django versions < 1.9
    from django.utils.importlib import import_module

from django.core.exceptions import ImproperlyConfigured, ValidationError
from tenants.utils import get_public_schema_name
from tenants.db.backends.base import DatabaseWrapperMixin
from .schema import DatabaseSchemaEditor

try:
    # Django versions >= 1.9
    from django.utils.module_loading import import_module
except ImportError:
    # Django versions < 1.9
    from django.utils.importlib import import_module

ORIGINAL_BACKEND = getattr(settings, 'ORIGINAL_BACKEND', 'django.db.backends.sqlite3')

original_backend = import_module(ORIGINAL_BACKEND + '.base')


class DatabaseWrapper(DatabaseWrapperMixin, original_backend.DatabaseWrapper):
    SchemaEditorClass = DatabaseSchemaEditor

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper,self).__init__(*args, **kwargs)

    def schema_exists(self, schema_name):
        sql = 'select 1 from sqlite_master where name like "%%%{schema_name_prefix}s"'.format(
                    schema_name_prefix = self.schema_name_prefix
                )
        cursor = self.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        if row:
            exists =True
        else:
            exists = False

        cursor.close()
        return exists
