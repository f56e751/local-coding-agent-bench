NODE, EDGE, ATTR = range(3)


class Node:
    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs

    def __eq__(self, other):
        return self.name == other.name and self.attrs == other.attrs


class Edge:
    def __init__(self, src, dst, attrs):
        self.src = src
        self.dst = dst
        self.attrs = attrs

    def __eq__(self, other):
        return (self.src == other.src and
                self.dst == other.dst and
                self.attrs == other.attrs)


class Graph:
    def __init__(self, data=None):
        self.attrs = {}
        self.nodes = []
        self.edges = []
        
        # Check if data is valid
        if data is None:
            data = []
        elif not isinstance(data, list):
            raise TypeError("Graph data malformed")
        
        # Process each item in the data
        for item in data:
            # Check if item is a tuple/list
            if not isinstance(item, (tuple, list)):
                raise TypeError("Graph item incomplete")
            
            # Check if item has at least one element
            if len(item) == 0:
                raise TypeError("Graph item incomplete")
            
            item_type = item[0]
            
            if item_type == ATTR:
                # Attribute: (ATTR, key, value) - needs exactly 3 elements
                if len(item) != 3:
                    raise ValueError("Attribute is malformed")
                key = item[1]
                value = item[2]
                if not isinstance(key, (str, int)) or not isinstance(value, (str, int)):
                    raise ValueError("Attribute is malformed")
                self.attrs[key] = value
                
            elif item_type == NODE:
                # Node: (NODE, name, attrs) - needs exactly 3 elements
                if len(item) != 3:
                    raise ValueError("Node is malformed")
                name = item[1]
                attrs = item[2]
                if not isinstance(name, str) or not isinstance(attrs, dict):
                    raise ValueError("Node is malformed")
                self.nodes.append(Node(name, attrs))
                
            elif item_type == EDGE:
                # Edge: (EDGE, src, dst, attrs) - needs exactly 4 elements
                if len(item) != 4:
                    raise ValueError("Edge is malformed")
                src = item[1]
                dst = item[2]
                attrs = item[3]
                if not isinstance(src, str) or not isinstance(dst, str) or not isinstance(attrs, dict):
                    raise ValueError("Edge is malformed")
                self.edges.append(Edge(src, dst, attrs))
                
            else:
                raise ValueError("Unknown item")
