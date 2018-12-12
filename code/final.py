class Node(object):
    def __init__(self, nodeID=-1, base='N'):
        self.ID = nodeID
        self.base = base
        self.outEdges = []
        self.alignedTo = []

    def __str__(self):
        return "(%d:%s)" % (self.ID, self.base)

    # def addOutEdge(self, neighbourID, label):
    #     self._add_edge(self.outEdges, neighbourID, label)

    # def nextNode(self, label):
    #     """Returns the first (presumably only) outward neighbour
    #        having the given edge label"""
    #     nextID = None
    #     for e in self.outEdges:
    #         if label in self.outEdges[e].labels:
    #             nextID = e
    #     return nextID

    # @property
    # def alignDegree(self):
    #     return len(self.alignEdges)
    #
    # @property
    # def outDegree(self):
    #     return len(self.outEdges)


class Edge(object):
    def __init__(self, inNodeID=-1, outNodeID=-1, label=None):
        self.inNodeID  = inNodeID
        self.outNodeID = outNodeID
        # if label is None:
        #     self.labels = []
        # elif type(label) == list:
        #     self.labels = label
        # else:
        #     self.labels = [label]
        # return

    def __str__(self):
        nodestr = "(%d) -> (%d) " % (self.inNodeID, self.outNodeID)
        return nodestr

        # if self.labels is None:
        #     return nodestr
        # else:
        #     return nodestr + self.labels.__str__()


class Graph(object):
    def __init__(self, seq=None, label=None):
        self._nextnodeID = 0
        self._nnodes = 0
        self._nedges = 0
        self.nodedict = {}
        self.nodeidlist = []   # allows a (partial) order to be imposed on the nodes
        self.__needsort = False
        self.__labels = []
        self.__seqs = []
        self.__starts = []

        if seq is not None:
            self.addUnmatchedSeq(seq, label)

    def addNode(self, base):
        nid = self._nextnodeID
        newnode = Node(nid, base)
        self.nodedict[nid] = newnode
        self.nodeidlist.append(nid)
        self._nnodes += 1
        self._nextnodeID += 1
        return nid

    @property
    def needsSort(self):
        return self.__needsort

    @property
    def nNodes(self):
        return self._nnodes

    @property
    def nEdges(self):
        return self._nedges

    # def jsOutput(self):
    #     """returns a list of strings containing a a description of the graph for viz.js, http://visjs.org"""
    #
    #     # get the consensus sequence, which we'll use as the "spine" of the
    #     # graph
    #     path, __, __ = self.consensus()
    #     pathdict = {}
    #     for i, nodeID in enumerate(path):
    #         pathdict[nodeID] = i*150
    #
    #     lines = ['var nodes = [']
    #
    #     ni = self.nodeiterator()
    #     count = 0
    #     for node in ni():
    #         line = '    {id:'+str(node.ID)+', label: "'+node.base+'"'
    #         if node.ID in pathdict and count % 5 == 0:
    #             line += ', allowedToMoveX: false, x: ' + str(pathdict[node.ID]) + ', y: 0 , allowedToMoveY: true },'
    #         else:
    #             line += '},'
    #         lines.append(line)
    #
    #     lines[-1] = lines[-1][:-1]
    #     lines.append('];')
    #
    #     lines.append(' ')
    #
    #     lines.append('var edges = [')
    #     ni = self.nodeiterator()
    #     for node in ni():
    #         nodeID = str(node.ID)
    #         for edge in node.outEdges:
    #             target = str(edge)
    #             weight = str(len(node.outEdges[edge].labels)+1)
    #             lines.append('    {from: '+nodeID+', to: '+target+', value: '+weight+'},')
    #         for alignededge in node.alignedTo:
    #             # These edges indicate alignment to different bases, and are
    #             # undirected; thus make sure we only plot them once:
    #             if node.ID > alignededge:
    #                 continue
    #             target = str(alignededge)
    #             lines.append('    {from: '+nodeID+', to: '+target+', value: 1, style: "dash-line"},')
    #     lines[-1] = lines[-1][:-1]
    #     lines.append('];')
    #     return lines


cur = []

