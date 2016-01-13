#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import os.path
import xlwt
import xlrd
from datetime import datetime


class XlsxWriter(object):
    """
        XlsxWriter class wrap the xlwt to write data to excel
        Note: this module write 65535 line in a sheet at most
        other: `csv` also, but csv file could accommodate 100w+ datas, otherwise file type of
                xlwt generating can not
    """
    def __init__(self, excel_path, sheet_name='sheet1', headers=None, flush_bound=8192):
        self.__save_path = excel_path
        self.__sheet_name = sheet_name
        self.__flush = flush_bound
        self.__headers = headers if headers is not None else []
        self.__workbook = xlwt.Workbook(encoding='utf-8')
        self.__w_sheet = None
        self.__max_rows = 65536
        self.__sheet_index = 0
        self.__row = 0
        self.__add_sheet()

    def __add_sheet(self):
        if self.__sheet_index == 0:
            self.__w_sheet = self.__workbook.add_sheet(self.__sheet_name, cell_overwrite_ok=True)
        else:
            self.__w_sheet = self.__workbook.add_sheet(self.__sheet_name + '_' + str(self.__sheet_index), cell_overwrite_ok=True)

        for i, title in enumerate(self.__headers):
            self.__w_sheet.write(0, i, title)
        self.__row = self.__row if self.__headers == [] else self.__row + 1

    def write(self, values=None):
        print 'row:', self.__row, '| sheet:', self.__sheet_index
        if self.__row == self.__max_rows:
            self.__row -= self.__max_rows
            self.__sheet_index += 1
            self.__add_sheet()

        values = values if values is not None else []
        for col, item in enumerate(values):
            try:
                self.__w_sheet.write(self.__row, col, item)
            except Exception as e:
                print 'write excel error:', e

        self.__row = self.__row if not values else self.__row + 1
        if self.__row % self.__flush == 0:
            self.__w_sheet.flush_row_data()

    def save(self):
        self.__workbook.save(self.__save_path)


class XlsxReader(object):
    """
        read data generate dictionary from excel, only handle a excel file at one time
    """
    def __init__(self, excel_name, sheet_index=0, sheet_name='sheet1'):
        self.__excel_name = excel_name
        self.__sheet_index = sheet_index
        self.__sheet_name = sheet_name
        self.__open_book = xlrd.open_workbook(self.__excel_name)

    def types(self, _type, var):
        if not var and _type is None:
            return None
        if _type == int and isinstance(var, float):
            return _type(var)
        if _type == long and isinstance(var, float):
            return _type(var)
        if _type == str and isinstance(var, float):
            return _type(var) if var - long(var) else _type(long(var))
        if _type == datetime:
            return self.iso_datetime(var)
        return var

    def iso_datetime(self, t):
        """
            t (time) must date string, eg:'2014-08-10 00:00:00'
            return datetime.datetime value
        """
        if t.count('-') < 2:
            raise ValueError('%s is bad format' % t)
        return datetime.strptime(t + ' 00:00:00', '%Y-%m-%d %H:%M:%S')

    def sheet_name(self):
        return self.__open_book.sheet_names()[self.__sheet_index]

    def collection(self, **kwargs):
        """
           excel_name first line must title, not data. We start write data from second line in sheet table.
           field 'valid: 1', eg: {'valid': int}
           field 'org.id: 12030', 'org.en: 1003', eg: {'org.id': str, 'org.en': long}
        """
        if not os.path.exists(self.__excel_name):
            raise WindowsError("Don't exist: [%s]" % self.__excel_name)

        data = self.__open_book.sheet_by_index(self.__sheet_index)
        keys, rows = [str(k).strip() for k in data.row_values(0)], data.nrows

        for row in range(1, rows):
            collect = dict()
            for i, item in enumerate(data.row_values(row)):
                try:
                    if keys[i] in kwargs:
                        item = self.types(kwargs[keys[i]], item)
                    collect[keys[i]] = item
                except Exception as e:
                    collect[keys[i]] = None
                    print 'Get excel datas error:', e

            # handle with level two
            v = list(set([k.split('.')[0] for k in collect if len(k.split('.')) == 2]))
            for _v in v:
                v_d, v_l = dict(), list()
                for k in collect.keys():
                    if _v == k.split('.')[0] and not k[k.find('.') + 1:].isdigit():
                        v_d[k.split('.')[1]] = collect[k]
                        collect.pop(k)

                    if _v == k.split('.')[0] and k[k.find('.') + 1:].isdigit():
                        v_l.append(collect[k])
                        collect.pop(k)
                d = v_d if not v_l else v_l
                collect[_v] = d

            # handle with level three
            q = list(set([k[:k.rfind('.')] for k in collect if len(k.split('.')) == 3]))
            ct = list(set([k.split('.')[0] for k in q]))
            for _ct in ct:
                p_l = list()
                for _q in q:
                    p_d = dict()
                    for k in collect.keys():
                        if _ct in _q and _q == k[:k.rfind('.')]:
                            p_d[k.split('.')[-1]] = collect[k]
                            collect.pop(k)
                    if p_d:
                        p_l.append(p_d)
                collect[_ct] = p_l
            yield collect


if __name__ == '__main__':
    open_book = XlsxReader(r'E:\project\autumn\mongodb\data', sheet_index=1)
    getor = open_book.collection()
    for dic in getor:
        print dic
