import os

files = os.listdir("alignments")
for name in files:
    f = open("alignments/" + name, "r")

    snv = [842, 848, 854, 872, 875, 878, 884, 887]
    cor = ['T', 'A', 'A', 'T', 'G', 'G', 'A', 'G']
    for i in range(len(snv)):
        snv[i] -= 775

    correct = 0
    reads = 0

    if "pairwise" in name:
        score = f.readline()
        while score:
            reads += 1
            seq = f.readline()[:-1]
            read = f.readline()[:-1]
            n = f.readline()
            n = f.readline()
            score = f.readline()
            
            idx = 0
            sp = 0
            for i in range(len(seq)):
                if seq[i] == '-': 
                    continue
                
                if sp < len(snv) and idx == snv[sp]:
                    if read[i] == cor[sp]:
                        correct += 1
                    
                    sp += 1
                
                idx += 1    
    else:
        seq = f.readline().split()[1]
        l = f.readline()
        while l:
            reads += 1
            read = l.split()[1]
            l = f.readline()
            
            idx = 0
            sp = 0
            for i in range(len(seq)):
                if seq[i] == '-': 
                    continue
                
                if sp < len(snv) and idx == snv[sp]:
                    if read[i] == cor[sp]:
                        correct += 1
                    
                    sp += 1
                
                idx += 1    
        
        
    print "%s: %.3f / %d" % (name, 1.0 * correct / reads, len(snv))
    f.close()