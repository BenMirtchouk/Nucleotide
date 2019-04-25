from Graph import *
from Aligner import *
import sys
from math import log, ceil

if len(sys.argv) < 3:
    print 'usage: ./test_real_reads.py {number of reads} {file} [-v]'
    exit(0)

seqs = []
f = open(sys.argv[2],"r")
for i in range(100):
    name,seq = f.readline(),f.readline()
    seqs.append(Graph(seq, name[1:]))
  
verbose = len(sys.argv) > 3 and sys.argv[3] == '-v'
  
data = ''

n_seqs = int(sys.argv[1])
n_seqs = min(n_seqs, len(seqs))

n = int(ceil(log(n_seqs,2)))

for i in range(1,n+1):
    for j in range(0, 1<<n, 1<<i):
        if j+(1<<(i-1)) >= n_seqs:
            break
        
        print 'aligning',j,j+(1<<(i-1))
        
        align = Aligner(seqs[j], seqs[ j+(1<<(i-1)) ])
        align.align()


# print seqs[0]
print seqs[0].alignmentOutput(verbose=verbose)
seqs[0].gephiOutput()
data += seqs[0].graphData()
######## generate html #########

doc = '''
<html>
    <head>
      <title>NuCLeOTidE</title>
      <script type="text/javascript" src="visjs/vis.js"></script>
      <link href="visjs/visnetwork.min.css" rel="stylesheet" type="text/css"/>
    </head>
    <body>
        {0}
    </body>
</html>
'''.format(data)

with open('out.html','w') as f:
    f.write(doc)