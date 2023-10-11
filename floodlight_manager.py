import requests
import pprint
from http import client
import random
import json
from typing import List, Dict
from dijkstra import Graph
import sys


class StaticEntryPusher(object):

    def __init__(self, server):
        self.server = server

    def get(self, data):
        ret = self.rest_call({}, "GET")
        return json.loads(ret[2])

    def set(self, data):
        ret = self.rest_call(data, "POST")
        return ret[0] == 200

    def remove(self, objtype, data):
        ret = self.rest_call(data, "DELETE")
        return ret[0] == 200

    def rest_call(self, data, action):
        path = "/wm/staticentrypusher/json"
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        body = json.dumps(data)
        conn = client.HTTPConnection(self.server, 8080)
        conn.request(action, path, body, headers)
        response = conn.getresponse()
        ret = (response.status, response.reason, response.read())
        print(ret)
        conn.close()
        return ret


# pusher = StaticEntryPusher("localhost")

# flow1 = {
#     "switch": "00:00:00:00:00:00:00:01",
#     "name": "flow_mod_1",
#     "cookie": "0",
#     "priority": "32768",
#     "in_port": "1",
#     "active": "true",
#     "actions": "output=flood"
# }

# flow2 = {
#     "switch": "00:00:00:00:00:00:00:01",
#     "name": "flow_mod_2",
#     "cookie": "0",
#     "priority": "32768",
#     "in_port": "2",
#     "active": "true",
#     "actions": "output=flood"
# }

# pusher.set(flow1)
# pusher.set(flow2)


def get_idx(switch_DPID: str) -> int:
    return int(switch_DPID.replace(":", "")) - 1


def get_name(idx: int) -> str:
    return f"00:00:00:00:00:00:00:{idx+1:02}"


class Manager:
    def __init__(self, src, dst):
        self.pusher = StaticEntryPusher("localhost")
        self.mod_count = 0
        self.controller_ip = "localhost"
        self.controller_port = 8080
        self.src = dst
        self.dst = dst
        self.topology = self.get_topo()
        self.set_weight()
        self.graph = self.parse_links_topology_to_2d_list_graph()
        path, self.cost = self.graph.dijkstra(src, dst)
        self.path = [get_name(idx) for idx in path]
        print(f"'path:{self.path}\ncost:{self.cost}")
        self.flows = []

    def get_switch_ports(self, src, dst):
        for link in self.topology:
            if link['src-switch'] == src and link['dst-switch'] == dst:
                return link['src-port'], link['dst-port']
            elif link['src-switch'] == dst and link['dst-switch'] == src:
                return link['dst-port'], link['src-port']
        else:
            return -1, -1

    def make_flows(self, path):
        self.mod_count += 1
        for idx in range(len(path)):
            src = path[idx]
            dst = path[min(idx + 1, len(path) - 1)]
            src_port, dst_port = self.get_switch_ports(src, dst)
            if src == path[0]:
                in_port = self.get_host_port(src)
                out_port = src_port
            elif src == path[-1]:
                out_port = self.get_host_port(src)
            else:
                out_port = src_port
            self.flows.append(
                {
                    "switch": f"{src}",
                    "name": f"flow_mod{self.mod_count}_{len(self.flows)}",
                    "cookie": "0",
                    "priority": "32768",
                    "in_port": f"{in_port}",
                    "active": "true",
                    "actions": f"output={out_port}"
                }
            )
            in_port = dst_port
        return self.flows

    def push_flows(self):
        for flow in self.flows:
            self.pusher.set(flow)
        print("flows pushed.")

    def get_topo(self) -> List[Dict]:
        print(f"GOING TO {self.get_topo}")
        url = f"http://{self.controller_ip}:{self.controller_port}/wm/topology/links/json"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to retrieve topology information.")
        link_data: list = response.json()
        return link_data

    def get_switches(self):
        print(f"GOING TO {self.get_switches}")
        url = f"http://{self.controller_ip}:{self.controller_port}/wm/core/controller/switches/json"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to retrieve switches information.")
        switches_data = response.json()
        return switches_data

    def get_switch(self, switch_DPID, port):
        print(f"GOING TO {self.get_switch} {switch_DPID} {port}")
        url = f"http://{self.controller_ip}:{self.controller_port}/wm/core/switch/{switch_DPID}/{port}/json"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to retrieve switch information.")
        switch_data = response.json()
        return switch_data

    def parse_links_topology_to_2d_list_graph(self) -> Graph:
        print(f"GOING TO {self.parse_links_topology_to_2d_list_graph}")
        vertices = set([link["dst-switch"] for link in self.topology] +
                       [link["src-switch"] for link in self.topology])
        vertices = sorted(list(vertices))
        graph = Graph(vertices=vertices)
        for link in self.topology:
            src_idx = vertices.index(link["src-switch"])
            dst_idx = vertices.index(link["dst-switch"])
            graph.graph[src_idx][dst_idx] = link["weight"]
            graph.graph[dst_idx][src_idx] = link["weight"]
        return graph

    def set_weight(self) -> List[Dict]:
        print(f"GOING TO {self.set_weight}")
        for link in self.topology:
            link["weight"] = random.randint(1, 10)

    def get_host(self, switch_DPID: str) -> list:
        url = f"http://{self.controller_ip}:{self.controller_port}/wm/device/"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to retrieve host information. Status code:",
                            response.status_code)
        host_info = json.loads(response.text)
        devices = host_info["devices"]
        return [d for d in devices if d.get('attachmentPoint') and d.get('attachmentPoint')[0]['switch'] == switch_DPID]

    def get_host_port(self, switch_DPID: str) -> int:
        host = self.get_host(switch_DPID)
        return int(host[0]["attachmentPoint"][0]["port"]) if host else -1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Please provide two nodes for example \"python floodlight_manager 1 2\" to push rules for (S1, S2).")
        sys.exit(1)
    src = int(sys.argv[1]) - 1
    dst = int(sys.argv[2]) - 1
    manager = Manager(src, dst)
    pprint.pprint(manager.topology)
    print()
    print(manager.path)
    manager.make_flows(manager.path)
    print(manager.path[::-1])
    manager.make_flows(manager.path[::-1])
    pprint.pprint(manager.flows)
    manager.push_flows()
