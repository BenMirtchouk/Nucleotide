from Graph import *
from collections import deque

# initialize constants

inf = 10**4
score = {
    'match'    : +2,
    'mismatch' : -3,
    'indel'    : -2
}

class Aligner(object):
    def __init__(self, graph1, graph2):
        self.graph1 = graph1
        self.graph2 = graph2

    # if we have a new maximum, we update both the value and the self.parent, else nothing changes
    @staticmethod
    def max_with_parent(current_val, new_val, current_parent, new_parent):
        if new_val > current_val:
            return new_val, new_parent
        else:
            return current_val, current_parent
                
    def align(self):
        self.performDP()
        
        # init tracking variables
         
        self.seen1 = set()
        self.seen2 = set()
        self.seenContext = dict()
        self.alias = dict() # maps self.graph1 node numbers to self.graph2
        self.aligned = []
        self.alreadyAligned = set()
        
        self.traverseBack((self.graph1.nnodes, self.graph2.nnodes))
        
        unseen2 = self.topo2[::-1]
        # pick last unseen node from first graph
        for node1 in self.topo1[::-1]:
            if node1 in self.seen1:
                continue
            
            # select where in the self.dp array to start
            dp_index = None
            
            keep = []
            for i, node2 in enumerate(unseen2):
                if node2 not in self.seen2:
                    # check if potential dp_index has too low a score to be considered
                    best = -inf
                    for nbr1 in self.graph1.nodedict[node1].outEdges:
                        best = max(best, self.seenContext[nbr1])
                    if self.dp[node1][node2] < best - 2*score['match']: # maybe needs tweeking
                        keep.append(node2)
                        continue
                    
                    # set our newfound dp_index
                    dp_index = (node1, node2)
                    unseen2 = keep + unseen2[i+1:]
                    break
            
            if dp_index is None:
                break
            
            self.traverseBack(dp_index)
        
        self.encorporateAlignment()
        self.graph1._seqs += self.graph2._seqs
    
    def performDP(self):
        # self.dp[i][j] = best score to have self.aligned up to (and including) node id i in g1 and j in g2
        self.dp = [[-inf]*(self.graph2.nnodes+1) for i in range(self.graph1.nnodes+1)]
        
        # self.parent[i][j] = index into self.dp that led to the current best self.dp[i][j]
        self.parent = [[None]*(self.graph2.nnodes+1) for i in range(self.graph1.nnodes+1)]
        
        self.dp[0][0] = 0
        
        self.topo1 = self.graph1.topological_order()
        self.topo2 = self.graph2.topological_order()
        
        for node1 in self.topo1:
            for node2 in self.topo2:
                
                base1 = self.graph1.nodedict[node1].base
                base2 = self.graph2.nodedict[node2].base
                
                # insertion
                for nbr1 in self.graph1.nodedict[node1].outEdges:
                    self.dp[nbr1][node2], self.parent[nbr1][node2] = \
                        Aligner.max_with_parent(self.dp[nbr1][node2], self.dp[node1][node2] + score['indel'], \
                                                self.parent[nbr1][node2], (node1,node2) )
                
                # deletion
                for nbr2 in self.graph2.nodedict[node2].outEdges:
                    self.dp[node1][nbr2], self.parent[node1][nbr2] = \
                        Aligner.max_with_parent(self.dp[node1][nbr2], self.dp[node1][node2] + score['indel'], \
                                                self.parent[node1][nbr2], (node1,node2) )
                    
                # alignment
                for nbr1 in self.graph1.nodedict[node1].outEdges:
                    for nbr2 in self.graph2.nodedict[node2].outEdges:
                        self.dp[nbr1][nbr2], self.parent[nbr1][nbr2] = \
                            Aligner.max_with_parent(self.dp[nbr1][nbr2], self.dp[node1][node2] + (score['match'] if base1 == base2 else score['mismatch']), \
                                                    self.parent[nbr1][nbr2], (node1,node2) )
                
                # end alignment
                if len(self.graph1.nodedict[node1].outEdges) == 0 and len(self.graph2.nodedict[node2].outEdges) == 0:
                    self.dp[self.graph1.nnodes][self.graph2.nnodes], self.parent[self.graph1.nnodes][self.graph2.nnodes] = \
                        Aligner.max_with_parent(self.dp[self.graph1.nnodes][self.graph2.nnodes], self.dp[node1][node2] + (score['match'] if base1 == base2 else score['mismatch']), \
                                                self.parent[self.graph1.nnodes][self.graph2.nnodes], (node1,node2) )
                        
                    self.dp[self.graph1.nnodes][self.graph2.nnodes], self.parent[self.graph1.nnodes][self.graph2.nnodes] = \
                        Aligner.max_with_parent(self.dp[self.graph1.nnodes][self.graph2.nnodes], self.dp[node1][node2] + 2*score['indel'], \
                                                self.parent[self.graph1.nnodes][self.graph2.nnodes], (node1,node2) )
    
    # once we have an alignment score matrix (self.dp, self.parent), find which nodes need to be aligned starting at dp_index (and update [alias, aligned] accordingly)
    def traverseBack(self, dp_index):
        self.seen1_updt = set()
        self.seen2_updt = set()
        
        # move backwards through the self.parent chain in self.dp
        while dp_index != None:
            if dp_index[0] in self.seen1 or dp_index[1] in self.seen2:
                break
            
            self.seen1_updt.add(dp_index[0])
            self.seen2_updt.add(dp_index[1])
            
            if dp_index[0] not in self.seenContext:
                self.seenContext[dp_index[0]] = self.dp[dp_index[0]][dp_index[1]]
            else:
                self.seenContext[dp_index[0]] = max(self.seenContext[dp_index[0]], self.dp[dp_index[0]][dp_index[1]])
            
            self.parent_index = self.parent[dp_index[0]][dp_index[1]]
            
            # if both indicies changed we have alignment
            if self.parent_index != None and self.parent_index[0] != dp_index[0] and self.parent_index[1] != dp_index[1]:
                n1 = self.graph1.nodedict[ self.parent_index[0] ]
                n2 = self.graph2.nodedict[ self.parent_index[1] ]
                
                # make sure aligning n1/n2 does not break acyclic-ness
                
                    
                # print '\talign',n1.ID,n2.ID
                if n1.base == n2.base:
                    self.alias[ n2.ID ] = n1.ID
                else:
                    self.aligned.append( (n1.ID, n2.ID) )
                
            dp_index = self.parent_index
        
        self.seen1 |= self.seen1_updt
        self.seen2 |= self.seen2_updt
    
    def encorporateAlignment(self):
        for nodeID in self.graph2.nodeidlist:
            if nodeID not in self.alias:
                nd = self.graph2.nodedict[ nodeID ]
                self.alias[nodeID] = self.graph1.addNode(nd.base)
        
        for nodeID in self.graph2.nodeidlist:
            nd2 = self.graph2.nodedict[ nodeID ]
            nd1 = self.graph1.nodedict[ self.alias[nodeID] ]
            
            for outNodeID in nd2.outEdges:
                ####
                if outNodeID not in self.alias:
                    print 'hmm something wrong'
                    print outNodeID
                    print self.alias
                    print self.graph2.nodedict
                    exit(0)
                
                # don't connect to self
                if self.alias[nodeID] != self.alias[outNodeID]:
                    self.graph1.addEdge(self.alias[nodeID], self.alias[outNodeID], nd2.outEdges[outNodeID].agreements)
            
            for alignedID in nd2.alignedTo: 
                # don't align to self
                if self.alias[nodeID] != self.alias[alignedID]:
                    self.graph1.align_nodes(self.alias[nodeID], self.alias[alignedID], nd2.alignedTo[alignedID].agreements)
                
        
        for n1ID, n2ID in self.aligned:
            # don't align to self
            if n1ID != self.alias[n2ID]:
                self.graph1.align_nodes(n1ID, self.alias[n2ID], 1)
    