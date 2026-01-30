import pandas as pd

# ────────────────────────────────────────────────
# Load your merged file
# ────────────────────────────────────────────────
df = pd.read_csv("delhi_crime_2001_to_2013.csv")

# Clean up any sneaky whitespace in district names
df['DISTRICT'] = df['DISTRICT'].str.strip()

# Create temporary uppercase version for reliable matching
df['DISTRICT_upper'] = df['DISTRICT'].str.upper()

# ────────────────────────────────────────────────
# Districts we want to KEEP (various common spellings)
# ────────────────────────────────────────────────
keep_districts_upper = {
    'CENTRAL',
    'NEW DELHI',
    'NORTH',
    'SOUTH',
    'EAST',
    'NORTH EAST', 'NORTH-EAST',
    'NORTH WEST', 'NORTH-WEST',
    'SOUTH WEST', 'SOUTH-WEST',
    'WEST'
}

# Filter rows — keep only matching districts
mask = df['DISTRICT_upper'].isin(keep_districts_upper)
filtered_df = df[mask].copy()

# ────────────────────────────────────────────────
# Standardize names to nice consistent format
# ────────────────────────────────────────────────
district_standard = {
    'CENTRAL':      'Central',
    'NEW DELHI':    'New Delhi',
    'NORTH':        'North',
    'SOUTH':        'South',
    'EAST':         'East',
    'NORTH EAST':   'North-East',
    'NORTH-EAST':   'North-East',
    'NORTH WEST':   'North-West',
    'NORTH-WEST':   'North-West',
    'SOUTH WEST':   'South-West',
    'SOUTH-WEST':   'South-West',
    'WEST':         'West',
}

# Apply standardization using the uppercase column (still exists here)
filtered_df['DISTRICT'] = filtered_df['DISTRICT_upper'].map(district_standard)

# Now safe to drop the helper column
filtered_df = filtered_df.drop(columns=['DISTRICT_upper'])

# Sort for clean output: year → district
filtered_df = filtered_df.sort_values(['YEAR', 'DISTRICT']).reset_index(drop=True)

# ────────────────────────────────────────────────
# Save and show summary
# ────────────────────────────────────────────────
output_file = "delhi_crime_2001_2013_core_districts_only.csv"
filtered_df.to_csv(output_file, index=False)

print(f"Original rows:          {len(df):,}")
print(f"Rows after filtering:   {len(filtered_df):,}")
print(f"Rows removed:           {len(df) - len(filtered_df):,}\n")

print("Final districts kept (should be exactly these 9):")
print(sorted(filtered_df['DISTRICT'].unique()))

print("\nNumber of records per year (only core districts):")
print(filtered_df['YEAR'].value_counts().sort_index())

print(f"\nClean file saved → {output_file}")