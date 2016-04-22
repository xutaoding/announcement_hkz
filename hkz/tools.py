#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf8")

import re
import os
import os.path
import hashlib
import shutil
import time
import zipfile
from random import sample
from string import letters, digits
from datetime import date, datetime
from eggs.db.mongodb import Mongodb
from . import BaseDownloadHtml
from eggs.utils.up_server import UpServerWin

from passage.ttypes import Strategy, Storage, SObject
from passage.PassageService import Client
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport

from aws.bucket import Bucket

temp_store_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'files/').replace('\\', '/')


def pdf_size_pages(pdf_path):
    import pyPdf
    fd, pages = open(pdf_path, 'rb'), 1
    try:
        pdf = pyPdf.PdfFileReader(fd)
        pages = pdf.getNumPages()
    except:
        pass
    finally:
        fd.close()
    return pages


def md5(md5_str):
    if not isinstance(md5_str, basestring):
        raise ValueError('md5 must string!')
    m = hashlib.md5()
    m.update(md5_str)
    return m.hexdigest()


def download(path, name, ext, body):
    fp = open(path + name + ext, 'wb')

    try:
        fp.write(body)
    except Exception as e:
        print 'msg:', e
    finally:
        fp.close()


def upload_s3(local_path, name, ext):
    def aws_upload(key, file_data):
        try:
            socket = TSocket.TSocket(host, port)
            transport = TTransport.TBufferedTransport(socket)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            client = Client(protocol)
            transport.open()

            print 'fn:', key
            s3_strategy = Strategy(Storage.S3CN, bucket_name)
            client.putObject(s3_strategy, SObject(key=key, data=file_data))

            return key[1:] in client.listKeys(s3_strategy, os.path.dirname(key) + '/')
        except Exception as e:
            print 'Upload S3 Error:', e
        finally:
            transport.close()

    # host = '54.223.53.153'
    host = '122.144.134.96'
    port = 8888

    root_path = '/announce/hkz/'
    bucket_name = 'cn.com.chinascope.dfs'
    ymd = str(date.today()).replace('-', '')
    s3_path = os.path.join(root_path, ymd + '/').replace('\\', '/')
    s3_key = s3_path + name + ext

    with open(local_path + name + ext, 'rb') as fp:
        data = fp.read()

    for _recursion in range(10):
        if aws_upload(s3_key, data):
            break
        else:
            time.sleep(1.5)
    else:
        backup_upload_s3(local_path, name, ext)
    for filename in os.listdir(local_path):
        os.remove(local_path + filename)

    return s3_path


def backup_upload_s3(local_path, name, ext):
    root_path = 'announce/hkz/'
    ymd = str(date.today()).replace('-', '')
    s3_path = os.path.join(root_path, ymd + '/').replace('\\', '/')
    s3_key = s3_path + name + ext
    local_file = local_path + name + ext
    s3 = Bucket()
    s3.put(s3_key, local_file)


def compressed_zip(path, fn):
    ext = '.zip'
    files = os.listdir(path)
    temp_path = path + fn + ext
    z = zipfile.ZipFile(temp_path, 'w')

    try:
        for f in files:
            z.write(path + f, f)
            os.remove(path + f)
    finally:
        z.close()

    return ext


def document(url, ext, fn, temp_path):
    # below lines get path of store at Amazon S3
    multi_files_path = temp_path

    if not os.path.exists(multi_files_path):
        os.makedirs(multi_files_path)

    part_url, _ext = url[:url.rfind('/') + 1], '.' + ext

    if ext.lower() == 'htm':
        pat_href = re.compile(r'<a.*?href="(.*?)".*?>', re.S)
        body = BaseDownloadHtml().get_html(url, encoding=True)[0]
        hrefs = pat_href.findall(body)

        if not hrefs:
            download(multi_files_path, fn, _ext, body)
        elif len(hrefs) == 1:
            href, _ext = hrefs[0].strip().replace('./', ''), hrefs[0][hrefs[0].rfind('.'):]
            body = BaseDownloadHtml().get_html(part_url + href)[0]
            download(multi_files_path, fn, _ext, body)
        else:
            for href in hrefs:
                href, _ext, fne = href.strip().replace('./', ''), href[href.rfind('.'):], href[href.rfind('/') + 1:href.rfind('.')]
                body = BaseDownloadHtml().get_html(part_url + href)[0]
                download(multi_files_path, fne, _ext, body)
            _ext = compressed_zip(multi_files_path, fn)
    else:
        body = BaseDownloadHtml().get_html(url)[0]
        download(multi_files_path, fn, _ext, body)
    return multi_files_path + fn + _ext, _ext


def ssh_cmd(ip, passwd, cmd):
    import pexpect
    ret = -1
    ssh = pexpect.spawn('ssh root@%s "%s"' % (ip, cmd))
    try:
        i = ssh.expect(['password:', 'continue connecting(yes/no)?'], timeout=5)
        if i == 0:
            ssh.sendline(passwd)
        elif i == 1:
            ssh.sendline('yes\n')
            ssh.expect('password:')
            ssh.sendline(passwd)
        ssh.sendline(cmd)
        r = ssh.read()
        # print r
        ret = 0
    except pexpect.EOF:
        # print "EOF"
        ret = -1
    except pexpect.TIMEOUT:
        # print "TIMEOUT"
        ret = -2
    finally:
        ssh.close()
    return ret


