from Graph import *
from Aligner import *
import sys
from math import log, ceil

seqs_834 = [    
    # Graph('XAAAAAAAAAAX', 'seq'),
    Graph('XTTTGGGGTTTX', '0_12775'),
    Graph('XTTTTTTTTTTX', '0_1960')
    # Graph('XAAAGGGGAAAX', '0_9431')
]

seqs = seqs_834
data = ''

############# debug ###############

# n_seqs = int(sys.argv[1]) if len(sys.argv) >= 2 else 2
# n_seqs = min(n_seqs, len(seqs))

# n = int(ceil(log(n_seqs,2)))

# for i in range(1,n+1):
#     for j in range(0, 1<<n, 1<<i):
#         if j+(1<<(i-1)) >= n_seqs:
#             break
        
#         print 'aligning',j,j+(1<<(i-1))
        
#         align = Aligner(seqs[ j ],seqs[ j+(1<<(i-1)) ])
#         align.align()
    

align = Aligner(seqs[0],seqs[1])
align.align()
data += seqs[0].graphData(arrows=True, vertical=True)
print '01'*50
print seqs[0]
print '01'*50


align = Aligner(seqs[2],seqs[3])
align.align()
data += seqs[2].graphData(arrows=True, vertical=True)
print '23'*50
print seqs[2]
print '23'*50


align = Aligner(seqs[0],seqs[2])
align.align()
data += seqs[0].graphData(arrows=True, vertical=True)
print '**'*50
print seqs[0]
print '**'*50

# data += seqs[16].graphData(useConsensus=False, arrows=True)


doc = '''
<html>
    <head>
      <title>NuCLeOTidE</title>
      <script type="text/javascript" src="visjs/vis.js"></script>
      <link href="visjs/visnetwork.min.css" rel="stylesheet" type="text/css"/>
    </head>
    <body>
        <style>
        div{{
            display: table-cell;
            width: 38%;
            height: 600px;
        }};
        </style>
        {0}
        <script>
            window.onload = function() {{
                document.getElementsByTagName('canvas')[0].height=1000;
                document.getElementsByTagName('canvas')[1].height=1000;
                document.getElementsByTagName('canvas')[2].height=1000;
            }};
        </script>
    </body>
</html>
'''.format(data)

with open('out_verbose.html','w') as f:
    f.write(doc)

########### end debug #############