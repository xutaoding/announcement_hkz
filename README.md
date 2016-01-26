说明:
======

执行文件：
--------
1：python run.py， 每日更新港股公告

2：python update.py, 补抓某已上市公司具体哪一天的公告， 具体补抓规则参考：./hkz/config.py中的codes_date变量设定规则。


部署：

1：远程仓储：git@gitlab.chinascope.net:scraper/announcement_hkz.git

2：抓取环境部署： 192.168.250.206：/home/xutaoding/announcement_hkz/

    （a）：使用 screen 相关命令，使程序后台运行
    
    （b）：可用 git 相关命令更新代码， 提交到仓储
    
    
其他注意点：

（1）：下载的港股公告上传 amazon S3 上， 相关函数已在：./hkz/tools.py: upload_s3 function




