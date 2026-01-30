import pandas as pd
df_clean = pd.read_csv("delhi_crime_2001_2013_core_districts_only.csv")
print(df_clean['DISTRICT'].unique())



df = pd.read_csv("delhi_crime_2001_2013_core_districts_only.csv")

print("Unique districts mentioned each year:\n")
for year, group in df.groupby('YEAR'):
    districts = sorted(group['DISTRICT'].unique())
    print(f"Year {year}: {len(districts)} districts")
    print(", ".join(districts))
    print()