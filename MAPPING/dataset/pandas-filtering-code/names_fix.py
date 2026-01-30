import pandas as pd

# 1. Read the file
df = pd.read_csv("delhi_crime_2001_2013_core_districts_only.csv")   # ← change to your actual filename

# 2. Rename districts (remove hyphen where present)
rename_map = {
    'North-East': 'North East',
    'North-West': 'North West',
    'South-West': 'South West',
    # add more if you see other variations in your full file
    # e.g. 'NORTH-EAST': 'North East', etc.
}

df['DISTRICT'] = df['DISTRICT'].replace(rename_map)

# 3. Define the desired order
desired_order = [
    'Central',
    'East',
    'North East',
    'North',
    'North West',
    'New Delhi',
    'South',
    'South West',
    'West'
]

# Create a categorical type with the desired order
df['DISTRICT'] = pd.Categorical(
    df['DISTRICT'],
    categories=desired_order,
    ordered=True
)

# 4. Sort: first by YEAR, then by the custom district order
df = df.sort_values(['YEAR', 'DISTRICT'])

# 5. (Optional) reset index if you want clean row numbers
df = df.reset_index(drop=True)

# 6. Save the result
df.to_csv("delhi_crime_2001_2013_namesFix_reordered.csv", index=False)

print("Done.")
print("New file created: delhi_crime_2001_2013_namesFix_reordered.csv")
print("\nCheck the district order in one year:")
print(df[df['YEAR'] == 2001][['YEAR', 'DISTRICT']])