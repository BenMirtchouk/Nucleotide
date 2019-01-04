import random
import string

# Node, Edge, and Graph objects are based off of POA py
# These objects will be used to implement our Graph-to-Graph algorithm

class Node(object):
    def __init__(self, nodeID=-1, base='N'):
        self.ID = nodeID
        self.base = base
        self.outEdges = {} # outEdge[id] stores the out edge between self and id
        self.alignedTo = {} # alignedTo[id] stores the aligned edge between self and id

    def __str__(self):
        edges = '  ,  '.join(["%s" % self.outEdges[e] for e in self.outEdges])
        aligned = '  ,  '.join(["%s" % self.alignedTo[n] for n in self.alignedTo])
        return "(%d:%s)\t%s%s| %s" % (self.ID, self.base, edges, ' '*(60-len(edges)), aligned) 

    def alignTo(self, nodeID, label):
        if nodeID in self.alignedTo:
            self.alignedTo[nodeID].addlabel(label)
        else:
            self.alignedTo[nodeID] = Edge(self.ID, nodeID, label)
        
    # return if a new edge was created
    def addEdge(self, nodeID, label):
        if nodeID in self.outEdges:
            self.outEdges[nodeID].addlabel(label)
            return False
        else:
            self.outEdges[nodeID] =  Edge(self.ID, nodeID, label)
            return True
        
        
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
        return "%d -> %d %s" % (self.inNodeID, self.outNodeID, ', '.join(self.labels))
    
    def addlabel(self, label):
        if isinstance(label, list):
            self.labels.extend(label)
        else:
            self.labels.append(label)
    
class Graph(object):
    def __init__(self, seq=None, label=None):
        self.nnodes = 0
        self.nedges = 0
        self.nodedict = {}
        self.nodeidlist = []   # allows a (partial) order to be imposed on the nodes
        
        if label is None:
            self.label = []
        elif isinstance(label, list):
            self.label = label
        else:
            self.label = [label]
        
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

    def align_nodes(self, id1, id2, label):
        self.nodedict[id1].alignTo(id2, label)
        self.nodedict[id2].alignTo(id1, label)
    
    def topological_sort(self):
        visited = set()
        current = []
        
        def dfs(nid):
            if nid in visited:
                return
            
            for out_nbr in self.nodedict[nid].outEdges:
                dfs(self.nodedict[nid].outEdges[out_nbr].outNodeID)
            
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
        if self.nodedict[inNodeID].addEdge(outNodeID, label):
            self.nedges += 1
    
    def __str__(self):
        return '\n'.join([str(self.nodedict[nid]) for nid in self.nodedict])

    def visJSoutput(self, divID):
        
        nodes = 'var nodes = ['
        edges = 'var edges = ['
        accountedFor = set()
        
        for nodeID in self.nodedict:
            nodes += '{{id:{0}, label: "{1}"}},'.format(nodeID, self.nodedict[nodeID].base)
            node = self.nodedict[nodeID]
            
            for nbr in node.outEdges:
                agreements = len(node.outEdges[nbr].labels)
                edges += '{{from: {0}, to: {1}, value: {2}}},'.format(nodeID, nbr, agreements)
            
            for nbr in node.alignedTo:
                nbrEdge = node.alignedTo[nbr]
                
                if (nbrEdge.inNodeID, nbrEdge.outNodeID) in accountedFor or \
                   (nbrEdge.outNodeID, nbrEdge.inNodeID) in accountedFor:
                    continue
                
                accountedFor.add((nbrEdge.inNodeID, nbrEdge.outNodeID))
                
                agreements = len(nbrEdge.labels)
                edges += '{{from: {0}, to: {1}, value: {2}, style: "dash-line"}},'.format(nodeID, nbr, agreements)
        
        nodes = nodes[:-1] + '];'
        edges = edges[:-1] + '];'
        
        script = '''
<script>
    {0}
    {1}
    var container = document.getElementById('{2}');
    var data= {{
        nodes: nodes,
        edges: edges,
    }};
    var options = {{
        width: '100%',
        height: '800px'
    }};
    var network = new vis.Network(container, data, options);
</script>
                    '''.format(nodes,edges,divID)
        
        return script

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
        
        seen = set()
        done = set()
        alias = dict() # maps graph1 node numbers to graph2
        aligned = []
        
        # pick last unseen node from first graph
        for node1 in range(graph1.nnodes, -1, -1):
            if node1 in seen:
                continue
            
            # select where in the dp array to start
            for node2 in range(graph2.nnodes, -1, -1):
                if parent[node1][node2] != None:
                    break
            
            dp_index = (node1, node2)
            
            # move backwards through the parent chain in dp
            while dp_index != None:
                if dp_index in done:
                    break
                
                done.add(dp_index)
                seen.add(dp_index[0])
                
                parent_index = parent[dp_index[0]][dp_index[1]]
                
                # if both indicies changed we have alignment
                if parent_index != None and parent_index[0] != dp_index[0] and parent_index[1] != dp_index[1]:
                    n1 = graph1.nodedict[ topo1[parent_index[0]] ]
                    n2 = graph2.nodedict[ topo2[parent_index[1]] ]
                    
                    if n1.base == n2.base:
                        alias[ n2.ID ] = n1.ID
                    else:
                        aligned.append( (n1.ID, n2.ID) )
                    
                dp_index = parent_index
        
        for nodeID in topo2:
            if nodeID not in alias:
                nd = graph2.nodedict[ nodeID ]
                alias[nodeID] = graph1.addNode(nd.base)
        
        for nodeID in topo2:
            nd2 = graph2.nodedict[ nodeID ]
            nd1 = graph1.nodedict[ alias[nodeID] ]
            
            for outNodeID in nd2.outEdges:
                graph1.addEdge(alias[nodeID], alias[outNodeID], nd2.outEdges[outNodeID].labels)
            
            for alignedID in nd2.alignedTo:
                graph1.align_nodes(alias[nodeID], alias[alignedID], graph2.label)
                
        
        for n1ID, n2ID in aligned:
            graph1.align_nodes(n1ID, alias[ n2ID ], graph1.label + graph2.label)

    @staticmethod
    def randomString():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

    def graphData(self):
        rnd = self.randomString()
        div = '<div id="{0}"></div>'.format(rnd)
        script = self.visJSoutput(rnd)

        return div + script