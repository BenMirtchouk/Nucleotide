import sys
import argparse

INF = 10**5

parser = argparse.ArgumentParser()
parser.add_argument('infile', type=argparse.FileType('r'), default=sys.stdin, help='alignment input file')
parser.add_argument('-sam', type=argparse.FileType('w'), help='sam output file name')
parser.add_argument('-fasta', type=argparse.FileType('w'), help='fasta output file name')
parser.add_argument('--ref', type=str, default='seq', help='name of reference read (default=\'seq\'')
args = parser.parse_args()

ref = args.ref

raw = [l.split() for l in args.infile.read().split('\n') if l]
seqs = {name: alignment for name, alignment in raw}

args.fasta.write('>' + ref + '\n' + seqs[ref].replace('-', '') + '\n')
args.fasta.close()

for name in seqs:
    if name == ref:
        continue
    
    CIGAR_v = ''
    POS = INF
    dist = 1 # how deep in the reference
    
    for i in range(len(seqs[ref])):
        refc, myc = seqs[ref][i], seqs[name][i]
        
        if refc == '-' and myc == '-':
            continue
            
        if POS == INF:
            POS = dist
        
        if refc == '-':
            CIGAR_v += 'I'
        elif myc == '-':
            CIGAR_v += 'D'
            dist += 1
        else:
            CIGAR_v += 'M'
            dist += 1
        
    CIGAR = ''
    prev = CIGAR_v[0]
    cnt = 1
    for c in CIGAR_v[1:] + ' ':
        if c == prev:
            cnt += 1
        else:
            CIGAR += str(cnt) + prev
            prev = c
            cnt = 1
    
    QNAME = name
    FLAG  = 16 # unimportant
    RNAME = ref
    POS   = POS
    MAPQ  = 42 # unimportant
    CIGAR = CIGAR
    RNEXT = '*' # unimportant
    PNEXT = 0 # unimportant
    TLEN  = len(seqs[name].replace('-', ''))
    SEQ   = seqs[name].replace('-', '')
    QUAL  = '2' * TLEN # unimportant
    
    samstr = '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}'.format(QNAME, FLAG, RNAME, POS, MAPQ, CIGAR, RNEXT, PNEXT, TLEN, SEQ, QUAL)
    
    args.sam.write(samstr + '\n')
