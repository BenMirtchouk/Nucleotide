def intersect(a, b):
    return (max(a[0], b[0]), min(a[1], b[1]))

rng = (834, 895)

o = open("data/61_to_78__"+str(rng[0])+"_to_"+str(rng[1])+".txt", "w")
f = open("data/MSSA_78_1720493_1789360.fa", "r")

f.readline()
o.write(">seq\n" + "".join(f.readlines()).replace("\n","")[rng[0] - 60 : rng[1] + 60 + 1] + "\n")
f.close()

f = open("data/61_to_78_parsed.txt", "r")
#name, start, seq
l = f.readline()

while l:
    spl = l.split()
    st = int(spl[1])
    ln = len(spl[2])

    inter = intersect((rng[0] - 10, rng[1] + 10), (st, st+ln-1))
    if inter[0] <= inter[1] and inter[1] - inter[0] + 1 > 30:
        o.write(">" + spl[0].split("/")[-1] + "\n" + spl[2][inter[0] - st : inter[1] - st + 1] + "\n")
    
    l = f.readline()

f.close()
o.close()