#!/usr/bin/env python
# coding=utf-8

import re
import time
from peewee import *
import hashlib
from bootloader import db
from playhouse.signals import post_save
from lib.util import vmobile
import logging
import setting


# logger = logging.getLogger('peewee')
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())



def initDB():
    from lib.util import find_subclasses

    models = find_subclasses(db.Model)
    for model in models:
        if model.table_exists():
            print model
            model.drop_table()
        model.create_table()

if __name__ == '__main__':
    pass

