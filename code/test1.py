from final import *

data = ''

############ graph 1 #############

g1 = Graph('SGATATGA','seq1')

############ graph 2 #############

g2 = Graph('SGACTCTCTA','seq2')

############ graph 3 #############

g3 = Graph(label='seq3')
l3 = 'SGCCCTGCAGTA'
for i in range(12):
    g3.addNode(l3[i])

g3.addEdge(0,1,'seq3')
g3.addEdge(1,2, 'seq3')
g3.addEdge(1,8, 'seq3')
g3.addEdge(2,3, 'seq3')
g3.addEdge(8,9, 'seq3')
g3.addEdge(9,10, 'seq3')
g3.addEdge(3,4, 'seq3')
g3.addEdge(10,4, 'seq3')
g3.addEdge(4,5, 'seq3')
g3.addEdge(5,6, 'seq3')
g3.addEdge(6,7, 'seq3')
g3.addEdge(6,11, 'seq3')

############ graph 4 #############

g4 = Graph(label='seq4')
l4 = 'SGAGATCTGTACA'

for i in range(13):
    g4.addNode(l4[i])

g4.addEdge(0,1, 'seq4')
g4.addEdge(1,2, 'seq4')
g4.addEdge(2,3, 'seq4')
g4.addEdge(2,11, 'seq4')
g4.addEdge(11,6, 'seq4')
g4.addEdge(3,4, 'seq4')
g4.addEdge(4,5, 'seq4')
g4.addEdge(5,6, 'seq4')
g4.addEdge(6,7, 'seq4')
g4.addEdge(6,12, 'seq4')
g4.addEdge(7,8, 'seq4')
g4.addEdge(12,8, 'seq4')
g4.addEdge(8,9, 'seq4')
g4.addEdge(9,10, 'seq4')

####### append graph html ########

data += g1.graphData()
data += g2.graphData()
data += g3.graphData()
data += g4.graphData()

########## align 1 & 2 ###########

Graph.align(g1,g2)
data += g1.graphData()

########## align 3 & 4 ###########

Graph.align(g3,g4)
data += g3.graphData()

####### align (1&2) & (3&4) ######

Graph.align(g1,g3)
data += g1.graphData()

######## generate html #########

doc = '''
<html>
    <head>
      <title>NuCLeOTidE</title>
      <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/vis/3.11.0/vis.min.js"></script>
    </head>
    <body>
        {0}
    </body>
</html>
'''.format(data)

print doc