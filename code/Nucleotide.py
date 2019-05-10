from Graph import *
from Aligner import *

import sys
from math import log, ceil
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('infile', type=argparse.FileType('r'), default=sys.stdin, help='seq input file')
parser.add_argument('-v', '--verbosity', type=int, default=0, help='increase output verbosity')
parser.add_argument('-n', '--nseqs', type=int, default=-1, help='number of seqs to align, default=all')
# TODO:
# parser.add_argument('-G', '--gap', type=int, default=-1, help='Gap penalty, default=-1')
# parser.add_argument('-g', '--globalAlign', action='store_true', help='Global alignment (default: local)')
# parser.add_argument('-s', '--simple', action='store_true', help='Simple method')
# parser.add_argument('-m', '--match', type=int, default=1, help='Match score, default=+1')
# parser.add_argument('-M', '--mismatch', type=int, default=-1, help='Mismatch score, default=-1')
parser.add_argument('--html', type=argparse.FileType('w'), help='html output')
parser.add_argument('--gephi', type=argparse.FileType('w'), help='gephi output')
args = parser.parse_args()

n = args.nseqs
raw_seqs = []
seqs = []
while len(seqs) <= n or n == -1:
    name, seq = args.infile.readline(), args.infile.readline()
    if not name or not seq:
        break
    raw_seqs.append({'seq': seq[:-1], 'name': name[1:-1]})
    seqs.append(Graph(seq=seq[:-1], name=name[1:-1]))

if n == -1:
    n = len(seqs)

for i in range(1, n):
    if args.verbosity >= 1:
        print 'aligning', 0, i
    align = Aligner(seqs[0], seqs[i])
    align.align()


if args.verbosity >= 5:
    print seqs[0]

# lg = int(ceil(log(n,2)))
# for i in range(1,lg+1):
#     for j in range(0, 1<<lg, 1<<i):
#         if j+(1<<(i-1)) >= n:
#             break
        
#         print 'aligning',j,j+(1<<(i-1))
        
#         align = Aligner(seqs[j], seqs[ j+(1<<(i-1)) ])
#         align.align()

trace = sorted(seqs[0].trace_seqs(), key=lambda v:v[0])
max_name_len = max(len(name) for name, align_str in trace)
for name, align_str in trace:
    print name + ' '*(max_name_len-len(name)) + '   ' + align_str

if args.html:
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
    '''.format(seqs[0].graphData())

    args.html.write(doc)
if args.gephi:
    args.gephi.write(seqs[0].gephiOutput())
    