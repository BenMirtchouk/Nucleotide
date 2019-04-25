from collections import deque
import random
import string
from math import log
import heapq

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

    # Adds alignment edge between self and another node
    def alignTo(self, nodeID, agreements):
        if nodeID in self.alignedTo:
            self.alignedTo[nodeID].agreements += agreements
        else:
            self.alignedTo[nodeID] = Edge(self.ID, nodeID, agreements)
        
    # Return if a new edge was created
    # Adds an edge going out
    def addOutEdge(self, nodeID, agreements=1):
        if nodeID in self.outEdges:
            self.outEdges[nodeID].agreements += agreements
            return False
        else:
            self.outEdges[nodeID] = Edge(self.ID, nodeID, agreements)
            return True
    
    # Adds an edge going in        
    def addInEdge(self, nodeID, agreements=1):
        if nodeID in self.inEdges:
            self.inEdges[nodeID].agreements += agreements
            return False
        else:
            self.inEdges[nodeID] = Edge(nodeID, self.ID, agreements)
            return True
        
class Edge(object):
    def __init__(self, inNodeID=-1, outNodeID=-1, agreements=1):
        self.inNodeID  = inNodeID
        self.outNodeID = outNodeID
        self.agreements = agreements
        
    def __str__(self):
        return "%d -> %d [%d]" % (self.inNodeID, self.outNodeID, self.agreements)
    
