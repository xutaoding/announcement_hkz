#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
from StringIO import StringIO
import requests
from qiniu import conf
from qiniu import io
from qiniu import rs
from eggs.utils.conf import bucket_name
from eggs.utils.conf import access_key, secret_key


class UpLoad(object):
    def __init__(self):
        conf.ACCESS_KEY = access_key
        conf.SECRET_KEY = secret_key

    def put_file(self, key=None, local_file=None, rename=None):
        """
            put local file to qiniu. If key is None, the server will generate one.
            Note: local_file if local file path.
        """
        if local_file is None:
            raise NameError('upload file to qiniu error!')

        policy = rs.PutPolicy(bucket_name)
        policy.saveKey = rename
        up_token = policy.token()

        ret, err = io.put_file(up_token, key, local_file)
        if err is not None:
            sys.stderr.write('error: %s ' % err)
            return ret['key']
        else:
            # print 'upload local: %s file ok.' % local_file
            pass
        return ret

    def put(self, img_url, key=None, rename=None):
        """
            put your data to qiniu. If key is None, the server will generate one.
            Note: img_url is web url.
        """
        r = None
        if img_url is None:
            raise ValueError('upload img path to qiniu error!')

        for i in range(5):
            r = requests.get(img_url, timeout=10.0)
            if r is not None:
                break
        policy = rs.PutPolicy(bucket_name)
        policy.saveKey = rename
        up_token = policy.token()

        ret, err = io.put(up_token, key, StringIO(r.content))
        if err is not None:
            sys.stderr.write('error: %s ' % err)
            return ret['key']
        else:
            # print 'upload img ok.'
            pass
        return ret

if __name__ == '__main__':
    import time
    start = time.time()
    # local_files = [r'D:\image\1999160\2111.jpg', r'D:\image\1999160\4470.jpg', r'D:\image\1999160\6479.jpg']
    # for local in local_files:
    #     Image().put_file(local_file=local)
    img = 'http://photo.sac.net.cn/sacmp/images/20080102/registrationRpInfo/136386365484786545.jpg'
    UpLoad().put(img, rename='abc')
    print time.time() - start