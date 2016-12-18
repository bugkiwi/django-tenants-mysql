#!/usr/bin/env python
#coding:utf-8

__author__ = 'gkiwi'
import os
import importlib
import warnings

OLD_DIR = os.path.abspath(os.curdir)
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def auto_patch():
    print("*"*50)
    print("Give a tenant.monkey pacth")
    print("*"*50)
    def get_path(path):
        if os.path.isfile(path):
            if path.endswith(".py"):
                paths.append(path)
        else:
            for _path in os.listdir(path):
                get_path(os.path.join(path,_path))

    def replace_cls_method(old,new):
        """
        replace old method by the new one;
        only replace method
        :param old:
        :param new:
        :return:
        """
        for (item,value) in new.__dict__.items():
            if hasattr(value,'__call__') and hasattr(old,item):
                setattr(old,item,value)

    def _patch(path):
        if path == '__init__':
            return

        module = importlib.import_module('tenants.monkey.{name}'.format(name=path))
        if not hasattr(module,'__all__'):
            return

        for cls in module.__all__:
            new = getattr(module,cls)
            try:
                old_module = importlib.import_module('django.{name}'.format(name=path))
                if hasattr(old_module,cls):
                    old = getattr(old_module,cls)
                else:
                    raise ImportError
                replace_cls_method(old,new)
            except ImportError:
                warnings.warn("django.{path}.{cls} not Exist, please check your monkey path".format(path=path,cls=cls))
    os.chdir(THIS_DIR)
    paths = []
    get_path('.')
    for path in paths:
        path = path[2:-3]
        path = path.replace('/','.')
        _patch(path)
    os.chdir(OLD_DIR)

patch = auto_patch

if __name__=='__main__':
    auto_patch()
