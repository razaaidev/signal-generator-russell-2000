import numpy as np, pandas as pd
exec(open("calib2.py").read().split("print(\"SIZING")[0])

print("CONTROL — chosen config (3.0s stop, 21d cap, 4 x 25%) across skill levels")
print(f"{'hit rate':>9} {'median':>9} {'P(BE)':>7} {'P>=110':>8} {'P>=120':>8} {'P<=90':>7} {'P<=75':>7} {'trades':>7}")
for p in (0.50, 0.55, 0.60, 0.65):
    f,st,so,tw,nt = run(p, 3.0, 21, False, 0.05, 4, nsim=20000)
    print(f"{p:>8.0%} £{np.median(f):>8.2f} {np.mean(f>=100):>6.1%} {np.mean(f>=110):>7.1%} "
          f"{np.mean(f>=120):>7.1%} {np.mean(f<=90):>6.1%} {np.mean(f<=75):>6.1%} {nt:>7.1f}")

print(f"\nstop distance at 3.0 sigma = {3.0*sig:.1%} of entry (cohort daily sigma {sig:.2%})")
print(f"position size = min(5%/stop, 25%) = {min(0.05/(3*sig),0.25):.0%} of account -> 4 slots = fully invested")

print("\nALERT FREQUENCY — how often a held name closes below its 20-day SMA")
n=0; fires=0; days=0
for _ in range(4000):
    t0=rng.integers(40,len(U)-25); c=rng.integers(0,U.shape[1])
    if not (LV[t0,c] > SMA20[t0,c]): continue      # only count names entered in an uptrend
    n+=1
    for d in range(1,22):
        days+=1
        if LV[t0+d,c] < SMA20[t0+d,c]: fires+=1; break
print(f"  of {n} positions entered above the 20-day, {fires/n:.0%} closed below it within 21 trading days")
print(f"  -> expect roughly {fires/n*4:.1f} alerts per month with 4 open positions")

print("\nSANITY — does the stop formula scale? noise stop-out at 3 sigma should be ~vol-invariant")
for lo,hi,lbl in ((0.20,0.35,"mid-vol"),(0.35,1.0,"small-cap proxy")):
    c2=C[(ANN.reindex(C).values>lo)&(ANN.reindex(C).values<=hi)]
    U2=np.exp(R[c2].dropna(how="any").values)-1.0; s2=np.mean(U2.std(axis=0))
    hit=0
    for _ in range(8000):
        t=rng.integers(0,len(U2)-22); cc=rng.integers(0,U2.shape[1])
        if (np.cumprod(1+U2[t:t+21,cc])-1).min() <= -3.0*s2: hit+=1
    print(f"  {lbl:<18} daily sigma {s2:.2%} -> 3s stop = {3*s2:>5.1%} -> touched in {hit/8000:.1%} of 21-day holds")
