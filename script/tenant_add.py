#!/usr/bin/env python
#coding:utf-8
from __future__ import absolute_import
import sys
if sys.getdefaultencoding()=='ascii':
    reload(sys)
    sys.setdefaultencoding('utf-8')
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

import django
django.setup()

import tenants.monkey
tenants.monkey.patch()

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import connection
from tenants.utils import get_tenant_model
from utils import rand

"""
INSERT INTO `public$domain_domain` (`domain_url`, `schema_name`, `name`, `created_on`)
VALUES ('public.example.com','public','some pub','2016-09-18');
"""
def rand_str(length):
    """
        return a random str with digits
    """
    import string
    import random

    poolOfChars  = string.ascii_letters + string.digits
    random_codes = lambda x, y: ''.join([random.choice(x) for i in range(y)])
    return random_codes(poolOfChars, length)

if __name__ == '__main__':
    TenantModel = get_tenant_model()
    schema_name = 'mit'
    name = "Mit"
    data = {
            "domain_url" :'%s.example.com'%schema_name,
            "schema_name" : schema_name,
            "name" : name
    }

    tenants = TenantModel.objects.filter(Q(domain_url=data['domain_url'])|Q(schema_name=data['schema_name']))
    if len(tenants)>0:
        print("An tenant has exist(schema_name or domain_url):")
        print(tenants[0],data)
    else:
        tenant = TenantModel(**data)
        tenant.save()
        print("*"*50)
        print("Tenant has been created:",tenant)
        print("-"*20)
        connection.set_tenant(tenant)
        User = get_user_model()
        passwd = rand.random_str(10)
        User.objects.create_superuser('admin','admin@example.com',passwd)
        print("create admin user: admin/{passwd}"%passwd)
