import pandas as pd, numpy as np
df = pd.read_csv("all5yr.csv", parse_dates=["date"])
px = df.pivot(index="date", columns="Name", values="close").sort_index()
ratio = px/px.shift(1)
cands = [2,3,4,5,7,10,1/2,1/3,1/4,1/5,1/7,1/10]
fixed, log = px.copy(), []
for c in px.columns:
    r = ratio[c]
    hits = r[(r.notna()) & ((r>1.8)|(r<0.55))]
    for dt, val in hits.items():
        m = min(cands, key=lambda k: abs(val-k))
        if abs(val-m)/m < 0.08:                      # split-like jump
            fixed.loc[:dt-pd.Timedelta(days=1), c] = fixed.loc[:dt-pd.Timedelta(days=1), c]*m
            log.append((c, str(dt.date()), round(val,3), m))
print(f"splits corrected: {len(log)}"); [print("  ", *x) for x in log[:15]]
r = np.log(fixed).diff()
good = r.columns[r.notna().sum() > 1200]; r = r[good]
r = r.mask(r.abs() > 0.40)                            # residual bad ticks
ann = r.std()*np.sqrt(252)
print("\nann vol pctiles:", (ann.describe(percentiles=[.5,.9,.99])[['50%','90%','99%','max']]*100).round(1).to_dict())
print("median excess kurtosis:", round(r.kurtosis().median(),2))
hv = ann[ann>0.40].index
print(f"\nHV cohort ({len(hv)}):", list(hv))
print("HV mean ann vol:", f"{ann[hv].mean():.1%}", "| max:", f"{ann[hv].max():.1%}")
print("HV excess kurtosis:", round(r[hv].kurtosis().mean(),2))
r.to_pickle("rets_clean.pkl"); ann.to_pickle("annvol_clean.pkl")
