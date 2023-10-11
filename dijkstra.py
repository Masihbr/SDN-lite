import sys

class Graph:
    def __init__(self, vertices):
        self.V = len(vertices)
        self.vertices = vertices
        self.graph = [[0 for _ in range(self.V)] for _ in range(self.V)]

    def dijkstra(self, src, dst):
        num_nodes = len(self.graph)
        distances = [sys.maxsize] * num_nodes
        visited = [False] * num_nodes
        previous = [-1] * num_nodes

        distances[src] = 0

        while not visited[dst]:
            min_distance = sys.maxsize
            min_node = -1

            for node in range(num_nodes):
                if not visited[node] and distances[node] < min_distance:
                    min_distance = distances[node]
                    min_node = node

            visited[min_node] = True

            for neighbor in range(num_nodes):
                if self.graph[min_node][neighbor] > 0:
                    new_distance = distances[min_node] + self.graph[min_node][neighbor]
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous[neighbor] = min_node

        path = []
        current_node = dst

        while current_node != -1:
            path.insert(0, current_node)
            current_node = previous[current_node]

        return path, distances[dst]