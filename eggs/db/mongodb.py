#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo


class Mongodb(object):
    def __init__(self, host, port, database, collection):
        self.__host = host
        self.__port = port
        self.__db_name = database
        self.__coll_name = collection
        self.__conn = None

    def __connect(self):
        if self.__conn is not None:
            self.__conn.close()
        try:
            self.__conn = pymongo.MongoClient(self.__host, self.__port)
            self.__db = self.__conn[self.__db_name]
            self.__collection = self.__db[self.__coll_name]
        except Exception, e:
            print 'connect update_ error:', e

    def disconnect(self):
        try:
            if self.__conn is not None:
                self.__conn.close()
        except Exception, e:
            print 'close update_ error:', e
        finally:
            self.__conn = None

    def get_db(self):
        if self.__conn is None:
            self.__connect()
        return self.__db

    def count(self, condition=None):
        if self.__conn is None:
            self.__connect()

        try:
            if condition is None:
                return self.__collection.count()

            if not isinstance(condition, dict):
                raise ValueError('`condition` is not dict type.')
            return self.query(condition).count()
        except Exception, e:
            print 'count error:', e

    def get(self, condition, kwargs=None, spec_sort=None):
        """`type(condition) is not dict` or `type(condition) == dict` is all right.
            condition is `spec_or_id` parameter of find_one function in pymongo
        """
        if type(condition) is not dict:
            raise TypeError('condition type error in get')
        if not isinstance(kwargs, (dict, type(None))):
                raise TypeError('`kwargs` fields type error.')

        if self.__conn is None:
            self.__connect()

        if kwargs is None and spec_sort is None:
            # `**{}` is dict in function parameter, also `fine_one` function `kwargs` parameter
            return self.__collection.find_one(condition)
        if kwargs and spec_sort is None:
            return self.__collection.find_one(condition, kwargs)

        if spec_sort and not isinstance(spec_sort, tuple):
            #  `_sort` type apply to python of win OS, maybe other OS isn't tuple
            raise TypeError('`sort` is empty or Type error.')
        if kwargs is None:
            return self.__collection.find(condition).sort([spec_sort]).limit(-1)[0]
        elif kwargs:
            return self.__collection.find(condition, kwargs).sort([spec_sort]).limit(-1)

    def query(self, condition=None, kwargs=None):
        if condition is None:
            condition = dict()

        if type(condition) is not dict:
            raise TypeError('condition type error in query')
        if not isinstance(kwargs, (dict, type(None))):
            raise TypeError('`kwargs` type error in query')

        if self.__conn is None:
            self.__connect()
        if kwargs is None:
            return self.__collection.find(condition, **{})
        elif kwargs:
            return self.__collection.find(condition, kwargs)

    def insert(self, data, batch=None):
        """
            data: eg, {...}, or [{...}, {...}, ...]
        """
        if self.__conn is None:
            self.__connect()

        try:
            self.__collection.insert(data)
        except Exception, e:
            print 'insert signal data error:', e

    def update(self, condition, setdata=None, unsetdata=None):
        """
            condition: indicate that get must a unique record in __collection.
                       if not, only update_ one record, others can not update_.
        """
        if type(condition) is not dict:
            raise TypeError('condition type error in update_')

        if self.__conn is None:
            self.__connect()
        try:
            if setdata is not None and unsetdata is None:
                return self.__collection.update(condition, {'$set': setdata})  # $set 修改文档里已有字段或新增一个新字段

            if unsetdata is not None and setdata is None:
                self.__collection.update(condition, {'$unset': unsetdata})  # $unset 删除一个字段，unsetdata为字段对应值

            if setdata is not None and unsetdata is not None:
                self.__collection.update(condition, {'$set': setdata})
                self.__collection.update(condition, {'$unset': unsetdata})
        except Exception, e:
            print 'update_ error:', e

    def distinct(self, key=None):
        if key is None:
            raise ValueError('key is None Error')

        if self.__conn is None:
            self.__connect()
        try:
            return self.__collection.distinct(key)
        except Exception, e:
            print 'distinct error:', e

    def remove(self, condition):
        """
            if condition is {}, then drop all the data of this collection, but this collection
            itself isn't dropped; otherwise remove qualified data.
        """
        if type(condition) is not dict:
            raise TypeError('condition type error in remove')

        if self.__conn is None:
            self.__connect()
        try:
            return self.__collection.remove(condition)
        except Exception, e:
            print 'remove error:', e


if __name__ == '__main__':
    coll_in = Mongodb('192.168.250.200', 27017, 'ada', 'announcement_hk_chz')
    print coll_in.get({'sid': 'http://www.hkexnews.hk/listedco/listconews/SEHK/2014/1211/LTN20141211825_C.pdf'}, {'title': 1})
    # db = pymongo.MongoClient('192.168.250.200', 27017)
    # coll = db['ada']['base_margin_trading']
    # print coll.find_one({'secu': '510880_SH_FD'}, so)
    #     print doc