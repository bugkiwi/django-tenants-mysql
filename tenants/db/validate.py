SQL_SCHEMA_RESERVED = ('admin',)


def schema_name_validate(schema_name):
    return schema_name not in SQL_SCHEMA_RESERVED