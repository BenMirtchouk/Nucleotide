# Node, Edge, and Graph objects are based off of POA py
# These objects will be used to implement our Graph-to-Graph algorithm

class Node(object):
    def __init__(self, nodeID=-1, base='N'):
        self.ID = nodeID
        self.base = base
        self.outEdges = []
        self.alignedTo = []

    def __str__(self):
        return "(%d:%s)" % (self.ID, self.base) 


class Edge(object):
    def __init__(self, inNodeID=-1, outNodeID=-1, label=None):
        self.inNodeID  = inNodeID
        self.outNodeID = outNodeID
        
    def __str__(self):
        nodestr = "(%d) -> (%d) " % (self.inNodeID, self.outNodeID)
        return nodestr
    
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

cur = []

def dfs(u, graph, visited): # depth first search
    global cur
    
    if u in visited:
        return
    
    for v in graph[u]:
        dfs(v, graph, visited)
    
    visited.add(u)
    cur.append(u)

def topo(graph):
    global cur
    
    visited = set()
    
    ret = []
    for i in graph:
        if i not in visited:
            cur = []
            dfs(i, graph, visited)        
            ret += cur 
    
    return ret[::-1]

def graph_to_graph(graph1, l1, graph2, l2): # graph to graph alignment! 
    
    print 'topo ',graph1
    tg1 = topo(graph1) #topologically sorted graph1
    print 'res:',graph1
    print '-'*50
    
    print 'topo ',graph2
    tg2 = topo(graph2) #topologically sorted graph2
    print 'res:',tg2
    print '-'*50
    
    dp = {i : {j : 0 for j in graph2} for i in graph1}
    
    parent = {i : {j : (-1,-1) for j in graph2} for i in graph1}
    
    for node_tg1 in tg1:
        for node_tg2 in tg2:
            
            for node_g1 in graph1[i]:
                for node_g2 in graph2[node_tg2]:
                    
                    if l1[node_g1] == l2[node_g2]:
                        if dp[node_g1][node_g2] < dp[node_tg1][node_tg2] + 1:
                            dp[node_g1][node_g2] = dp[node_tg1][node_tg2] + 1
                            parent[node_g1][node_g2] = (node_tg1, node_tg2)    
                    else:
                        if dp[node_g1][node_g2] < dp[node_tg1][node_tg2] - 2:
                            dp[node_g1][node_g2] = dp[node_tg1][node_tg2] - 2
                            parent[node_g1][node_g2] = (node_tg1, node_tg2)
                
                    if dp[node_g1][node_tg2] < dp[node_tg1][node_tg2] - 1:
                        dp[node_g1][node_tg2] = dp[node_tg1][node_tg2] - 1
                        parent[node_g1][node_tg2] = (node_tg1,node_tg2)
                    
                    if dp[node_tg1][node_g2] < dp[node_tg1][node_tg2] - 1:
                        dp[node_tg1][node_g2] = dp[node_tg1][node_tg2] - 1
                        parent[node_tg1][node_g2] = (node_tg1,node_tg2)
    
    new_graph, newl = graph1.copy(), l1.copy()
    new_graph.update(graph2)
    newl.update(l2)

    seen = set()
    done = set()
    for ep1 in tg1[::-1]:
        if ep1 in seen:
            continue
        
        ep2 = None
        for u in tg2[::-1]:
            if parent[ep1][u] != (-1,-1):
                ep2 = u
                break
        
        print 'start at',ep1, ep2-100 
        u = (ep1, ep2)
        while u != (-1,-1):
            if u in done:
                break
            
            done.add(u)
            seen.add(u[0])
            
            par = parent[u[0]][u[1]]
            
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

