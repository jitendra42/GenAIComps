# Copyright (c) 2024 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import OrderedDict, defaultdict
from copy import deepcopy


class DAG(object):
    def __init__(self):
        self.reset_graph()

    def add_node(self, node_name: str):
        graph = self.graph
        if node_name in graph:
            raise KeyError("node %s already exists" % node_name)
        graph[node_name] = set()

    def add_node_if_not_exists(self, node_name):
        try:
            self.add_node(node_name)
        except KeyError:
            pass

    def delete_node(self, node_name):
        graph = self.graph
        if node_name not in graph:
            raise KeyError("node %s does not exist" % node_name)
        graph.pop(node_name)

        for node, edges in graph.items():
            if node_name in edges:
                edges.remove(node_name)

    def delete_node_if_exists(self, node_name):
        try:
            self.delete_node(node_name)
        except KeyError:
            pass

    def add_edge(self, ind_node, dep_node):
        graph = self.graph
        if ind_node not in graph or dep_node not in graph:
            raise KeyError("one or more nodes do not exist in graph")
        test_graph = deepcopy(graph)
        test_graph[ind_node].add(dep_node)
        is_valid = self.validate(test_graph)
        if is_valid:
            graph[ind_node].add(dep_node)
        else:
            raise Exception("validation error!")

    def delete_edge(self, ind_node, dep_node):
        graph = self.graph
        if dep_node not in graph.get(ind_node, []):
            raise KeyError("this edge does not exist in graph")
        graph[ind_node].remove(dep_node)

    def predecessors(self, node):
        graph = self.graph
        return [key for key in graph if node in graph[key]]

    def downstream(self, node) -> list:
        graph = self.graph
        if node not in graph:
            raise KeyError("node %s is not in graph" % node)
        return list(graph[node])

    def all_downstreams(self, node):
        graph = self.graph
        nodes = [node]
        nodes_seen = set()
        i = 0
        while i < len(nodes):
            downstreams = self.downstream(nodes[i])
            for downstream_node in downstreams:
                if downstream_node not in nodes_seen:
                    nodes_seen.add(downstream_node)
                    nodes.append(downstream_node)
            i += 1
        return list(filter(lambda node: node in nodes_seen, self.topological_sort(graph=graph)))

    def all_leaves(self):
        graph = self.graph
        return [key for key in graph if not graph[key]]

    def from_dict(self, graph_dict):
        self.reset_graph()
        for new_node in graph_dict.keys():
            self.add_node(new_node)
        for ind_node, dep_nodes in graph_dict.items():
            if not isinstance(dep_nodes, list):
                raise TypeError("dict values must be lists")
            for dep_node in dep_nodes:
                self.add_edge(ind_node, dep_node)

    def reset_graph(self):
        self.graph = OrderedDict()

    def ind_nodes(self, graph=None):
        graph = graph if graph is not None else self.graph

        dependent_nodes = set(node for dependents in graph.values() for node in dependents)
        return [node for node in graph.keys() if node not in dependent_nodes]

    def validate(self, graph=None):
        graph = graph if graph is not None else self.graph
        if len(self.ind_nodes(graph=graph)) == 0:
            # no independent nodes
            return False
        try:
            self.topological_sort(graph)
        except ValueError:
            # topological sort failed
            return False
        return True

    def topological_sort(self, graph=None):
        if graph is None:
            graph = self.graph
        result = []
        in_degree = defaultdict(lambda: 0)

        for u in graph:
            for v in graph[u]:
                in_degree[v] += 1
        ready = [node for node in graph if not in_degree[node]]

        while ready:
            u = ready.pop()
            result.append(u)
            for v in graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    ready.append(v)

        if len(result) == len(graph):
            return result
        else:
            raise ValueError("graph is not acyclic")

    def size(self):
        return len(self.graph)


if __name__ == "__main__":
    dag = DAG()
    # a->b->c->d
    # a->d
    dag.add_node("a")
    dag.add_node("b")
    dag.add_edge("a", "b")
    dag.add_node("c")
    dag.add_node("d")
    dag.add_edge("a", "d")
    dag.add_edge("b", "c")
    dag.add_edge("c", "d")
    assert dag.topological_sort() == ["a", "b", "c", "d"]
    assert dag.graph == OrderedDict([("a", {"d", "b"}), ("b", {"c"}), ("c", {"d"}), ("d", set())])
    assert sorted(dag.all_downstreams("a")) == ["b", "c", "d"]
    assert dag.size() == 4
    assert sorted(dag.predecessors("d")) == ["a", "c"]
    assert dag.ind_nodes() == ["a"]
    assert dag.all_leaves() == ["d"]
    assert sorted(dag.all_downstreams("a")) == ["b", "c", "d"]
    assert sorted(dag.downstream("a")) == ["b", "d"]
    assert dag.predecessors("c") == ["b"]

    dag2 = DAG()
    graph_dict = {"a": ["b", "d"], "b": ["c"], "c": ["d"], "d": []}
    dag2.from_dict(graph_dict)
    assert dag.graph == dag2.graph

    dag2.delete_edge("a", "b")
    assert dag2.graph == OrderedDict([("a", {"d"}), ("b", {"c"}), ("c", {"d"}), ("d", set())])
    dag2.delete_node("c")
    assert dag2.graph == OrderedDict([("a", {"d"}), ("b", set()), ("d", set())])