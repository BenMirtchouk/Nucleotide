f = open("data/61_to_78__834_to_895.txt", "r")
# name, start, seq

seq = None
names = []
reads = []

l = f.readline()
while l:
    l = f.readline()[:-1]
    
    if seq == None:
        seq = l
    else:    
        reads.append(l)
    
    l = f.readline()
    
f.close()

# pairwise

score = (-1, 1, -2) # mismatch, match, indel
inf = 10**6
mb = 5 # max bonus

for read in reads:
    dp = [[[-inf] * (mb+1) for i in range(len(read) + 1)] for j in range(len(seq) + 1)]
    parent = [[[None] * (mb+1) for i in range(len(read) + 1)] for j in range(len(seq) + 1)]
    dp[0][0][0] = 0
    parent[0][0][0] = (0,0,0)
    # dp[i][j][k] score for i chars of seq, j chars of read, streak k
    
    for i in range(len(seq)+1):
        for j in range(len(read)+1):
            for k in range(mb+1):
                if parent[i][j] == None:
                    continue
                
                if i < len(seq) and dp[i+1][j][0] < dp[i][j][k] + score[2]:
                    dp[i+1][j][0] = dp[i][j][k] + score[2]
                    parent[i+1][j][0] = (i,j,k)
                
                if j < len(read) and dp[i][j+1][0] < dp[i][j][k] + score[2]:
                    dp[i][j+1][0] = dp[i][j][k] + score[2]
                    parent[i][j+1][0] = (i,j,k)
                
                if i < len(seq) - 1 and j < len(read) - 1:
                    if seq[i] == read[j]:
                        if dp[i+1][j+1][min(k+1, mb)] < dp[i][j][k] + score[1] + k:
                            dp[i+1][j+1][min(k+1, mb)] = dp[i][j][k] + score[1] + k
                            parent[i+1][j+1][min(k+1, mb)] = (i,j,k)
                    else:
                        if dp[i+1][j+1][0] < dp[i][j][k] + score[0]:
                            dp[i+1][j+1][0] = dp[i][j][k] + score[0]
                            parent[i+1][j+1][0] = (i,j,k)
    
    pos = (len(seq), len(read), 0)
    for i in range(1, mb+1):
        if dp[len(seq)][len(read)][i] > dp[len(seq)][len(read)][pos[2]]:
            pos[2] = i
    
    print dp[len(seq)][len(read)][pos[2]]
    
    nseq = ""
    nread = ""
    
    while pos != (0, 0, 0):
        par = parent[pos[0]][pos[1]][pos[2]]
        
        if par[0] + 1 == pos[0] and par[1] + 1 == pos[1]:
            nseq += seq[par[0]]
            nread += read[par[1]]
        elif par[0] + 1 == pos[0]:
            nseq += seq[par[0]]
            nread += "-"
        else:
            nseq += "-"
            nread += read[par[1]]
        
        pos = par
    
    print nseq[::-1]
    print nread[::-1], '\n\n'