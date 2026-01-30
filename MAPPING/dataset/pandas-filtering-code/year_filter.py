import pandas as pd

df = pd.read_csv("delhi_crime_2001_2013_core_districts_namesFix_reordered.csv")

for year in range(2001, 2014):
    df_year = df[df['YEAR'] == year]
    df_year.to_csv(f"qgis_delhi_crime_{year}.csv", index=False)
    print(f"Saved qgis_delhi_crime_{year}.csv  ->  {len(df_year)} rows")