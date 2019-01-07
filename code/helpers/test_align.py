read = 'ATCAAAGTC'
seq =  'TTCAAGTTG'
inf = 10**9
score = (-2,1,-1)
mb = 0
        
dp = [[-inf for i in range(len(read) + 1)] for j in range(len(seq) + 1)]
parent = [[None for i in range(len(read) + 1)] for j in range(len(seq) + 1)]
dp[0][0] = 0
parent[0][0] = (0,0,0)

for i in range(len(seq) + 1):
    for j in range(len(read) + 1):
        if parent[i][j] == None:
            continue
        
        if i < len(seq) and dp[i + 1][j] < dp[i][j] + score[2]:
            dp[i + 1][j] = dp[i][j] + score[2]
            parent[i + 1][j] = (i,j)
        
        if j < len(read) and dp[i][j + 1] < dp[i][j] + score[2]:
            dp[i][j + 1] = dp[i][j] + score[2]
            parent[i][j + 1] = (i,j)
        
        if i < len(seq) - 1 and j < len(read) - 1:
            if seq[i] == read[j]:
                if dp[i + 1][j + 1] < dp[i][j] + score[1]:
                    dp[i + 1][j + 1] = dp[i][j] + score[1]
                    parent[i + 1][j + 1] = (i,j)
            else:
                if dp[i + 1][j + 1] < dp[i][j] + score[0]:
                    dp[i + 1][j + 1] = dp[i][j] + score[0]
                    parent[i + 1][j + 1] = (i,j)

pos = (len(seq), len(read))

#print dp[len(seq)][len(read)][pos[2]]

nseq = ''
nread = ''

while pos != (0, 0):
    print pos
    par = parent[pos[0]][pos[1]]
    
    if par[0] + 1 == pos[0] and par[1] + 1 == pos[1]:
        nseq += seq[par[0]]
        nread += read[par[1]]
    elif par[0] + 1 == pos[0]:
        nseq += seq[par[0]]
        nread += '-'
    else:
        nseq += '-'
        nread += read[par[1]]
    
    pos = par

#print nseq[::-1]
#print nread[::-1], '\n\n'

print nseq[::-1]
print nread[::-1]