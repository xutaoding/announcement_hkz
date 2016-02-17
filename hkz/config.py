#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import date


def post_params(view_state, code='', fy='1999', fm='04', fd='01', start=None, upt='no'):
    if upt == 'no':
        year, month, day = str(date.today()).split('-')
    else:
        year, month, day = fy, fm, fd
    txt_today = str(date.today()).replace('-', '')
    start_params = {
        '__VIEWSTATE': view_state,
        '__VIEWSTATEENCRYPTED': '',
        'ctl00$txt_today': txt_today,
        'ctl00$hfStatus': 'ACM',
        'ctl00$hfAlert': '',
        'ctl00$txt_stock_code': code,
        'ctl00$txt_stock_name': '',
        'ctl00$rdo_SelectDocType': 'rbAll',
        'ctl00$sel_tier_1': '-2',
        'ctl00$sel_DocTypePrior2006': '-1',
        'ctl00$sel_tier_2_group': '-2',
        'ctl00$sel_tier_2': '-2',
        'ctl00$ddlTierTwo': '59,1,7',
        'ctl00$ddlTierTwoGroup': '19.5',
        'ctl00$txtKeyWord': '',
        'ctl00$rdo_SelectDateOfRelease': 'rbManualRange',
        'ctl00$sel_DateOfReleaseFrom_d': fd,
        'ctl00$sel_DateOfReleaseFrom_m': fm,
        'ctl00$sel_DateOfReleaseFrom_y': fy,
        'ctl00$sel_DateOfReleaseTo_d': day,
        'ctl00$sel_DateOfReleaseTo_m': month,
        'ctl00$sel_DateOfReleaseTo_y': year,
        'ctl00$sel_defaultDateRange': 'SevenDays',
        'ctl00$rdo_SelectSortBy': 'rbDateTime'
    }

    params_next = {
        """__VIEWSTATE""": view_state,
        """__VIEWSTATEENCRYPTED""": '',
        """ctl00$btnNext2.x""": '34',
        """ctl00$btnNext2.y""": '11',
        # """ctl00$gvMain$ctl01$btnNext.x""": '34',
        # """ctl00$gvMain$ctl01$btnNext.y""": '11',
    }
    return start_params if start is None else params_next


# 这是需要补抓的公司代码和时间规则
# code: must string eg: len("00000") == 5, or is None, then crawl all items at date.
# date: int or string, eg: "0000-00-00", or is None, then crawl all items until today.

codes_date = [('00139', '2016-02-12'), ]
