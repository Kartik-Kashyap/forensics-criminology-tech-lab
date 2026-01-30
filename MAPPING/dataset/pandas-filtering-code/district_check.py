import pandas as pd

df = pd.read_csv("delhi_crime_2001_to_2013.csv")

print("Unique districts mentioned each year:\n")
for year, group in df.groupby('YEAR'):
    districts = sorted(group['DISTRICT'].unique())
    print(f"Year {year}: {len(districts)} districts")
    print(", ".join(districts))
    print()