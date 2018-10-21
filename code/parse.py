#samtools-1.9/samtools view mapping_bias_IGV/map_MSSA_61_to_MSSA_78_1720493_1789360.bam > 61_to_78.txt

f = open("data/61_to_78.txt", "r")
o = open("data/61_to_78_parsed.txt", "w")

l = f.readline()
while l:
    l = l.split()
    o.write(l[0] + " " + str(int(l[3]) - 1) + " " + l[9] + "\n")
    l = f.readline()

f.close()
o.close()