def upload_linux_to_linux(pdf_name):
    import pexpect
    y_m_d = str(date.today()).split('-')
    store_path = 'announce/hkcn/' + '/'.join(y_m_d) + '/'
    # print 'scp /opt/announcement_otc/files/%s root@192.168.250.206:/mfs/d01/announce/%s' % (pdf_name, '/'.join(y_m_d))
    child = pexpect.spawn('scp /opt/announcement_hkz/files/%s root@192.168.250.206:/mfs/d01/announce/hkcn/%s' % (pdf_name, '/'.join(y_m_d)))
    try:
        ssh_cmd('192.168.250.206', 'chinascope', 'mkdir -p /mfs/d01/announce/hkcn/%s' % '/'.join(y_m_d))
        while 1:
            index = child.expect(["root@192.168.250.206's password:", pexpect.TIMEOUT])
            if index == 0:
                child.sendline('chinascope\n')
                break
            elif index == 1:
                pass
    except:
        print 'upload_linux_to_linux error'
    finally:
        child.interact()
        child.close()
        try:
            # print '/opt/announcement_otc/files/%s' % (pdf_name)
            os.remove('/opt/announcement_hkz/files/%s' % (pdf_name))
        except:
            pass
    return store_path


def upload_win_to_linux(upload_file_path, fn, path):
    us = UpServerWin('192.168.250.206', 'root', 'chinascope', 22)
    ct_path = str(date.today()).replace('-', '/') + '/'
    store_path = '/mfs/d01/announce/hkcn/' + ct_path
    try:
        us.exec_command('mkdir -p %s' % store_path)
        us.put(upload_file_path, store_path + fn)
    except Exception as e:
        print 'upload err | ', e
    finally:
        us.disconnect()
    shutil.rmtree(path)  # remove download file: files in path
    return '/announce/hkcn/' + ct_path


def stock_codes():
    coll, st_codes = Mongodb('localhost', 27017, 'ada', 'base_stock'), []
    for doc in coll.query().sort([('_id', -1)]):
        try:
            if '_HK_EQ' not in doc['code']:
                continue
            st_codes.append(doc['tick'])
        except Exception as e:
            pass
    coll.disconnect()
    return list(set(st_codes))


def get_secu(code, coll):
    secus = []
    try:
        for doc in coll.query({'tick': code}).sort([('_id', -1)]):
            secus.append({'cd': doc['code'], 'mkt': doc['mkt']['code'], 'org': doc['org']['id']})
    except Exception as e:
        print type(e)
    return secus


def get_cat(cat, query_date, coll):
    scok = []
    try:
        if query_date >= datetime.strptime('2007-06-25 00:00:00', '%Y-%m-%d %H:%M:%S'):
            # print 'latest'
            # 处理 cata 的头
            cat_head, head_ancestors = [], []
            for ch in cat[0]:
                # print 'head:', ch
                head = coll.get({'szh': ch, "mkttyp": "H"})
                cat_head.append(head['code'])
                head_ancestors.extend(head['ancestors'])
            if_flag = 0

            # 处理 cata 的分类
            for each in cat[1:]:
                # print 'each:', each
                cursors = coll.query({'szh': each, 'mkttyp': "H"})
                for cur in cursors:
                    flag = [head in cur['ancestors'] for head in cat_head]
                    if True not in flag:
                        continue
                    scok.append(cur['code'])
                    scok.extend(cur['ancestors'])
                    if_flag = 1
            if if_flag == 0:
                return list(set(cat_head + head_ancestors))
        else:
            # print 'before:', cat[0][0]
            for cursor in coll.query({'bdt': 'before'}).sort(([('prior', 1)])):
                if cursor['key'] in cat[0][0]:
                    data = coll.get({'code': cursor['code']})
                    scok.append(data['code'])
                    scok.extend(data['ancestors'])
                    break
            else:  # H201、H2 其余放公告
                return ['H2', 'H201']
    except:pass
    return list(set(scok))


def random_title(title):
    md_tit = md5(title + ''.join(sample(letters, 10) + sample(digits, 5) + sample(letters, 10)))
    return md_tit + '_' + ''.join(sample(letters, 3) + sample(digits, 4) + sample(letters, 3))


def post_dict(secu, pub_date, cat, title, docu_url, cat_origin, coll_cat):  # cat is list
    fn, ext = random_title(title), docu_url[docu_url.rfind('.') + 1:].strip()

    abspath, _ext = document(docu_url, ext, fn, temp_store_file_path)
    # print 'abspath:', abspath, '_ext:', _ext

    byts, pn = os.path.getsize(abspath), pdf_size_pages(abspath) if ext.lower() == 'pdf' else 1
    with open(abspath) as fd:
        _md5 = md5(fd.read(200))
   
    # if run program at 192.168.250.206, not need use `upload_win_to_linux` or `upload_linux_to_linux` method
    # store_path = upload_win_to_linux(abspath, fn + _ext, path=r'D:\pdf' + os.sep)
    # store_path = upload_linux_to_linux(fn + _ext)
    print 'Prepare upload S3'
    s3_path = upload_s3(temp_store_file_path, fn, _ext)
    print 'Upload to S3 is ok'

    files = {
        'fn': fn, 'ext': _ext[1:], 'bytes': byts, 'pn': pn,
        'md5': _md5, 'src': docu_url, 'url': s3_path
    }

    data = {
        'title': title, 'file': files, 'valid': '1', 'pdt': pub_date,
        'cat': get_cat(cat, pub_date, coll_cat), 'typ': None, 'secu': secu,
        'pid': '', 'pubid': '', 'upu': '000000', 'upt': datetime.now(), 'cru': '000000',
        'crt': datetime.now(), 'src': '', 'sid': docu_url, 'effect': None, 'stat': 2,
        'check': False, 'cat_origin': cat_origin
    }
    return data

