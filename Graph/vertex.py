class Vertex(object):

    def __init__(self, vertex):
        """Initializes a vertex and its neighbors

        neighbors: set of vertices adjacent to self,
        stored in a dictionary with 
          key = vertex,
          value = weight of edge between self and neighbor.
        """
        self.id = vertex
        self.neighbors = {}

    def add_neighbor(self, vertex, weight=0):
        """Adds a neighbor along a weighted edge"""
        if vertex not in self.neighbors:
            self.neighbors[vertex] = weight

    def __str__(self):
        """Outputs the list of neighbors of this vertex"""
        return str(self.id) + " adjancent to " + str([x.id for x in self.neighbors])

    def get_neighbors(self):
        """Returns the neighbors of this vertex"""
        return self.neighbors.keys()

    def get_id(self):
        """Returns the id of this vertex"""
        return self.id

    def get_edge_weight(self, vertex):
        """Returns the weight of this edge"""
        return self.neighbors[vertex]
