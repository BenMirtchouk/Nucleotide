import os

snv = [842, 848, 854, 872, 875, 878, 884, 887]
cor = ['T', 'A', 'A', 'T', 'G', 'G', 'A', 'G']
    
files = os.listdir("../alignments")
for name in files:
    f = open("../alignments/" + name, "r")

    correct = 0
    reads = 0
    offset = int(name.split("_")[4])

    if "pairwise" in name:
        seq = f.readline()
        while seq:
            reads += 1
            seq = seq[:-1]
            read = f.readline()[:-1]
            nl = f.readline()
            
            idx = 0
            sp = 0
            
            for sp in range(len(snv)):
                if snv[sp] - offset - 1 >= 0:
                    break
            
            for i in range(len(seq)):
                if seq[i] == '-': 
                    continue
                
                if sp < len(snv) and idx == (snv[sp] - offset - 1):
                    if read[i] == cor[sp]:
                        correct += 1
                    
                    sp += 1
                
                idx += 1
            
            seq = f.readline()    
    else:
        
        seq = f.readline().split()[1][:-1]
        l = f.readline()
        while l:
            reads += 1
            read = l.split()[1][:-1]
            l = f.readline()
            
            idx = 0
            sp = 0
            
            # for sp in range(len(snv)):
            #     if snv[sp] - offset - 1 >= 0:
            #         break
            
            for i in range(len(seq)):
                if seq[i] == '-': 
                    continue
                
                if sp < len(snv) and idx == (snv[sp] - offset - 1):
                    if read[i] == cor[sp]:
                        correct += 1
                    
                    sp += 1
                
                idx += 1    
        
        
    print "%s: %.3f / %d" % (name, 1.0 * correct / reads, len(snv))
    f.close()