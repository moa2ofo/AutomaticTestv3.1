import pandas as pd
import glob
import re

files = glob.glob("*.csv")

dfs = []

for f in files:
    m = re.search(r'(\d+)kg_(\d+)rpm', f)
    mass = int(m.group(1))
    rpm = int(m.group(2))

    df = pd.read_csv(f)
    df["massa_kg"] = mass
    df["rpm"] = rpm
    dfs.append(df)

final = pd.concat(dfs, ignore_index=True)

final.to_csv("tabella_totale.csv", index=False)
final.to_excel("tabella_totale.xlsx", index=False)