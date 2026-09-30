"""Kiểm tra & hiệu chỉnh tọa độ đọc từ bản scan bằng cột 'Cạnh (m)' của chính bản vẽ.
Mỗi mốc: thử thay các chữ số dễ nhầm, chọn cách đọc làm khớp nhất 2 cạnh kề."""
import math, itertools
from coords import P1, P2, area

E1 = [19.61,28.89,24.87,11.61,41.80,23.80,24.62,0.43,14.10,11.76,10.11,9.16,2.10,49.80,11.17,4.80,9.18,3.80,8.19,12.00,
      1.77,1.60,1.41,1.16,2.77,3.39,3.08,2.05,3.51,1.56,1.02,0.90,15.62,8.43,10.50,2.70,33.68,36.70,20.97,46.95]
E2 = [7.13,10.23,None,None,29.51,6.02,98.79,0.42,5.25,3.80,8.19,12.00,1.77,1.60,1.41,1.16,2.77,3.39,3.08,2.05,3.51,1.56,
      1.03,0.90,15.62,8.43,19.44,16.71,36.70,20.97,2.70,24.41,41.56]
CONF = {'0':'0689','1':'17','2':'237','3':'3582','4':'41','5':'53689','6':'6580','7':'712','8':'836905','9':'98503'}

def variants(v):
    s = f"{v:.2f}"            # e.g. 903.26 (phần lẻ sau 1190xxx / 590xxx)
    idx = [i for i,c in enumerate(s) if c.isdigit()][-4:]   # 4 chữ số cuối (đơn vị m và 2 số thập phân + hàng chục)
    out = {v}
    for i in idx:
        for c in CONF[s[i]]:
            t = s[:i]+c+s[i+1:]
            out.add(float(t))
    return out

def err(P, E, i):
    n=len(P); e=0
    for j in (i-1, i):
        a,b = P[j%n], P[(j+1)%n]; L=E[j%n]
        if L is None: continue
        e += (math.dist(a,b)-L)**2
    return e

def fix(P, E, locked=()):
    P=list(P); changes=[]
    for _ in range(3):
        for i in range(len(P)):
            if i in locked: continue
            best=(err(P,E,i),P[i])
            for x in variants(P[i][0]):
                for y in variants(P[i][1]):
                    Q=P[:]; Q[i]=(x,y); e=err(Q,E,i)
                    if e < best[0]-1e-6 and (abs(x-P[i][0])>0 or abs(y-P[i][1])>0): best=(e,(x,y))
            if best[1]!=P[i]:
                changes.append((i+1,P[i],best[1])); P[i]=best[1]
    return P, changes

def report(name,P,E):
    n=len(P); bad=[]
    for j in range(n):
        if E[j] is None: continue
        d=math.dist(P[j],P[(j+1)%n])
        if abs(d-E[j])>0.05: bad.append((j+1,(j+1)%n+1,round(d,2),E[j]))
    print(name,"area",round(area(P),1),"| cạnh lệch >5cm:",bad)

if __name__=="__main__":
    report("P1 gốc",P1,E1)
    Q1,c1=fix(P1,E1); print("P1 hiệu chỉnh:",c1); report("P1 mới",Q1,E1)
    P2x=list(P2); P2x[3]=(921.17,384.30)
    report("P2 gốc",P2x,E2)
    Q2,c2=fix(P2x,E2,locked=(2,3,4)); print("P2 hiệu chỉnh:",c2); report("P2 mới",Q2,E2)
