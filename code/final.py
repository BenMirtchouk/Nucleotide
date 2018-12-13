# Node, Edge, and Graph objects are based off of POA py
# These objects will be used to implement our Graph-to-Graph algorithm

class Node(object):
    def __init__(self, nodeID=-1, base='N'):
        self.ID = nodeID
        self.base = base
        self.outEdges = []
        self.inEdges = []
        self.alignedTo = []

    def __str__(self):
        return "(%d:%s) %s" % (self.ID, self.base, str([str(e) for e in self.outEdges])) 


class Edge(object):
    def __init__(self, inNodeID=-1, outNodeID=-1, label=None):
        self.inNodeID  = inNodeID
        self.outNodeID = outNodeID
        
        if label is None:
            self.labels = []
        elif isinstance(label, list):
            self.labels = label
        else:
            self.labels = [label]
        
    def __str__(self):
        return "(%d) -> (%d) %s" % (self.inNodeID, self.outNodeID, self.labels)
    
class Graph(object):
    def __init__(self, seq=None, label=None):
        self.nnodes = 0
        self.nedges = 0
        self.nodedict = {}
        self.nodeidlist = []   # allows a (partial) order to be imposed on the nodes
        
        self.label = label
        
        self._nextnodeID = 0
        self.__seqs = []
        self.__starts = []
        self.__needsort = True
        
        if seq is not None:
            prev_nid = None
            
            for c in seq:
                nid = self.addNode(c)
                
                if prev_nid is not None:
                    self.addEdge(prev_nid, nid, label)
                    self.nedges += 1
                
                prev_nid = nid
            
            self.__seqs.append(label)

    def topological_sort(self):
        visited = set()
        current = []
        
        def dfs(nid):
            if nid in visited:
                return
            
            for out_edge in self.nodedict[nid].outEdges:
                dfs(out_edge.outNodeID)
            
            visited.add(nid)
            current.append(nid)
        
        self.nodeidlist = []
        
        for nid in self.nodedict:
            if nid not in visited:
                dfs(nid)   
                self.nodeidlist.extend(current) 
                current = []
        
        self.nodeidlist = self.nodeidlist[::-1]
        
    def topological_order(self):
        if self.__needsort:
            self.topological_sort()
        return self.nodeidlist
        
    def addNode(self, base):
        nid = self._nextnodeID
        newnode = Node(nid, base)
        self.nodedict[nid] = newnode
        self.nnodes += 1
        self._nextnodeID += 1
        return nid
    
    def addEdge(self, inNodeID, outNodeID, label = None):
        self.nodedict[inNodeID].outEdges.append(Edge(inNodeID, outNodeID, label))
        self.nodedict[outNodeID].inEdges.append(Edge(inNodeID, outNodeID, label))
        self.nedges += 1
    
    def __str__(self):
        return '\n'.join([str(self.nodedict[nid]) for nid in self.nodedict])

    @staticmethod
    def align(graph1, graph2):
        # dp[i][j] = best score to have aligned the first i bases of g1 & j bases of g2
        dp = [[-10**4]*(graph2.nnodes+1) for i in range(graph1.nnodes+1)]
        
        # parent[i][j] = index into dp that led to the current best dp[i][j]
        parent = [[None]*(graph2.nnodes+1) for i in range(graph1.nnodes+1)]
        
        dp[0][0] = 0
        
        topo1 = graph1.topological_order()
        topo2 = graph2.topological_order()
        
        # if we have a new maximum, we update both the value and the parent, else nothing changes
        def max_with_parent(current_val, new_val, current_parent, new_parent):
            if new_val > current_val:
                return new_val, new_parent
            else:
                return current_val, current_parent
        
        for i in range(graph1.nnodes+1):
            for j in range(graph2.nnodes+1):
                
                if i+1 <= graph1.nnodes: 
                    # try insertion in g1 or deletion in g2
                    dp[i+1][j], parent[i+1][j] = max_with_parent(dp[i+1][j], dp[i][j]-1, parent[i+1][j], (i,j)) 
                
                if j+1 <= graph2.nnodes: 
                    # try insertion in g2 or deletion in g1
                    dp[i][j+1], parent[i][j+1] = max_with_parent(dp[i][j+1], dp[i][j]-1, parent[i][j+1], (i,j)) 
                
                if i+1 <= graph1.nnodes and j+1 <= graph2.nnodes: 
                    # try align the current bases
                    if graph1.nodedict[topo1[i]].base == graph2.nodedict[topo2[j]].base:
                        dp[i+1][j+1], parent[i+1][j+1] = max_with_parent(dp[i+1][j+1], dp[i][j]+1, parent[i+1][j+1], (i,j)) 
                    else:
                        dp[i+1][j+1], parent[i+1][j+1] = max_with_parent(dp[i+1][j+1], dp[i][j]-2, parent[i+1][j+1], (i,j)) 
        
        print dp[graph1.nnodes][graph2.nnodes]
        
        seen = set()
        done = set()
        for node1 in range(graph1.nnodes+1)[::-1]:
            if node1 in seen:
                continue
            
            for node2 in range(graph2.nnodes+1)[::-1]:
                if parent[node1][node2] != (-1,-1):
                    break
            
            dp_index = (node1, node2)
            
            while dp_index != None:
                if dp_index in done:
                    break
                
                done.add(dp_index)
                seen.add(dp_index[0])
                
                parent_index = parent[dp_index[0]][dp_index[1]]
                
                if parent_index != None and parent_index[0] != dp_index[0] and parent_index[1] != dp_index[1]:
                    print 'align',(topo1[parent_index[0]],topo2[parent_index[1]])
                    pass
                    
                dp_index = parent_index
            print '-'*50

'''
# testcase 1
g1 = Graph('SATCAAAGTC','seq1')
g2 = Graph('STTCAAGTTG','seq2')
Graph.align(g1,g2)
'''

# testcase 2
g1 = Graph()
l1 = 'SGCCCTGCAGTA'

for i in range(12):
    g1.addNode(l1[i])

g1.addEdge(0,1)
g1.addEdge(1,2)
g1.addEdge(1,8)
g1.addEdge(2,3)
g1.addEdge(8,9)
g1.addEdge(9,10)
g1.addEdge(3,4)
g1.addEdge(10,4)
g1.addEdge(4,5)
g1.addEdge(5,6)
g1.addEdge(6,7)
g1.addEdge(6,11)

g2 = Graph()
l2 = 'SGAGATCTGTACA'

for i in range(13):
    g2.addNode(l2[i])

g2.addEdge(0,1)
g2.addEdge(1,2)
g2.addEdge(2,3)
g2.addEdge(2,11)
g2.addEdge(11,6)
g2.addEdge(3,4)
g2.addEdge(4,5)
g2.addEdge(5,6)
g2.addEdge(6,7)
g2.addEdge(6,12)
g2.addEdge(7,8)
g2.addEdge(12,8)
g2.addEdge(8,9)
g2.addEdge(9,10)

Graph.align(g1,g2)

