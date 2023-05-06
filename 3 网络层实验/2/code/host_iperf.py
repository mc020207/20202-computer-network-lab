from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI

from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSController
import time
import threading

class labtopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        Host1 = self.addHost("H1",ip_address="10.0.0.1",mac="00:00:00:00:ff:01")
        Host2 = self.addHost("H2",ip_address="10.0.0.2",mac="00:00:00:00:ff:02")
        Host3 = self.addHost("H3",ip_address="10.0.0.3",mac="00:00:00:00:ff:03")
        Host4 = self.addHost("H4",ip_address="10.0.0.4",mac="00:00:00:00:ff:04")
        Switch1 = self.addSwitch("S1")
        Switch2 = self.addSwitch("S2")

        self.addLink(Host1,Switch1,bw=10,delay="2ms")
        self.addLink(Host2,Switch1,bw=20,delay="10ms")
        self.addLink(Host3,Switch2,bw=10,delay="2ms")
        self.addLink(Host4,Switch2,bw=20,delay="10ms")
        self.addLink(Switch1,Switch2,bw=20,delay="2ms",loss=10)

# topos = {'labtopo':(lambda:labtopo())}
def perfTest():
    topo = labtopo()
    net = Mininet( topo=topo, link=TCLink, controller=OVSController)
    net.start()
    h1,h2,h3,h4 = net.get( 'H1','H2','H3','H4')
    net.iperf( (h1, h2))
    net.iperf( (h2, h4))
    net.iperf( (h3, h4))
    net.stop()

def test1(h1,h3):
    result3 = h3.cmd('iperf -s -p 5001 & ')
    print(result3)
    result1 = h1.cmd('iperf -c 10.0.0.3 -p 5001 -t 20 -i 0.5')
    print(result1)
    # print(h1,h3)

def test2(h2,h4):
    time.sleep(10)
    result4 = h4.cmd('iperf -s -p 5002 & ')
    print(result4)
    result2 = h2.cmd('iperf -c 10.0.0.4 -p 5002 -t 20 -i 0.5 ')
    print(result2)

def perfTest2():
    "Create network and run simple performance test"
    topo = labtopo()
    net = Mininet( topo=topo, link=TCLink, controller=OVSController)
    net.start()
    print( "Dumping host connections" )
    dumpNodeConnections( net.hosts )

    print( "Testing bandwidth between h1 and h4" )
    h1,h2,h3,h4 = net.get( 'H1','H2','H3','H4')
    # result3 = h3.cmd('iperf -s -p 5001 & ')
    # print(result3)
    # result1 = h1.cmd('iperf -c 10.0.0.3 -p 5001 -t 20 -i 0.5')
    # print(result1)
    # result4 = h4.cmd('iperf -s -p 5001 & ')
    # print(result4)
    # result2 = h2.cmd('iperf -c 10.0.0.4 -p 5001 -t 20 -i 0.5 ')
    # print(result2)
    # test1(h1,h3)
    thread1=threading.Thread(group=None,target=test1,args=(h1,h3))
    thread2=threading.Thread(group=None,target=test2,args=(h2,h4))
    thread1.start()
    thread2.start()
    time.sleep(35)
    net.stop()
if __name__ == '__main__':
    setLogLevel( 'info' )
    # perfTest()
    perfTest2()
