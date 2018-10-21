def pairwise_seq_seq(s1, s2):
	# Needleman-Wulsh

def pairwise_seq_graph(s1, s2):
	# sequence to graph alignment as in POA

def pairwise_graph_graph(s1, s2):
	# we need to design our own
	
	# most simple idea is trace all deg(u)^2 paths but as degree
	# grows quite large (can be 20-50) we will need to design a 
	# more efficient mechanism
	
def align(s1, s2):
	if s1 is seq 
		if s2 is seq:
			return pairwise_seq_seq(s1,s2)
		else
			return pairwise_seq_graph(s1,s2)
	else
		if s2 is seq:
			return pairwise_seq_graph(s2,s1)
		else
			return pairwise_graph_graph(s1,s2)
	
def fill(seqs):
	scores = []
	for i in range(len(seqs)):
		for j in range(len(seqs)):
			if i == j:
				continue
			
			pts = align(seqs[s1], seqs[s2])
			heapq.push(scores, (pts, i, j))
	
	return scores
	
def pop_best(scores):
	return heapq.pop(scores)[1:]
	
def clear(scores, a):
	for e in scores:
		if e[1] in a or e[2] in a:
			scores.remove(e) # not a real thing
	
def update(scores, seq, seqs):
	for s in seqs:
		pts = align(seq, s)
		heapq.push(scores, (pts, seq, s)) # indicies or sequences?
		
def alignment(seqs): # all sequences 
	
	alignment_scores = fill(seqs) # pairwise align all sequences
	
	remaining = seqs
	while len(remaining) > 1:
		s1, s2 = pop_best(alignment_scores) # indicies or sequences?
		clear(alignment_scores, [s1, s2])
		
		remaining.remove(s1)
		remaining.remove(s2)
		
		aligned = align(s1, s2)
		
		update(scores, aligned, remaining)
		
		remaining.append(aligned)
	
	return seqs[0]