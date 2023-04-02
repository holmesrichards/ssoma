import json

def main():
    with open ("xx.json", "r") as f:
        s = json.load (f)

    d2 = []
    for si in s:
        d = {"W": 0, "Y": 0, "G": 0, "O": 0, "L": 0, "R": 0, "B": 0}
        for p in si:
            for r in p:
                for c in r:
                    cl = c.upper()
                    if cl != '.':
                        d[cl] += 1
        p = ""
        q = ""
        for k in sorted(d.keys()):
            if d[k] > 4:
                p += k
            elif d[k] == 0:
                q += k
        if [p, q] not in d2:
            d2.append([p, q])

    o = []
    for d2i in d2:
        o.append(" ".join(d2i))
    
    for oi in sorted(o):
        print (oi)
        
main()
