from collections import deque
import random
import string

# initialize constants

inf = 10**4
score = {
    'match'    : +2,
    'mismatch' : -3,
    'indel'    : -2
}

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
            self.labels.extend([lbl for lbl in label if lbl not in self.labels])
        else:
            if label not in self.labels:
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
        inDeg = {}
        
        for nid in self.nodedict:
            inDeg[nid] = 0
        for nid in self.nodedict:
            for nbr_id in self.nodedict[nid].outEdges:
                inDeg[nbr_id] += 1
        
        self.nodeidlist = []
        
        queue = deque([nid for nid in self.nodedict if inDeg[nid] == 0])
        while len(queue):
            nid = queue.popleft()
            self.nodeidlist.append(nid)
            
            for nbr_id in self.nodedict[nid].outEdges:
                inDeg[nbr_id] -= 1
                
                if inDeg[nbr_id] == 0:
                    queue.append(nbr_id)
        
        if self.nnodes != len(self.nodeidlist):
            print 'dammit'
            print self.nodeidlist
            doc='''
<html>
    <head>
      <title>NuCLeOTidE</title>
      <script type="text/javascript" src="visjs/vis.js"></script>
      <link href="visjs/vis-network.min.css" rel="stylesheet" type="text/css"/>
    </head>
    <body>
        {0}
    </body>
</html>
'''.format(self.graphData(useConsensus=False))
            print 'output'
            with open('out_error.html','w') as f:
                f.write(doc)
            exit(0)
        
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

    # if we have a new maximum, we update both the value and the parent, else nothing changes
    @staticmethod
    def max_with_parent(current_val, new_val, current_parent, new_parent):
        if new_val > current_val:
            return new_val, new_parent
        else:
            return current_val, current_parent
                
    def consensus(self):
        dp = [0] * self.nnodes
        parent = [None] * self.nnodes
        dp[0] = 0
        
        topo = self.topological_order()
        
        for nid in topo:
            for nbr_id in self.nodedict[nid].outEdges:
                agreements = len(self.nodedict[nid].outEdges[nbr_id].labels)
                
                dp[nbr_id], parent[nbr_id] = Graph.max_with_parent(dp[nbr_id], dp[nid] + agreements, parent[nbr_id], nid)
        
        nodeID = 0
        for i in range(1, self.nnodes):
            if dp[i] > dp[nodeID]:
                nodeID = i
        
        path = []
        while nodeID is not None:
            path.append(nodeID)
            nodeID = parent[nodeID]
        
        return path[::-1]
    
    @staticmethod
    def align(graph1, graph2):
        # dp[i][j] = best score to have aligned up to (and including) node id i in g1 and j in g2
        dp = [[-inf]*(graph2.nnodes+1) for i in range(graph1.nnodes+1)]
        
        # parent[i][j] = index into dp that led to the current best dp[i][j]
        parent = [[None]*(graph2.nnodes+1) for i in range(graph1.nnodes+1)]
        
        dp[0][0] = 0
        
        topo1 = graph1.topological_order()
        topo2 = graph2.topological_order()
        
        for node1 in topo1:
            for node2 in topo2:
                
                base1 = graph1.nodedict[node1].base
                base2 = graph2.nodedict[node2].base
                
                # insertion
                for nbr1 in graph1.nodedict[node1].outEdges:
                    dp[nbr1][node2], parent[nbr1][node2] = \
                        Graph.max_with_parent(dp[nbr1][node2], dp[node1][node2] + score['indel'], \
                                              parent[nbr1][node2], (node1,node2) )
                
                # deletion
                for nbr2 in graph2.nodedict[node2].outEdges:
                    dp[node1][nbr2], parent[node1][nbr2] = \
                        Graph.max_with_parent(dp[node1][nbr2], dp[node1][node2] + score['indel'], \
                                              parent[node1][nbr2], (node1,node2) )
                    
                # alignment
                for nbr1 in graph1.nodedict[node1].outEdges:
                    for nbr2 in graph2.nodedict[node2].outEdges:
                        dp[nbr1][nbr2], parent[nbr1][nbr2] = \
                            Graph.max_with_parent(dp[nbr1][nbr2], dp[node1][node2] + (score['match'] if base1 == base2 else score['mismatch']), \
                                                  parent[nbr1][nbr2], (node1,node2) )
                
                # end alignment
                if len(graph1.nodedict[node1].outEdges) == 0 and len(graph2.nodedict[node2].outEdges) == 0:
                    dp[graph1.nnodes][graph2.nnodes], parent[graph1.nnodes][graph2.nnodes] = \
                        Graph.max_with_parent(dp[graph1.nnodes][graph2.nnodes], dp[node1][node2] + (score['match'] if base1 == base2 else score['mismatch']), \
                                              parent[graph1.nnodes][graph2.nnodes], (node1,node2) )
                    
                     
        seen1 = set()
        seen2 = set()
        seenContext = dict()
        alias = dict() # maps graph1 node numbers to graph2
        aligned = []
        
        ## TODO break topo ties based on score
        
        Graph.traverseBack(graph1, graph2, parent, seen1, seen2, seenContext, alias, aligned, (graph1.nnodes, graph2.nnodes), dp=dp)
        
        # pick last unseen node from first graph
        for node1 in topo1[::-1]:
            if node1 in seen1:
                continue
            
            ## TODO use two-pointers to make this O(n) not O(n^2)
            
            # select where in the dp array to start
            
            dp_index = None
            
            for node2 in topo2[::-1]:
                if node2 not in seen2:
                    # check if potential dp_index has too low a score to be considered
                    
                    best = -inf
                    for nbr1 in graph1.nodedict[node1].outEdges:
                        best = max(best, seenContext[nbr1])
                    if dp[node1][node2] < best - 2*score['match']: # maybe needs tweeking
                        continue
                    
                    # set our newfound dp_index
                    
                    dp_index = (node1, node2)
                    break
            
            if dp_index is None:
                break
            
            Graph.traverseBack(graph1, graph2, parent, seen1, seen2, seenContext, alias, aligned, dp_index, dp=dp)
        
        Graph.encorporateAlignment(graph1, graph2, alias, aligned)
            
    # once we have an alignment score matrix (dp, parent), find which nodes need to be aligned starting at dp_index (and update [alias, aligned] accordingly)
    @staticmethod
    def traverseBack(graph1, graph2, parent, seen1, seen2, seenContext, alias, aligned, dp_index, dp = None):
        seen1_updt = set()
        seen2_updt = set()
        
        # move backwards through the parent chain in dp
        while dp_index != None:
            if dp_index[0] in seen1 or dp_index[1] in seen2:
                break
            
            seen1_updt.add(dp_index[0])
            seen2_updt.add(dp_index[1])
            
            if dp_index[0] not in seenContext:
                seenContext[dp_index[0]] = dp[dp_index[0]][dp_index[1]]
            else:
                seenContext[dp_index[0]] = max(seenContext[dp_index[0]], dp[dp_index[0]][dp_index[1]])
            
            parent_index = parent[dp_index[0]][dp_index[1]]
            
            # if both indicies changed we have alignment
            if parent_index != None and parent_index[0] != dp_index[0] and parent_index[1] != dp_index[1]:
                n1 = graph1.nodedict[ parent_index[0] ]
                n2 = graph2.nodedict[ parent_index[1] ]
                
                # print '\talign',n1.ID,n2.ID
                if n1.base == n2.base:
                    alias[ n2.ID ] = n1.ID
                else:
                    aligned.append( (n1.ID, n2.ID) )
                
            dp_index = parent_index
        
        seen1 |= seen1_updt
        seen2 |= seen2_updt
    
    @staticmethod
    def encorporateAlignment(graph1, graph2, alias, aligned):
        for nodeID in graph2.nodeidlist:
            if nodeID not in alias:
                nd = graph2.nodedict[ nodeID ]
                alias[nodeID] = graph1.addNode(nd.base)
        
        for nodeID in graph2.nodeidlist:
            nd2 = graph2.nodedict[ nodeID ]
            nd1 = graph1.nodedict[ alias[nodeID] ]
            
            for outNodeID in nd2.outEdges:
                ####
                if outNodeID not in alias:
                    print 'hmm something wrong'
                    print outNodeID
                    print alias
                    print graph2.nodedict
                    exit(0)
                
                # don't connect to self
                if alias[nodeID] != alias[outNodeID]:
                    graph1.addEdge(alias[nodeID], alias[outNodeID], nd2.outEdges[outNodeID].labels)
            
            for alignedID in nd2.alignedTo: 
                # don't align to self
                if alias[nodeID] != alias[alignedID]:
                    graph1.align_nodes(alias[nodeID], alias[alignedID], graph2.label)
                
        
        for n1ID, n2ID in aligned:
            # don't align to self
            if n1ID != alias[n2ID]:
                graph1.align_nodes(n1ID, alias[n2ID], graph1.label + graph2.label)
        
    def visJSoutput(self, divID, useConsensus=True):
        
        cons = {}
        if useConsensus:
            cons = {nid:i for i, nid in enumerate(self.consensus())}
        else:
            cons = {nid:i for i, nid in enumerate(self.nodeidlist)}    
        
        nodes = 'var nodes = ['
        edges = 'var edges = ['
        accountedFor = set()
        
        for nodeID in self.nodedict:
            extra = ''
            if nodeID in cons: 
                extra = ', fixed: {{ x : true }}, x: {0}, y: 0'.format(cons[nodeID]*150) # horizontal
                # extra = ', fixed: {{ y : true }}, x: 0, y: {0}'.format(cons[nodeID]*150) # vertical
            
            nodes += '{{ id:{0}, label: "{1}"{2} }},'.format(nodeID, self.nodedict[nodeID].base, extra)
            node = self.nodedict[nodeID]
            
            for nbr in node.outEdges:
                agreements = len(node.outEdges[nbr].labels)
                  
                edges += '{{from: {0}, to: {1}, value: {2}, arrows:{{ to: {{enabled: true, scaleFactor: 1}} }} }},'.format(nodeID, nbr, agreements)
            
            for nbr in node.alignedTo:
                nbrEdge = node.alignedTo[nbr]
                
                if (nbrEdge.inNodeID, nbrEdge.outNodeID) in accountedFor or \
                   (nbrEdge.outNodeID, nbrEdge.inNodeID) in accountedFor:
                    continue
                
                accountedFor.add((nbrEdge.inNodeID, nbrEdge.outNodeID))
                
                agreements = len(nbrEdge.labels)
                edges += '{{ from: {0}, to: {1}, value: {2}, dashes: [10,15]}},'.format(nodeID, nbr, agreements)
        
        nodes = nodes[:-1] + '];'
        edges = edges[:-1] + '];'
        
        script = '''
<script type="text/javascript">
    {0}
    {1}
    var container = document.getElementById('{2}');
    var data= {{
        nodes: nodes,
        edges: edges,
    }};
    var options = {{
        width: '100%',
        height: '100%'
    }};
    var network = new vis.Network(container, data, options);
</script>
                    '''.format(nodes,edges,divID)
        
        return script

    @staticmethod
    def randomString():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

    def graphData(self, useConsensus=True):
        rnd = self.randomString()
        div = '<div id="{0}"></div>'.format(rnd)
        script = self.visJSoutput(rnd, useConsensus)

        return div + script