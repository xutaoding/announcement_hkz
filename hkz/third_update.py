#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import re
import datetime
import json
from pyquery import PyQuery
from . import BaseDownloadHtml
from eggs.db.mongodb import Mongodb

from .config import post_params
from .tools import get_secu, post_dict


class ThirdUpdate(BaseDownloadHtml):
    def __init__(self):
        self.__post_datas = None
        self.__b_url = 'http://www.hkexnews.hk/listedco/listconews/advancedsearch/search_active_main_c.aspx'

    def web_form_view_state(self, document=None, start=None):
        fy, fm, fd = str(datetime.date.today()).split('-')
        if start is not None and not document:
            raise ValueError('`document` error.')

        if start is None and document is None:
            document = PyQuery(self.get_html(self.__b_url)[0])
        view_state_ = document('#__VIEWSTATE').attr('value')
        return post_params(view_state_, fy=fy, fm=fm, fd=fd, start=start)
        # return post_params(view_state_, fy='2015', fm='05', fd='06', start=start, upt='yes')

    def pages_num(self, docum):
        pages_pat = re.compile(r'(\d+)', re.S)
        pages_ls = pages_pat.findall(docum('#ctl00_lblDisplay').text())
        if pages_ls:
            pages, mod = divmod(int(pages_ls[-1]), 20)
            return pages if mod == 0 else pages + 1
        return 0

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

    def extract_html(self, document):
        if self.__post_datas is None:
            self.__post_datas = []

        for ids in range(3, 23):
            _ids = '0' + str(ids) if len(str(ids)) == 1 else str(ids)
            date_pub = document('#ctl00_gvMain_ctl%s_lbDateTime' % _ids).text()
            com_code = document('#ctl00_gvMain_ctl%s_lbStockCode' % _ids).text()
            cat_text = document('#ctl00_gvMain_ctl%s_lbShortText' % _ids).text()
            doc_title = document('#ctl00_gvMain_ctl%s_hlTitle' % _ids).text()
            post_file = document('#ctl00_gvMain_ctl%s_hlTitle' % _ids).attr('href')

            if not date_pub.strip():
                break

            # print date_pub, '|', cat_text, '|', doc_title, '|', com_code.strip().split()
            # print post_file, '\n\n'
            dmy, hm = date_pub.strip().split()
            dt = datetime.datetime.strptime('-'.join(reversed(dmy.split('/'))) + ' %s:00' % hm, '%Y-%m-%d %H:%M:%S')
            self.__post_datas.append(([code for code in com_code.strip().split() if code], dt,
                                      self.category(cat_text.replace('\n', '')), doc_title.replace('\n', ''),
                                      'http://www.hkexnews.hk' + post_file, cat_text.replace('\n', '')))
        return self.web_form_view_state(document, start=1)

    def main(self):
        st_data = self.web_form_view_state()
        html = self.get_html(self.__b_url, st_data, method='POST', encoding=True)[0]
        document = PyQuery(unicode(html, 'utf-8'))

        for page in range(1, self.pages_num(document) + 1):
            eve_data = self.extract_html(document)
            go_html = self.get_html(self.__b_url, eve_data, method='POST', encoding=True)[0]
            document = PyQuery(unicode(go_html, 'utf-8'))
            print 'page: [%d] is done!' % page
        return self.__post_datas


def third_update():
    coll_in = Mongodb('192.168.250.208', 27017, 'news', 'announcement_hk_chz')
    coll_cat = Mongodb('192.168.250.200', 27017, 'ada', 'dict_announce_catalog_hk')
    coll_secu = Mongodb('192.168.250.200', 27017, 'ada', 'base_stock')
    kt = 0
    cdctuo = ThirdUpdate().main()
    cd_dt_cat_tit_url_ori = cdctuo if cdctuo else []
    for codes, dt, cat, title, url, cat_origin in cd_dt_cat_tit_url_ori:
        kt += 1
        for code in codes:
            secu = get_secu(code, coll_secu)
            if secu and not coll_in.get({'sid': url, 'secu.0.cd': secu[0]['cd']}, {'title': 1}):
                print 'kt:', kt, '|', code, '|',  dt, '|', url, '\n|', title

                try:
                    hk_data = post_dict(secu, dt, cat, title, url, cat_origin, coll_cat)
                    coll_in.insert(hk_data)
                except Exception as e:
                    print 'Error:', e.message

                # 创建索引
                inds_mon = coll_in.get({'sid': url})
                ind_url = "http://192.168.250.205:17081/indexer/services/indexes/delta.json?" \
                          "indexer=announce_hkz&taskids="
                if inds_mon:
                    jdata = BaseDownloadHtml().get_html(ind_url + str(inds_mon['_id']))[0]
                    if json.loads(jdata)['code'] == 200:
                        print '\tcreate index is ok!\n\n'
    coll_in.disconnect()
    coll_cat.disconnect()
    coll_secu.disconnect()

