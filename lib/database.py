#!/usr/bin/env python
# coding=utf-8

from playhouse.signals import Model as _model
from playhouse.pool import PooledMySQLDatabase
import peewee
import simplejson


class Db(object):
    fn = peewee.fn
    JOIN_LEFT_OUTER = peewee.JOIN_LEFT_OUTER
    def __init__(self, kw):
        self.config = kw
        self.load_database()
        self.Model = self.get_model_class()

    def load_database(self):
        self.database = PooledMySQLDatabase(self.config.pop('db'), threadlocals=True, **self.config)

    def get_model_class(self):
        class BaseModel(_model):
            def __str__(self):
                r = {}
                for k in self._data.keys():
                  try:
                     r[k] = str(getattr(self, k))
                  except:
                     r[k] = simplejson.dumps(getattr(self, k))
                return str(r)
            class Meta:
                database = self.database

        return BaseModel

    def connect(self):
        self.database.connect()

    def close(self):
        try:
            self.database.close()
        except:
            pass

    @property
    def handle(self):
        return self.database