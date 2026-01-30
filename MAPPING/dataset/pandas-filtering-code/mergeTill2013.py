import pandas as pd

# 1. Read both files
# Change paths if the files are not in the current working directory
df_2001_2012 = pd.read_csv("delhi_only_dstrIPC.csv")
df_2013      = pd.read_csv("delhi_only_dstrIPC_2013.csv")

# 2. Basic checks (good practice)
print("Columns in 2001-2012 file:", df_2001_2012.columns.tolist())
print("Columns in 2013 file:     ", df_2013.columns.tolist())
print("\nYears in first file: ", sorted(df_2001_2012['YEAR'].unique()))
print("Years in second file:", sorted(df_2013['YEAR'].unique()))

# Optional: quick look at row counts
print(f"\nRows in 2001-2012: {len(df_2001_2012):,}")
print(f"Rows in 2013:      {len(df_2013):,}")

# 3. Concatenate (stack rows)
df_merged = pd.concat([df_2001_2012, df_2013], ignore_index=True)

# 4. Optional: sort by YEAR and DISTRICT for better readability
df_merged = df_merged.sort_values(['YEAR', 'DISTRICT']).reset_index(drop=True)

# 5. Save to new file
output_filename = "delhi_crime_2001_to_2013.csv"
df_merged.to_csv(output_filename, index=False)

print(f"\nMerged file saved as: {output_filename}")
print(f"Total rows: {len(df_merged):,}")
print(f"Years covered: {sorted(df_merged['YEAR'].unique())}")

# Optional: show first few and last few rows
print("\nFirst 3 rows:")
print(df_merged.head(3))
print("\nLast 3 rows:")
print(df_merged.tail(3))