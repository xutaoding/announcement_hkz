# -*- coding: UTF-8 -*-

import os
import os.path
import urllib
import urllib2
import requests
import socket
import time
import StringIO
import chardet
#from PIL import Image

from eggs.utils.conf import confs, proxy_ips


class BaseDownloadHtml(object):
    def __init__(self):
        self.encoding = None

    def image_down(self, img_path, img_url, img_name=None):
        now, fmt, r = time.time(), img_url[img_url.rfind('.'):], None
        if not os.path.exists(img_path):
            os.makedirs(img_path)
        img_name = time.strftime('%Y%m%d%H%M%S', time.localtime(now)) + fmt if img_name is None else img_name + fmt

        try:
            # img_path + img_name is store path and filename
            # @(1) request module get(...)
            for i in range(5):
                r = requests.get(img_url, timeout=10.0)
                if r is not None:
                    break
            Image.open(StringIO.StringIO(r.content)).convert('RGB').save(img_path + img_name)

            # @(2) image_name, mime = urllib.urlretrieve(img_url, img_path + img_name),
            # but sometimes have problems to big amount crawler
            # @(2) return image_name
        except Exception, e:
            print 'down image error:', e
        return img_path + img_name

    def get_html(self, url, data=None, method='GET', headers=None, encoding=False):

        """you can use many methods to crawl web source, here use requests."""
        r = self.request_load(url, data, method, headers)
        if r is not None:
            if not encoding:
                return r.content, r
            else:
                # return r.content, r
                return self.to_utf8(r.content), r
        return 'None', None

    def request_load(self, url, params=None, method='GET', headers=None):
        params = {} if params is None else params
        headers = {} if headers is None else headers
        for _ in range(0, 10):
            try:
                if method.lower() == 'get':
                    return requests.get(url, params=params, headers=headers, timeout=30.0)
                if method.lower() == 'post':
                    return requests.post(url, data=params, headers=headers, timeout=30.0)
            except Exception as e:
                print 'request_load `%s` method error:' % method.lower(), e

    def downloader_browser(self, url, data=None, headers=None, encoding=False):
        """
            Limited browser login, be disguised as a browser.Because some sites antipathy crawler visit,
            so the crawler will reject the request, then we need to pretend to be the browser.
            sp: if need, can sleep(3) after crawl web,general no need
            Note:if total 8 times download fail,then recognize download fail
        """
        if isinstance(data, dict):
            data = urllib.urlencode(data)

        headers = {} if headers is None else headers
        for i in range(1, 9):
            req = urllib2.Request(url) if not data else urllib2.Request(url, data, headers)
            req.add_header('User-Agent', '	Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0')
            try:
                response = urllib2.urlopen(req, timeout=30.0)
                feed_data = response.read()
                response.close()
                return self.to_utf8(feed_data) if encoding else feed_data
            except Exception, e:
                print 'Web open error', i, 'times:', e
                time.sleep(3.0)
        return 'None'

    def downloader_proxy(self, url, _post=None, encoding=False, _proxy_ips=None):
        """
            If IP is blocked, or the number of visits is limited, use a proxy server more useful,
            agent IP can grab yourself some web proxy data.
        """
        _proxy_ips = _proxy_ips if _proxy_ips else proxy_ips
        _data = urllib.urlencode(_post) if _post else _post
        for proxy_ip in _proxy_ips:
            proxy_sopport = urllib2.ProxyHandler({'http': proxy_ip})
            opener = urllib2.build_opener(proxy_sopport, urllib2.HTTPHandler)
            try:
                urllib2.install_opener(opener)
                fd = urllib2.urlopen(url, data=_data, timeout=30.0)
                html = fd.read()
                fd.close()
                return self.to_utf8(html) if encoding else html
            except Exception, e:
                print 'proxy error:', e
        return 'None'

    def to_utf8(self, string):
        """
        Auto convert encodings to utf8, because For the encoding of different site content is different,
        must be turned into UTF-8 code
        return: return value is a dictionary(have a key is 'encoding')
        note:
            1、`decode('GB2312')` is messy code, due to `GB2312` character set less than `gb18030`
            2、`Big5` is Traditional Chinese
        """
        charset = chardet.detect(string)['encoding']
        if charset is None:
            return string
        elif charset != 'utf-8' and charset == 'GB2312':
            charset = 'gb18030'
        elif charset.lower()[:4] == 'big5' or charset.lower() == 'windows-1252':
            charset = 'big5hkscs'
        try:
            return string.decode(charset).encode('utf-8')
        except Exception as e:
            print 'chardet error:', e


if __name__ == '__main__':
    from pyquery import PyQuery
    # g_url = 'https://mdskip.taobao.com/core/initItemDetail.htm?isApparel=true&cartEnable=true&isSecKill=false&tryBeforeBuy=false&isForbidBuyItem=false&isUseInventoryCenter=false&addressLevel=2&showShopProm=false&offlineShop=false&queryMemberRight=true&sellerPreview=false&service3C=false&isRegionLevel=false&tmallBuySupport=true&household=false&cachedTimestamp=1441870902037&isAreaSell=false&progressiveSupport=true&itemId=36424250160&callback=setMdskip&timestamp=1441871169981&areaId=810000&cat_id=50025135'
    g_url = 'http://finance.sina.com.cn/chanjing/cyxw/20140615/081019415534.shtml'
    headers = {'referer': 'https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.1.Fn7NlQ&id=36424250160&skuId=77598565279&areaId=810000&cat_id=50025135&rn=dd660f9a7ceea4e4235a8bfd76599d0b&user_id=408107205&is_b=1'}

    # html = BaseDownloadHtml().get_html(g_url)[0]
    html = BaseDownloadHtml().downloader_browser(g_url)
    print html
    # document = PyQuery(html)
    # print document('#J_AttrUL').text()

