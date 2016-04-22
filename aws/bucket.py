import os
import ssl
import logging
from ConfigParser import ConfigParser
import boto
from boto.s3 import connection

# from ....eggs import logger_error
logger_error = logging.getLogger(__name__)
logger_error.setLevel(logging.INFO)


class Config(ConfigParser):
    default_section = 'default'

    def __init__(self, config_path=None):
        layer = 1
        if config_path is None:
            default_path = os.path.dirname(__file__)
            for _ in range(layer):
                default_path = os.path.dirname(default_path)
            config_path = os.path.join(default_path, 'aws', 's3').replace('\\', '/')
        print config_path

        ConfigParser.__init__(self)
        self.read(config_path)

    @property
    def access_key(self):
        return self.get(self.default_section, 'aws_access_key_id')

    @property
    def secret_key(self):
        return self.get(self.default_section, 'aws_secret_access_key')

    @property
    def host(self):
        return self.get(self.default_section, 'host')

    @property
    def bucket_name(self):
        return self.get(self.default_section, 'bucket_name')


class Bucket(object):
    config_class = Config

    def __init__(self):
        self.config = self.config_class()
        self.bucket_name = self.config.bucket_name

        self.conn = boto.connect_s3(
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                host=self.config.host,
                calling_format=boto.s3.connection.OrdinaryCallingFormat(),
        )

    def all_buckets_name(self):
        return [bucket.name for bucket in self.conn.get_all_buckets()]

    def lookup(self):
        return self.conn.lookup(self.bucket_name)

    def get_buck(self):
        return self.conn.get_bucket(self.bucket_name)

    def create_bucket(self):
        """ Temporary don't have to implement """
        pass

    def delete_bucket(self):
        """ Temporary don't have to implement """
        pass

    def put(self, key_name, filename):
        """
        :param key_name: key name of Amazon S3
        :param filename: Store local directory filename path
        """
        try:
            bucket = self.get_buck()
            key = bucket.new_key(key_name)
            key.set_contents_from_filename(filename)
        except Exception as e:
            logger_error.info('Put file to S3 Error: [{}]'.format(e))

    def get(self, key_name, filename=None):
        """
        :param key_name: key name of Amazon S3
        :param filename: Store local directory filename path
        :return `boto.s3.key.Key` class instance
        """
        try:
            bucket = self.get_buck()
            key = bucket.get_key(key_name)

            if key and filename is not None:
                key.get_contents_to_filename(filename)

            return key
        except ssl.SSLError as e:
            logger_error.info('Get file from S3 Error: [{}]'.format(e))

    def list_keys(self, prefix=''):
        """
        List key from S3 bucket
        :param prefix: key part
        """
        try:
            bucket = self.get_buck()
            lister = bucket.list(prefix)

            for key in lister:
                yield key.name
        except ssl.SSLError:
            yield

    def delete_key(self):
        pass

    def close(self):
        return self.conn.close()

if __name__ == '__main__':
    s3 = Bucket()
    # print s3.all_buckets_name()
    # s3.put(
    #         'csf_news/20151222/20151222165800_EXZbSmio079184.txt',
    #         r'D:\temp\csf_news\20151222\20151222165800_EXZbSmio079184.txt'
    # )
    # for k, _key in enumerate(s3.list_keys('data/news/csf_news/20160407/'), 1):
    for k, _key in enumerate(s3.list_keys('announce/hkz/20160411/'), 1):
        print 's3:', _key
    # kkey = s3.get('csf_news/20151222/20151222165700_tWIyqUEP65178.txt', r'D:\temp\data\ssss3.txt')
    # print kkey, type(kkey)