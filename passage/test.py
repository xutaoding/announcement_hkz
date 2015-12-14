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
host = '192.168.250.206'
port = 8888

socket = TSocket.TSocket(host, port)
# socket = TSSLSocket.TSSLSocket(host, port, validate=False)
transport = TTransport.TBufferedTransport(socket)
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = Client(protocol)
transport.open()

strategy = Strategy(Storage.HAFS, "/mfs/d01/")
sobject = SObject('announce/hkcn/2015/12/14/11ccce6a3c40242f8437061314b9bff4_SAU1542fmo.pdf')


ff = client.getObject(strategy, 'announce/hkcn/2015/12/14/11ccce6a3c40242f8437061314b9bff4_SAU1542fmo.pdf')
print ff.data

transport.close()




