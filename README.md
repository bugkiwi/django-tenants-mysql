
This application is base on [django-tenant-schemas](https://github.com/bernardopires/django-tenant-schemas), I try to use the same django command and with the same setting and can will support MySQL on multi-tenant;

I have test on python2.7.10, django1.9.5 and mysql5.6, and use it on my production, everything work well.

Actually, multi-tenant orm in MySQL is very different with PostgreSQL. PostgreSQL has **schemas** that looks like a directory in a operating system, and MySQL only have os and files:(

So I try give a prefix on table name for different tenant, then my db table looks like this:

```
    stanford$clazz
    stanford$student
    mit$clazz
    mit$student
```

There are three part of this libs, a django command for manage db, a migrate part, and a CRUD part.

Some tips:
If you use some django cache, remeber change they source for support multi-tenant(just take `connection.get_schema_name()` as part of cache key).

####How to use
1. Change your `DATABASES` engine
```
# project/settings.py
DATABASES = [

    'default': {
        'ENGINE': 'tenants.db.backends.mysql',
        # ..
    }
]
```

2. Give a middleware
If you use a url for different tenant, `TenantMiddleware` will work good. But If you use a header or a cookie value, you should use `TenantProMiddleware`;
```
# project/settings.py
MIDDLEWARE_CLASSES = [
    'tenants.middleware.TenantMiddleware' # or 'tenants.middleware.TenantProMiddleware'
]
```

3. Set a db router for stop SHARED_APPS migrate
You also to need give a router

```
# project/settings.py
DATABASE_ROUTERS = {
    'tenants.routers.TenantSyncRouter',
}
```

4. Create your tenant, look like
```
class Domain(TenantMixin):
    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return self.name
```

and tell `settings.py` where's that model.
```
# project/settings.py
TENANT_MODEL='domain.Domain' #or some model path your define
```

5. Give a patch
```
# project/wsgi.py bottom
application = get_wsgi_application()

import tenants.monkey
tenants.monkey.patch()
```
That step is diff from `bernardopires/django-tenant-schemas`, because I need to rewrite table name and row name where you CRUD.

---

You can find a doc for more detail on [bernardopires/django-tenant-schemas](`https://django-tenant-schemas.readthedocs.io/en/latest/`)

Some example in [script/tenant_add.py](./script/tenant_add.py), it will show you how to build a tenant;

I will give some test and support more version of django and python later.
