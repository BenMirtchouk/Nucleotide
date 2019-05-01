from Graph import *
from Aligner import *
import sys
from math import log, ceil
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('n_seqs', type=int, help="number of reads")
ap.add_argument('file', help="path to file")
ap.add_argument('--verbose', '-v', action='store_true', help="toggle verbosity")
args = vars(ap.parse_args())

seqs = []
f = open(args['file'], "r")
for i in range(100):
    name,seq = f.readline(),f.readline()
    seqs.append(Graph(seq, name[1:]))

verbose = args['verbose']

data = ''

n_seqs = args['n_seqs']
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
