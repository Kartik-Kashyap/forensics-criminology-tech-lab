import pandas as pd

# Read the CSV file
# (adjust the path if your file is not in the same folder as this script)
df = pd.read_csv("dstrIPC_2013.csv")

# Filter rows where STATE/UT is exactly "Delhi UT"
# Using .str.strip() in case there are extra spaces in the data
delhi_df = df[df['STATE/UT'].str.strip() == 'Delhi UT']

# Alternative spellings people sometimes use - uncomment if needed:
# delhi_df = df[df['STATE/UT'].str.strip().str.upper().isin(['DELHI', 'DELHI UT', 'NCT OF DELHI'])]

# Check how many rows we got
print(f"Number of rows for DELHI UT: {len(delhi_df)}")
if len(delhi_df) == 0:
    print("Warning: No rows found with STATE/UT = 'DELHI UT'")
    print("Actual unique values in STATE/UT column:")
    print(df['STATE/UT'].unique())

# Save to new CSV file
delhi_df.to_csv("delhi_only_dstrIPC_2013.csv", index=False)

print("Done! Output file created: delhi_only_dstrIPC_2013.csv")