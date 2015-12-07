#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import xlsxwriter


class XlsxWriter(object):
    """
        this class can write massive data to excel, no like xlwt only write 65536 row at most.
        Note:
            (1): if write data is str, then need str convert unicode, otherwise fail.
            (2): fit one sheet in excel.
    """
    def __init__(self, save_path, sheet_name=None, headers=None):
        self.__sheet_name = sheet_name if sheet_name is not None else 'Sheet'
        self.__headers = headers if headers is not None else []
        self.__workbook = xlsxwriter.Workbook(save_path)
        self.__worksheet = None
        self.__sheet_names = None
        self.__sheet_index = 0
        self.__max_row = 1048576
        self.__rows = 0
        self.__add_sheet()

    def __add_sheet(self):
        self.__worksheet = self.__workbook.add_worksheet(self.__sheet_name + str(self.__sheet_index))

        for i, header in enumerate(self.__headers):
            self.__worksheet.write(0, i, header)
        self.__rows = self.__rows if self.__headers == [] else self.__rows + 1

    def write(self, values=None):
        if self.__rows == self.__max_row:
            self.__rows -= self.__max_row
            self.__sheet_index += 1
            self.__add_sheet()

        values = values if values is not None else []
        for col, value in enumerate(values):
            try:
                self.__worksheet.write(self.__rows, col, value)
            except Exception as e:
                print 'xlsxwriter write error:', e
        self.__rows = self.__rows if not values else self.__rows + 1

    def close(self):
        self.__workbook.close()


if __name__ == '__main__':
    # workbook = XlsxWriter(r'D:\project\autumn\eggs\utils\xw.xlsx', sheet_name='0002')
    # for k in xrange(1):
    #     workbook.write([u'002249海通证券 2014-08-26 佩特来并表推动业绩快速增长，电动车总成将成发展亮点'])
    #     print k
    # workbook.close()
    workbook = xlsxwriter.Workbook('filename.xlsx')
    # worksheet = workbook.add_worksheet()
    # for i in xrange(1000000):
    #     worksheet.write(i, 0, i)
    #     print i
    # worksheet.r
    print workbook.sheet_name
    # print worksheet.row_sizes
    workbook.close()