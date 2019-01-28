from collections import deque
import random
import string

# Node, Edge, and Graph objects are based off of POA py
# These objects will be used to implement our Graph-to-Graph algorithm

class Node(object):
    def __init__(self, nodeID=-1, base='N'):
        self.ID = nodeID
        self.base = base
        self.inEdges = {}   # inEdge[id]    stores the in      edge between self and id
        self.outEdges = {}  # outEdge[id]   stores the out     edge between self and id
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
    def addOutEdge(self, nodeID, label):
        if nodeID in self.outEdges:
            self.outEdges[nodeID].addlabel(label)
            return False
        else:
            self.outEdges[nodeID] = Edge(self.ID, nodeID, label)
            return True
            
    def addInEdge(self, nodeID, label):
        if nodeID in self.inEdges:
            self.inEdges[nodeID].addlabel(label)
            return False
        else:
            self.inEdges[nodeID] = Edge(nodeID, self.ID, label)
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
        
    def merge_nodes(self, id1, id2):
        if id1 == id2:
            return
        nd1 = self.nodedict[id1]
        nd2 = self.nodedict[id2]
        
        for outNodeID in nd2.outEdges:
            self.addEdge(id1, outNodeID, nd2.outEdges[outNodeID].labels)
            
        for inNodeID in nd2.inEdges:
            self.addEdge(inNodeID, id1, nd2.inEdges[inNodeID].labels)
            
        for alignedID in nd2.alignedTo: 
            self.align_nodes(id1, alignedID, self.label)
    
    ## TODO break topo ties based on score
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
            print 'bad'
            exit(0)
        
    def breaksAcyclic(self, id1, id2):
        recStack = set()
        done = set()
        
        def dfs(u, done, recStack):
            if u in done:
                return False
            if u in recStack:
                return True
  
            if u == id1 or u == id2:
                recStack.add(id1)
                recStack.add(id2)
                for v in self.nodedict[id1].outEdges.keys() + self.nodedict[id2].outEdges.keys():
                    if dfs(v, done, recStack):
                        return True
                done.add(id1)
                done.add(id2)
            else:
                recStack.add(u)
                for v in self.nodedict[u].outEdges:
                    if dfs(v, done, recStack):
                        return True
                done.add(u)
                
            return False
            
        for nid in self.nodedict:
            if nid not in done:
                if dfs(nid, done, recStack):
                    return True
        return False           
        
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
        if self.nodedict[inNodeID].addOutEdge(outNodeID, label):
            self.nedges += 1
        self.nodedict[outNodeID].addInEdge(inNodeID, label)
        
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
        if self.nnodes == 0:
            return
        
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
        
    def visJSoutput(self, divID, useConsensus=True,  arrows=False):
        
        cons = {}
        if useConsensus:
            cons = {nid:i for i, nid in enumerate(self.consensus())}
        else:
            cons = {nid:i for i, nid in enumerate(self.nodeidlist)} ##
        
        num_cons = 0
        
        nodes = 'var nodes = ['
        edges = 'var edges = ['
        accountedFor = set()
        
        for nodeID in self.nodeidlist:
            extra = ''
            if nodeID in cons: 
                extra = ', fixed: {{ x : true }}, x: {0}, y: 0'.format(cons[nodeID]*150) # horizontal
                # extra = ', fixed: {{ y : true }}, x: 0, y: {0}'.format(cons[nodeID]*150) # vertical
                num_cons += 1
            else:
                extra = ', x: {0}, y: 0'.format(num_cons*150)
                
            nodes += '{{ id:{0}, label: "{1}"{2} }},'.format(nodeID, self.nodedict[nodeID].base, extra)
            node = self.nodedict[nodeID]
            
            for nbr in node.outEdges:
                agreements = len(node.outEdges[nbr].labels)
                  
                edges += '{{from: {0}, to: {1}, value: {2}, arrows:{{ to: {{ enabled: {3}, scaleFactor: 1 }} }} }},'.format(nodeID, nbr, agreements, 'true' if arrows else 'false')
            
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

    def graphData(self, useConsensus=True, arrows=False):
        rnd = self.randomString()
        div = '<div id="{0}"></div>'.format(rnd)
        script = self.visJSoutput(rnd, useConsensus=useConsensus, arrows=arrows)

        return div + script