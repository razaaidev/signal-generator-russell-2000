import numpy as np, pandas as pd
rng = np.random.default_rng(31)
R  = pd.read_pickle("rets_clean.pkl"); ANN = pd.read_pickle("annvol_clean.pkl")
C  = np.array(R.columns); sel = C[(ANN.reindex(C).values > 0.35)]
D  = R[sel].dropna(how="any")
U  = np.exp(D.values) - 1.0
LV = np.cumprod(1+U, axis=0)                      # price levels, for real SMA20
SMA20 = pd.DataFrame(LV).rolling(20).mean().values
sig = np.mean(U.std(axis=0)); RT = 0.006; NDAYS = 21
print(f"cohort {U.shape[1]} names | daily sigma {sig:.2%} | ann {sig*np.sqrt(252):.1%}\n")

def run(p, k, H, use20, risk, maxpos, nsim=15000):
    stop = k*sig
    out=np.empty(nsim); so=tw=tr=0
    for s in range(nsim):
        t0 = rng.integers(40, len(U)-NDAYS-H-1)
        cash=acct=100.0; pos=[]; pool=0
        cols = rng.integers(0, U.shape[1], size=maxpos*10)
        for d in range(NDAYS):
            i = t0+d; keep=[]
            for q in pos:
                q['cum']=(1+q['cum'])*(1+U[i,q['c']])-1; q['age']+=1
                ex=False
                if q['cum']<=-stop: ex=True; so+=1
                elif use20 and LV[i,q['c']] < SMA20[i,q['c']]: ex=True; tw+=1
                elif q['age']>=H: ex=True
                if ex: cash += q['sz']*(1+q['cum'])*(1-RT/2)
                else: keep.append(q)
            pos=keep
            acct = cash + sum(q['sz']*(1+q['cum']) for q in pos)
            while len(pos)<maxpos and d<=NDAYS-2:
                sz=min(risk*acct/stop, 0.25*acct, cash)
                if sz<1.0: break
                c=cols[pool%len(cols)]; pool+=1
                if use20 and not (LV[i,c] > SMA20[i,c]): pool+=0; 
                fwd=np.prod(1+U[i:i+H,c])-1
                if (fwd>0)!=(rng.random()<p): continue
                cash-=sz; tr+=1
                pos.append(dict(c=c,cum=0.0,age=0,sz=sz*(1-RT/2)))
        out[s]=cash+sum(q['sz']*(1+q['cum']) for q in pos)
    return out, stop, so/max(tr,1), tw/max(tr,1), tr/nsim

print("SIZING SWEEP — 3.0 sigma stop, 21-day max hold, 55% hit rate")
print(f"{'risk':>6} {'pos':>4} {'size%':>7} {'median':>9} {'P(BE)':>7} {'P>=110':>8} {'P>=120':>8} {'P<=90':>7} {'P<=75':>7}")
for risk in (0.02, 0.03, 0.05, 0.08):
    for mp in (4, 5):
        f, st, so, tw, nt = run(0.55, 3.0, 21, False, risk, mp)
        print(f"{risk:>5.0%} {mp:>4} {min(risk/st,0.25):>6.1%} £{np.median(f):>8.2f} {np.mean(f>=100):>6.1%} "
              f"{np.mean(f>=110):>7.1%} {np.mean(f>=120):>7.1%} {np.mean(f<=90):>6.1%} {np.mean(f<=75):>6.1%}")

print("\nEXIT RULE COMPARISON — 5% risk, 4 positions, 55% hit rate")
print(f"{'rule':<34} {'median':>9} {'P(BE)':>7} {'P>=110':>8} {'P<=90':>7} {'stop-exit':>10} {'20d-exit':>9} {'trades':>7}")
for lbl,k,H,u20 in (("3.0s stop only, 21d cap",3.0,21,False),
                    ("3.0s stop + close<20d SMA",3.0,21,True),
                    ("2.5s stop + close<20d SMA",2.5,21,True),
                    ("4.0s stop + close<20d SMA",4.0,21,True),
                    ("close<20d SMA only (wide 6s)",6.0,21,True)):
    f,st,so,tw,nt = run(0.55,k,H,u20,0.05,4)
    print(f"{lbl:<34} £{np.median(f):>8.2f} {np.mean(f>=100):>6.1%} {np.mean(f>=110):>7.1%} "
          f"{np.mean(f<=90):>6.1%} {so:>9.1%} {tw:>8.1%} {nt:>7.1f}")
