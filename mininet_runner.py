from mininet.cli import CLI
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController

from topology_builder import MyTopology

REMOTE_CONTROLLER_IP = "10.0.2.2"
REMOTE_CONTROLLER_PORT = 6653


def simpleTest():
    # Create and test a simple network
    topo = MyTopology()

    net = Mininet(topo=topo,
                  controller=None,
                  autoStaticArp=True)
    net.addController("c0",
                      controller=RemoteController,
                      ip=REMOTE_CONTROLLER_IP,
                      port=REMOTE_CONTROLLER_PORT)
    net.start()
    print("Connections:")
    dumpNodeConnections(net.hosts)
    net.pingAll()
    net.stop()


def run():
    setLogLevel('info')
    simpleTest()
    topo = MyTopology()
    net = Mininet(topo=topo,
                  controller=None,
                  autoStaticArp=True)
    net.addController("c0",
                      controller=RemoteController,
                      ip=REMOTE_CONTROLLER_IP,
                      port=REMOTE_CONTROLLER_PORT)
    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    run()