class Graph(object):
    def __init__(self, seq=None, seqs=0):
        self.nnodes = 0
        self.nedges = 0
        self.nodedict = {}
        self.nodeidlist = []   # allows a (partial) order to be imposed on the nodes
        self._nextnodeID = 0
        self._seqs = seqs
        self.__needsort = True
        
        if seq is not None:
            prev_nid = None
            
            for c in seq:
                nid = self.addNode(c)
                
                if prev_nid is not None:
                    self.addEdge(prev_nid, nid)
                    self.nedges += 1
                
                prev_nid = nid
            
            self._seqs = 1

    def align_nodes(self, id1, id2, agreements):
        self.nodedict[id1].alignTo(id2, agreements)
        self.nodedict[id2].alignTo(id1, agreements)
    
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
        
        # Error checking, TODO delete this
        if self.nnodes != len(self.nodeidlist):
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
'''.format(self.graphData(useConsensus=False, arrows=True))
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
    
    def addEdge(self, inNodeID, outNodeID, agreements=1):
        if self.nodedict[inNodeID].addOutEdge(outNodeID, agreements):
            self.nedges += 1
        self.nodedict[outNodeID].addInEdge(inNodeID, agreements)
    
    def __str__(self):
        return '\n'.join([str(self.nodedict[nid]) for nid in self.nodedict])

    # If we have a new maximum, we update both the value and the parent, 
    # Else nothing changes
    @staticmethod
    def max_with_parent(current_val, new_val, current_parent, new_parent):
        if new_val > current_val:
            return new_val, new_parent
        else:
            return current_val, current_parent
             
    # Generating consensus path (path of highest confidence)   
    def consensus(self):
        if self.nnodes == 0:
            return
        
        dp = [0] * self.nnodes
        parent = [None] * self.nnodes
        dp[0] = 0
        
        topo = self.topological_order()
        
        for nid in topo:
            for nbr_id in self.nodedict[nid].outEdges:
                agreements = self.nodedict[nid].outEdges[nbr_id].agreements
                
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
        
    # Generating .gml output for visualization
    def gephiOutput(self):
        nodes = ''
        edges = ''
        accountedFor = set()
        
        for nodeID in self.nodeidlist:
            extra = ''
            if hasattr(self, 'scores'):
                extra = '    conf {0}\n'.format(self.scores[nodeID])
            
            nodes += '\n  node\n  [\n    id {0}\n    label "{1}"\n{2}  ]'.format(nodeID, self.nodedict[nodeID].base, extra)
            node = self.nodedict[nodeID]
            
            for nbr in node.outEdges:
                agreements = node.outEdges[nbr].agreements
                  
                edges += '\n  edge\n  [\n    source {0}\n    target {1}\n    value {2}\n  ]'.format(nodeID, nbr, agreements)
            
            for nbr in node.alignedTo:
                nbrEdge = node.alignedTo[nbr]
                
                if (nbrEdge.inNodeID, nbrEdge.outNodeID) in accountedFor or \
                   (nbrEdge.outNodeID, nbrEdge.inNodeID) in accountedFor:
                    continue
                
                accountedFor.add((nbrEdge.inNodeID, nbrEdge.outNodeID))
                
                agreements = nbrEdge.agreements
                edges += '\n  edge\n  [\n    source {0}\n    target {1}\n    value {2}\n  ]'.format(nodeID, nbr, agreements)
            
        graph = 'graph \n[' + nodes + edges + '\n]'
        
        with open('test.gml','w') as f:
            f.write(graph)
        
        return ''
        
    # Generating output for visJS visualization
    def visJSoutput(self, divID, useConsensus=True, arrows=False, vertical=False):
        
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
            if self.scores[nodeID] < 0.4:
                continue
                
            extra = ''
            if nodeID in cons: 
                if vertical:
                    extra = ', fixed: {{ y : true }}, x: 0, y: {0}'.format(cons[nodeID]*150) # vertical
                else:
                    extra = ', fixed: {{ x : true }}, x: {0}, y: 0'.format(cons[nodeID]*150) # horizontal
                num_cons += 1
            else:
                extra = ', x: {0}, y: 0'.format(num_cons*150)
                
            nodes += '{{ id:{0}, label: "{1}"{2} }},'.format(nodeID, self.nodedict[nodeID].base + " " + str(self.nodedict[nodeID].ID), extra)
            node = self.nodedict[nodeID]
            
            for nbr in node.outEdges:
                agreements = node.outEdges[nbr].agreements * (random.random() * 3 + 2)
                  
                edges += '{{from: {0}, to: {1}, value: {2}, arrows:{{ to: {{ enabled: {3}, scaleFactor: 1 }} }} }},'.format(nodeID, nbr, agreements, 'true' if arrows else 'false')
            
            for nbr in node.alignedTo:
                nbrEdge = node.alignedTo[nbr]
                
                if (nbrEdge.inNodeID, nbrEdge.outNodeID) in accountedFor or \
                   (nbrEdge.outNodeID, nbrEdge.inNodeID) in accountedFor:
                    continue
                
                accountedFor.add((nbrEdge.inNodeID, nbrEdge.outNodeID))
                
                agreements = nbrEdge.agreements
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

    def graphData(self, useConsensus=True, arrows=False, vertical=False):
        rnd = self.randomString()
        div = '<div id="{0}"></div>'.format(rnd)
        script = self.visJSoutput(rnd, useConsensus=useConsensus, arrows=arrows, vertical=vertical)

        return div + script
    
    def getRegex(self, threshold, verbose):
        topo = self.topological_order()
        
        dist = [-1] * self.nnodes
        def getdist(nid):
            if dist[nid] != -1:
                return dist[nid]
            
            dist[nid] = 0
            for nbr_id in self.nodedict[nid].outEdges:
                if self.scores[nbr_id] >= threshold:
                    dist[nid] = max(dist[nid], getdist(nbr_id) + 1)
            return dist[nid]
        getdist(topo[0])
        
        def getTerm(node):
            seen = set()
            pq = []
            for nbr_id in node.outEdges:
                if nbr_id not in seen and self.scores[nbr_id] >= threshold:
                    pq.append((-dist[nbr_id], nbr_id))
                    seen.add(nbr_id)
            heapq.heapify(pq)
            
            while len(pq) > 1:
                nid = heapq.heappop(pq)[1]
                for nbr_id in self.nodedict[nid].outEdges:
                    if nbr_id not in seen and self.scores[nbr_id] >= threshold:
                        seen.add(nbr_id)
                        heapq.heappush(pq, (-dist[nbr_id], nbr_id))
            
            terminating_node = pq[0][1]
            
            return terminating_node
        
        def getSeq(node, last):
            cur = node
            ans = ''
            while cur != last:
                term = getTerm(self.nodedict[cur])
                
                answers = []
                for nbr_id in self.nodedict[cur].outEdges:
                    if self.scores[nbr_id] >= 0.25:
                        answers.append(getSeq(nbr_id, term)[:-1])
                
                if verbose:
                    print 'DID',node,'->',last,'needs',cur,'->',term,'gave',answers
                
                if len(answers) == 1:
                    ans += answers[0]
                elif len(answers) > 1:
                    ans += '({0})'.format('|'.join(answers))
                ans += self.nodedict[term].base
                
                cur = term
            
            return self.nodedict[node].base + ans
            
        return getSeq(topo[0], topo[-1])
        
    def alignmentOutput(self, verbose=False):
        score = [0.] * self.nnodes
        count = [0] * self.nnodes
        
        # hmm
        threshold = 0.25 
        
        topo = self.topological_order()
        for nid in topo:
            node = self.nodedict[nid]
            
            if len(node.inEdges) == 0:
                score[nid] = 1
                count[nid] = 1
            
            if verbose:
                print '\n',nid,'->', score[nid], '/',count[nid]
            if len(node.outEdges) == 1:
                nbr_id = node.outEdges.keys()[0]
                ag = node.outEdges[nbr_id].agreements
                scr = 1.0 * ag/self._seqs
                
                if verbose:
                    print '\toffer',nid,'->',nbr_id, '=',score[nid] + scr, '/',count[nid]+1
                if count[nbr_id] == 0 or (score[nid] + scr)/(count[nid] + 1) > score[nbr_id]/count[nbr_id]:
                    score[nbr_id] = score[nid] + scr
                    count[nbr_id] = count[nid] + 1
                
                continue
            
            for nbr_id in node.outEdges:
                ag = node.outEdges[nbr_id].agreements
                scr = 1.0 * ag/self._seqs
                
                if verbose:
                    print '\toffer',nid,'->',nbr_id, '=',scr, '/',1
                if count[nbr_id] == 0 or scr > score[nbr_id] / count[nbr_id]:
                    score[nbr_id] = scr
                    count[nbr_id] = 1
        
        self.scores = [1.0*score[i]/count[i] for i in range(self.nnodes)]

        if verbose:
            for i in range(self.nnodes):
                print i,':',self.scores[i]
        return self.getRegex(threshold, verbose)
 