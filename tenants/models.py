from __future__ import unicode_literals

from django.db import models, connection
from django.db.backends.utils import truncate_name
from tenants.utils import get_public_schema_name, schema_exists
from tenants.signals import post_schema_sync
from tenants.db.validate import schema_name_validate
from django.core.management import call_command


class TenantMixin(models.Model):
    """
    All tenant models must inherit this class.
    """

    auto_drop_schema = False
    """
    USE THIS WITH CAUTION!
    Set this flag to true on a parent class if you want the schema to be
    automatically deleted if the tenant row gets deleted.
    """

    auto_create_schema = True
    """
    Set this flag to false on a parent class if you don't want the schema
    to be automatically created upon save.
    """

    domain_url = models.CharField(max_length=128, unique=True)
    schema_name = models.CharField(max_length=63, unique=True,
                                   validators=[schema_name_validate])
    class Meta:
        abstract = True

    def save(self, verbosity=1, *args, **kwargs):
        is_new = self.pk is None

        if is_new and connection.schema_name != get_public_schema_name():
            raise Exception("Can't create tenant outside the public schema. "
                            "Current schema is %s." % connection.schema_name)
        elif not is_new and connection.schema_name not in (self.schema_name, get_public_schema_name()):
            raise Exception("Can't update tenant outside it's own schema or "
                            "the public schema. Current schema is %s."
                            % connection.schema_name)

        super(TenantMixin, self).save(*args, **kwargs)

        if is_new and self.auto_create_schema:
            try:
                self.create_schema(check_if_exists=True, verbosity=verbosity)
            except:
                # We failed creating the tenant, delete what we created and
                # re-raise the exception
                connection.set_schema_to_public()
                self.delete(force_drop=True)
                raise
            else:
                post_schema_sync.send(sender=TenantMixin, tenant=self)

    def delete(self, force_drop=False, *args, **kwargs):
        """
        Deletes this row. Drops the tenant's schema if the attribute
        auto_drop_schema set to True.
        """
        if connection.schema_name not in (self.schema_name, get_public_schema_name()):
            raise Exception("Can't delete tenant outside it's own schema or "
                            "the public schema. Current schema is %s."
                            % connection.schema_name)

        if schema_exists(self.schema_name) and (self.auto_drop_schema or force_drop):
            self.delete_schema()

        super(TenantMixin, self).delete(*args, **kwargs)

    def create_schema(self, check_if_exists=False, sync_schema=True,
                      verbosity=1):
        """
        Creates the schema 'schema_name' for this tenant. Optionally checks if
        the schema already exists before creating it. Returns true if the
        schema was created, false otherwise.
        """

        # safety check
        schema_name_validate(self.schema_name)
        cursor = connection.cursor()

        if sync_schema:
            call_command('migrate_schemas',
                         schema_name=self.schema_name,
                         interactive=False,
                         verbosity=verbosity)

        connection.set_schema_to_public()

    def delete_schema(self):
        #for mysql:
        # raise NotImplementedError('Should Write for diff db engine')
        #TOFO
        cursor = connection.cursor()
        tables = connection.introspection.get_table_list(connection.cursor())
        cur_schema_filted_tables = [table.name for table in tables if table.name.startswith(connection.schema_name_prefix)]

        raise Exception('------------')
