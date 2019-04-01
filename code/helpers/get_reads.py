def intersect(a, b):
    return (max(a[0], b[0]), min(a[1], b[1]))

def get_int(i, s):
    ret = 0
    while i < len(s) and s[i].isdigit():
        ret = ret*10 + int(s[i])
        i += 1
    return ret, i

rng = (500, 1500)

o = open('../data/61_to_78__' + str(rng[0]) + '_to_' + str(rng[1]) + '.txt', 'w')
f = open('../data/MSSA_78_1720493_1789360.fa', 'r')

f.readline()
reference = ''.join(f.readlines()).replace('\n','')[rng[0]: rng[1] + 1]
print reference
o.write('>seq\n' + reference + '\n')
f.close()

f = open('../data/61_to_78.txt', 'r')

l = f.readline()

display_alignment = False

while l:
    spl = l.split()
    l = f.readline()
    
    # BAM format
    name = spl[0]
    pos = spl[3]
    cigar = spl[5]
    seq = spl[9]
    
    pos = int(pos) - 1 # 0 index
    
    if pos > rng[0]:
        continue
    
    seq_idx = pos
    ref_idx = pos
    cigar_idx = 0
    
    aligned = ''
    
    while cigar_idx < len(cigar):
        q, cigar_idx = get_int(cigar_idx, cigar)
        ch = cigar[cigar_idx]
        
        # print q, ch
        
        if ch == 'M':
            inter = intersect((ref_idx, ref_idx + q - 1), rng)
            if inter[0] <= inter[1]:
                aligned += seq[seq_idx + (inter[0] - ref_idx) : seq_idx + (inter[1] - ref_idx) + 1]
            
            seq_idx += q
            ref_idx += q
        elif ch == 'D':
            if display_alignment:
                inter = intersect((ref_idx, ref_idx + q - 1), rng)
                if inter[0] <= inter[1]:
                    aligned += '-' * (inter[1] - inter[0] + 1)
            
            ref_idx += q
        elif ch == 'I':
            if not display_alignment:
                inter = intersect((ref_idx, ref_idx + q - 1), rng)
                if inter[0] <= inter[1]:
                    aligned += seq[seq_idx + (inter[0] - ref_idx) : seq_idx + (inter[1] - ref_idx) + 1]
                
            seq_idx += q
        else:
            print 'ohno', ch
            exit(-1)
        
        cigar_idx += 1
    
    if len(aligned) >= (rng[1] - rng[0] + 1) // 2:
        o.write('>' + name.split('/')[-1] + '\n')
        o.write(aligned + '\n')
        print aligned

f.close()
o.close()