from ttypes import Strategy, Storage, SObject
from PassageService import Client

from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport, TSSLSocket

"""
    Java code example:

    PassageClient passageClient = new PassageClient();
    Strategy strategy = new Strategy();
    strategy.setBucketName("cn.com.chinascope.dfs");
    strategy.setSType(Storage.S3CN);
    ListKeysAction action = new ListKeysAction();
    action.setKey("/announce/cn/20110131/");
    action.setStrategy(strategy);
    Object list = passageClient.perform(action);
    System.out.println("list = " + list);
"""
# host = '192.168.250.206' # 206 server
host = '54.223.53.153'
port = 8888

socket = TSocket.TSocket(host, port)
# socket = TSSLSocket.TSSLSocket(host, port, validate=False)
transport = TTransport.TBufferedTransport(socket)
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = Client(protocol)
transport.open()

s3_strategy = Strategy(Storage.S3CN, 'cn.com.chinascope.dfs')

#  # send
# with open('D:/temp/data/aaa.txt', 'rb') as fp:
#     data = fp.read()
#
# client.putObject(s3_strategy, SObject(key='/announce/hkz/20161215/1200.pdf', data=data))

# list
ll = client.listKeys(s3_strategy, '/announce/hkz/20151214/')
print ll

# dd = client.getObject(s3_strategy, '/announce/hkz/20151214/a255aae599d62c3362c803492f4383c6_eBd9047mLc.pdf')
# print dd
# print dd.data

transport.close()




