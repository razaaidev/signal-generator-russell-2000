import pandas as pd, numpy as np
df = pd.read_csv("all5yr.csv", parse_dates=["date"])
px = df.pivot(index="date", columns="Name", values="close").sort_index()
print("date range:", px.index.min().date(), "->", px.index.max().date(), "| days:", len(px), "| tickers:", px.shape[1])
r = np.log(px).diff()
# keep tickers with full-ish history
good = r.columns[r.notna().sum() > 1200]
r = r[good].dropna(how="all")
ann = r.std()*np.sqrt(252)
print("\nannualised vol distribution across names:")
print(ann.describe(percentiles=[.1,.25,.5,.75,.9,.99]).round(3))
print("\nhighest-vol names:"); print((ann.sort_values(ascending=False).head(12)*100).round(1))
# excess kurtosis
k = r[good].kurtosis()
print("\nmedian excess kurtosis of daily returns:", round(k.median(),2))
v = pd.read_csv("vix.csv", parse_dates=["DATE"])
print("\nVIX range:", v.DATE.min().date(), "->", v.DATE.max().date(), "| mean", round(v.CLOSE.mean(),1), "| median", round(v.CLOSE.median(),1))
r.to_pickle("rets.pkl"); ann.to_pickle("annvol.pkl")
print("\nsaved rets.pkl", r.shape)
