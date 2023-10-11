#!/usr/bin/python
import random

from mininet.topo import Topo
from mininet.node import OVSSwitch


class MyTopology(Topo):
    bandwidth = 1000
    # Single switch connected to n hosts

    def __init__(self, *args, **params):
        # Initialize topology and default option
        super().__init__(self, *args, **params)

        # create 7 switches with 1 host each
        for i in range(8):
            s = OVSSwitch(name=f"s{i+1}", protocols='OpenFlow13')
            self.addSwitch(name=s.name, cls=s.__class__, protocols=s.protocols)
            self.addHost(name=f"h{i+1}", ip=f"10.0.0.{i+1}/24",
                         defaultRoute=f"via 10.0.0.{i+1}")
            self.addLink(s.name, f"h{i+1}", bw=self.bandwidth)

        self.add_link("s1", "s3", weight=random.randint(1, 10))
        self.add_link("s1", "s8", weight=random.randint(1, 10))

        self.add_link("s3", "s8", weight=random.randint(1, 10))
        self.add_link("s3", "s6", weight=random.randint(1, 10))
        self.add_link("s3", "s4", weight=random.randint(1, 10))

        self.add_link("s8", "s6", weight=random.randint(1, 10))
        self.add_link("s8", "s7", weight=random.randint(1, 10))

        self.add_link("s6", "s5", weight=random.randint(1, 10))

        self.add_link("s5", "s7", weight=random.randint(1, 10))
        self.add_link("s5", "s2", weight=random.randint(1, 10))
        self.add_link("s5", "s4", weight=random.randint(1, 10))

        self.add_link("s2", "s4", weight=random.randint(1, 10))
        self.add_link("s2", "s7", weight=random.randint(1, 10))

        self.add_link("s4", "s7", weight=random.randint(1, 10))

    def add_link(self, s1: str, s2: str, weight: int):
        self.addLink(s1, s2, bw=self.bandwidth, weight=weight)