def dfs(u, g, done):
    global cur
    
    if u in done:
        return
    
    for v in g[u]:
        dfs(v, g, done)
    
    done.add(u)
    cur.append(u)

def topo(g):
    global cur
    
    n = len(g)
    done = set()
    
    ret = []
    for i in g:
        if i not in done:
            cur = []
            dfs(i, g, done)        
            ret += cur 
    
    return ret[::-1]

def graph_to_graph(g1, l1, g2, l2):
    
    print 'topo ',g1
    tg1 = topo(g1)
    print 'res:',tg1
    print '-'*50
    
    print 'topo ',g2
    tg2 = topo(g2)
    print 'res:',tg2
    print '-'*50
    
    dp = {i : {j : 0 for j in g2} for i in g1}
    
    pa = {i : {j : (-1,-1) for j in g2} for i in g1}
    
    for i in tg1:
        for j in tg2:
            
            for u in g1[i]:
                for v in g2[j]:
                    
                    if l1[u] == l2[v]:
                        if dp[u][v] < dp[i][j] + 1:
                            dp[u][v] = dp[i][j] + 1
                            pa[u][v] = (i,j)    
                    else:
                        if dp[u][v] < dp[i][j] - 2:
                            dp[u][v] = dp[i][j] - 2
                            pa[u][v] = (i,j)
                
                    if dp[u][j] < dp[i][j] - 1:
                        dp[u][j] = dp[i][j] - 1
                        pa[u][j] = (i,j)
                    
                    if dp[i][v] < dp[i][j] - 1:
                        dp[i][v] = dp[i][j] - 1
                        pa[i][v] = (i,j)
    
    newg, newl = g1.copy(), l1.copy()
    newg.update(g2)
    newl.update(l2)

    seen = set()
    done = set()
    for ep1 in tg1[::-1]:
        if ep1 in seen:
            continue
        
        ep2 = None
        for u in tg2[::-1]:
            if pa[ep1][u] != (-1,-1):
                ep2 = u
                break
        
        print 'start at',ep1, ep2-100 
        u = (ep1, ep2)
        while u != (-1,-1):
            if u in done:
                break
            
            done.add(u)
            seen.add(u[0])
            
            par = pa[u[0]][u[1]]
            
            if par[0] != -1 and par[0] != u[0] and par[1] != u[1]:
                print 'align',(u[0],u[1]-100)
                pass
                
            u = par
        print '-'*50
        
flr = 0

def seq_to_graph(s):
    global flr
    
    g = {}
    for i in range(len(s)-1):
        g[i+flr] = [i+1+flr]
    g[len(s)-1+flr] = []
    
    l = {}
    for i in range(len(s)):
        l[i+flr] = s[i]
    
    flr += len(s)

    return g,l


# s1 = 'SATCAAAGTC'
# g1,l1 = seq_to_graph(s1)
# s2 = 'STTCAAGTTG'
# g2,l2 = seq_to_graph(s2)

g1 = {i : {} for i in range(12)}
g1[0] = [1]
g1[1] = [2,8]
g1[2] = [3]
g1[3] = [4]
g1[4] = [5]
g1[5] = [6]
g1[6] = [7,11]
g1[7] = []
g1[8] = [9]
g1[9] = [10]
g1[10] = [4]
g1[11] = []

l1 = {i:['S','G','C','C','C','T','G','C','A','G','T','A'][i] for i in range(12)}

g2 = {i+100 : [] for i in range(13)}
g2[0+100] = [1+100]
g2[1+100] = [2+100]
g2[2+100] = [3+100,11+100]
g2[3+100] = [4+100]
g2[4+100] = [5+100]
g2[5+100] = [6+100]
g2[6+100] = [7+100,12+100]
g2[7+100] = [8+100]
g2[8+100] = [9+100]
g2[9+100] = [10+100]
g2[10+100] = []
g2[11+100] = [6+100]
g2[12+100] = [8+100]

l2 = {i+100:['S','G','A','G','A','T','C','T','G','T','A','C','A'][i] for i in range(13)}

print 'l1:',l1
print 'g1:',g1
print '-'*50

print 'l2:',l2
print 'g2:',g2
print '-'*50

graph_to_graph(g1,l1,g2,l2)

