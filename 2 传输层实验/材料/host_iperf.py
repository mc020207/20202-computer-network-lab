from mininet.topo import Topo
from mininet.net import Mininet

from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSController

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

#topos = {'labtopo':(lambda:labtopo())}
def perfTest():
    "Create network and run simple performance test"
    topo = labtopo()
    net = Mininet( topo=topo, link=TCLink, controller=OVSController)
    net.start()
    print( "Dumping host connections" )
    dumpNodeConnections( net.hosts )
    print( "Testing network connectivity" )
    #net.pingAll()
    print( "Testing bandwidth between h1 and h4" )
    h1, h4 = net.get( 'H1', 'H4' )
    a = "temp.out"
    h1.cmd('iperf -h > ',a)
    h1.cmdPrint(a)
    #net.iperf( (h1, h4) , seconds = 1)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    perfTest()
