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

