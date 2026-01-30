import pandas as pd

# 1. Load your main crime file
crime_df = pd.read_csv("delhi_crime_2001_2013_core_districts_namesFix_reordered.csv")

# 2. Load the population CSV you shared
# (make sure the file is in the same folder as this script)
pop_df = pd.read_csv("delhi_district_population_census2011.csv")

# Quick clean-up (in case of extra spaces)
pop_df['District'] = pop_df['District'].str.strip()
crime_df['DISTRICT'] = crime_df['DISTRICT'].str.strip()

# 3. Select only the columns we want from population
# You can add more columns later if needed (Sex Ratio, Literacy, etc.)
pop_subset = pop_df[['District', 'Population', 'Density']].copy()

# Rename 'District' → 'DISTRICT' to match crime file
pop_subset = pop_subset.rename(columns={'District': 'DISTRICT'})

# Convert Population and Density to numeric (remove commas if any, though your sample doesn't have them)
pop_subset['Population'] = pd.to_numeric(pop_subset['Population'], errors='coerce')
pop_subset['Density'] = pd.to_numeric(pop_subset['Density'], errors='coerce')

# 4. Merge population into crime data (left join on DISTRICT)
# All years get the same 2011 population values for each district
merged_df = pd.merge(
    crime_df,
    pop_subset,
    on='DISTRICT',
    how='left'          # keeps all crime rows, even if district not in pop
)

# Optional: check for missing matches
missing = merged_df[merged_df['Population'].isna()]['DISTRICT'].unique()
if len(missing) > 0:
    print("Warning: These districts have no population match:")
    print(missing)
else:
    print("All districts matched successfully.")

# Optional: add crime rate columns (example: total IPC crimes per 100,000 people)
# Only makes sense if Population is not NaN
merged_df['Total_IPC_per_100k'] = (merged_df['TOTAL IPC CRIMES'] / merged_df['Population']) * 100000
merged_df['Murder_per_100k']     = (merged_df['MURDER'] / merged_df['Population']) * 100000

# Round rates to 2 decimal places for readability
merged_df['Total_IPC_per_100k'] = merged_df['Total_IPC_per_100k'].round(2)
merged_df['Murder_per_100k']     = merged_df['Murder_per_100k'].round(2)

# 5. Save the enriched full file (optional — good for checking)
merged_df.to_csv("delhi_crime_2001_2013_with_population.csv", index=False)
print("Saved full file with population: delhi_crime_2001_2013_with_population.csv")

# 6. Split into year-wise files for QGIS (as you wanted)
years = range(2001, 2014)

for year in years:
    df_year = merged_df[merged_df['YEAR'] == year].copy()
    output_name = f"qgis_delhi_crime_{year}_with_pop.csv"
    df_year.to_csv(output_name, index=False)
    print(f"Saved {output_name} -> {len(df_year)} rows")

print("\nDone! You now have year-wise CSVs with Population, Density, and example rates.")
print("Use these directly in QGIS for joins -> you can symbolize using 'Population', 'Total_IPC_per_100k', etc.")