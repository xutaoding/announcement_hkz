#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import re
import json
import datetime
from time import sleep
from pyquery import PyQuery
from . import BaseDownloadHtml
from eggs.db.mongodb import Mongodb
from .tools import get_secu, post_dict
from .config import post_params, codes_date


class PoskUpdate(BaseDownloadHtml):
    def __init__(self, code, upt=None):
        self.__code = code or ''
        self.__pages = None
        self.__post_datas = None
        self.__pages_pat = re.compile(r'(\d+)', re.S)
        self.__upt = upt if upt is not None else upt
        self.__base_url = "http://www.hkexnews.hk/listedco/listconews/advancedsearch/search_active_main_c.aspx"

    def web_form_view_state(self, document, start=None):
        view_state_ = document('#__VIEWSTATE').attr('value')
        if self.__upt is None:
            return post_params(view_state_, self.__code, start=start)
        fy, fm, fd = self.__upt.split('-')
        return post_params(view_state_, self.__code, fy=fy, fm=fm, fd=fd, start=start, upt='yes')

    def __pages_num(self, docum):
        pages_text = docum('#ctl00_lblDisplay').text()
        pages_ls = self.__pages_pat.findall(pages_text)
        if pages_ls:
            print 'total items:', pages_ls[-1]
            expression = int(pages_ls[-1]) % 20 == 0
            self.__pages = int(pages_ls[-1]) / 20 if expression else int(pages_ls[-1]) / 20 + 1
        else:
            self.__pages = 0

    def category(self, cat_str):
        """"
            ## (修改後標題) 公告及通告 - [不尋常價格 / 成交量變動 - 附帶意見]
            #   print 'cat_str:', cat_str, type(cat_str)
        """
        index = cat_str.rfind(' - [')
        first = [[cat_str[:index].split()[-1]]] if index != -1 else [[cat_str.split()[-1]]]
        if '[' in cat_str and '...' in cat_str:
            return first + [item.strip() for item in cat_str[cat_str.find('[') + len('['):cat_str.rfind('...')].split(' / ')]
        if '[' in cat_str and ']' in cat_str:
            cat = cat_str[cat_str.find('[') + len('['):cat_str.rfind(']')]
            return first + [item.strip() for item in cat.split(' / ')]

        if '(' in cat_str:
            return [[re.compile(r'\(.*?\)(.*)').findall(cat_str)[0].strip()]]
        else:
            return [[cat_str]]

    def extract(self, form_data=None):
        """
            if only `self.get_html(... encoding=True)`, Does not solve the problem of gibberish,
            you should so:
                first: `self.get_html(... encoding=True)`,
                second: PyQuery(unicode(html, 'utf-8')),
            this can solve to extraction of traditional Chinese garbled.
        """
        if form_data is None:
            start_html = self.get_html(self.__base_url)[0]
            form_data = self.web_form_view_state(PyQuery(start_html))
        html = self.get_html(self.__base_url, data=form_data, method='POST', encoding=True)[0]
        document = PyQuery(unicode(html, 'utf-8'))

        if self.__pages is None:
            self.__pages_num(document)

        for ids in range(3, 23):
            _ids = '0' + str(ids) if len(str(ids)) == 1 else str(ids)
            date_pub = document('#ctl00_gvMain_ctl%s_lbDateTime' % _ids).text()
            com_code = document('#ctl00_gvMain_ctl%s_lbStockCode' % _ids).text()
            cat_text = document('#ctl00_gvMain_ctl%s_lbShortText' % _ids).text()
            doc_title = document('#ctl00_gvMain_ctl%s_hlTitle' % _ids).text()
            post_file = document('#ctl00_gvMain_ctl%s_hlTitle' % _ids).attr('href')
            if not date_pub:
                break

            # print date_pub, '|', cat_text, '|', doc_title
            # print post_file, '\n\n'
            dmy, hm = date_pub.split()
            cat_str = doc_title if not cat_text.strip() else cat_text
            dt = datetime.datetime.strptime('-'.join(reversed(dmy.split('/'))) + ' %s:00' % hm, '%Y-%m-%d %H:%M:%S')
            self.__post_datas.append(([code for code in com_code.strip().split() if code], dt, self.category(cat_str.replace('\n', '')), doc_title.replace('\n', ''),
                                      'http://www.hkexnews.hk' + post_file, cat_text.replace('\n', '')))
        return self.web_form_view_state(document, 1)

    def main(self):
        if self.__post_datas is None:
            self.__post_datas = []
        eve_data = self.extract()
        print 'page:[1] done!'

        for page in range(2, self.__pages + 1):
            form_data = self.extract(eve_data)
            eve_data = form_data
            print 'page:[%d] done!' % page
        return self.__post_datas


def validate(code_query, query):
    """
        query:(1)、`None`:       当前天（为None）
              (2)、`0000-00-00`: 之前的具体某一天
              (3)、`int`:        本日到当天到之前的几天的所有公告
    """
    if code_query and len(code_query) != 5:
        raise ValueError('`code_query` error')

    expression = re.compile(r'\d{4}-\d\d-\d\d')
    if query is not None and expression.search(query) is None:
        raise ValueError('`query` format is error!')


def update():
    coll_in = Mongodb('192.168.250.208', 27017, 'news', 'announcement_hk_chz')
    coll_cat = Mongodb('192.168.250.200', 27017, 'ada', 'dict_announce_catalog_hk')
    coll_secu = Mongodb('192.168.250.200', 27017, 'ada', 'base_stock')
    count = 0
    for code, query in codes_date:
        ktt = 0
        count += 1
        validate(code, query)
        print '[%s-->>%s,%s]' % (count, code, query), ':waiting few minutes......\n'
        dctu = PoskUpdate(code, query).main()  # codes, date, cat, title, url
        for codes, dt, cat, title, url, cat_origin in dctu:
            ktt += 1
            print '\t[%s ->> ktt:%s]' % (code, ktt), '|', codes, '|', dt, '|', title, '|', url

            for code_ in codes:
                secu = get_secu(code_, coll_secu)
                print 'secu:', secu
                if secu and not coll_in.get({'sid': url}, {'title': 1}):
                    try:
                        hk_data = post_dict(secu, dt, cat, title, url, cat_origin, coll_cat)
                        coll_in.insert(hk_data)
                    except Exception as e:
                        print '\t[%s] |%s|upload error: %s!' % (code_, dt, e.message)

                    inds_mon = coll_in.get({'sid': url}, {'title': 1})
                    ind_url = "http://192.168.250.205:17081/indexer/services/indexes/delta.json?" \
                              "indexer=announce_hkz&taskids="
                    if inds_mon:  # 创建索引
                        jdata = BaseDownloadHtml().get_html(ind_url + str(inds_mon['_id']))[0]
                        if json.loads(jdata)['code'] == 200:
                            print '\tcreate index is ok!\n\n'

                if ktt % 80 == 0:
                        sleep(2 * 60)

    coll_in.disconnect()
    coll_cat.disconnect()
    coll_secu.disconnect()


if __name__ == '__main__':
    update()
