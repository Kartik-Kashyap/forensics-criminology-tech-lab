import pandas as pd
import numpy as np

# Read the three CSV files
df_2001_2012 = pd.read_csv('delhi_only_dstrIPC.csv')
df_2013 = pd.read_csv('delhi_only_dstrIPC_2013.csv')
df_2014 = pd.read_csv('delhi_only_dstrIPC_2014.csv')

# Standardize column names to uppercase for consistency
df_2001_2012.columns = df_2001_2012.columns.str.upper()
df_2013.columns = df_2013.columns.str.upper()
df_2014.columns = df_2014.columns.str.upper()

# Create a mapping for 2014 columns to match earlier format
# The 2014 format has more granular categories that need to be collapsed

# First, let's create aggregated columns in df_2014 to match the earlier format
df_2014_processed = df_2014.copy()

# Map basic columns
column_mapping = {
    'STATES/UTS': 'STATE/UT',
    'YEAR': 'YEAR',
    'MURDER': 'MURDER',
    'ATTEMPT TO COMMIT MURDER': 'ATTEMPT TO MURDER',
    'CULPABLE HOMICIDE NOT AMOUNTING TO MURDER': 'CULPABLE HOMICIDE NOT AMOUNTING TO MURDER'
}

# Aggregate RAPE columns (2014 breaks it down into multiple categories)
if 'RAPE' in df_2014_processed.columns:
    df_2014_processed['RAPE_TOTAL'] = df_2014_processed['RAPE']
else:
    # Sum all rape-related columns
    rape_cols = [col for col in df_2014_processed.columns if 'RAPE' in col and col != 'CUSTODIAL RAPE']
    df_2014_processed['RAPE_TOTAL'] = df_2014_processed[rape_cols].sum(axis=1, skipna=True)

# Aggregate CUSTODIAL RAPE
custodial_rape_cols = [col for col in df_2014_processed.columns if 'CUSTODIAL' in col and 'RAPE' in col]
if custodial_rape_cols:
    df_2014_processed['CUSTODIAL RAPE'] = df_2014_processed[custodial_rape_cols].sum(axis=1, skipna=True)

# Aggregate OTHER RAPE
other_rape_cols = ['RAPE OTHER THAN CUSTODIAL', 'RAPE_GANG RAPE', 'RAPE_OTHERS', 'ATTEMPT TO COMMIT RAPE']
available_other_rape = [col for col in other_rape_cols if col in df_2014_processed.columns]
if available_other_rape:
    df_2014_processed['OTHER RAPE'] = df_2014_processed[available_other_rape].sum(axis=1, skipna=True)

# Aggregate KIDNAPPING & ABDUCTION
if 'KIDNAPPING & ABDUCTION_TOTAL' in df_2014_processed.columns:
    df_2014_processed['KIDNAPPING & ABDUCTION'] = df_2014_processed['KIDNAPPING & ABDUCTION_TOTAL']
else:
    kidnap_cols = [col for col in df_2014_processed.columns if 'KIDNAPPING' in col or 'ABDUCTION' in col]
    df_2014_processed['KIDNAPPING & ABDUCTION'] = df_2014_processed[kidnap_cols].sum(axis=1, skipna=True)

# For sub-categories that exist in earlier format
if 'KIDNAPPING & ABDUCTION' in df_2014_processed.columns and 'KIDNAPPING & ABDUCTION IN ORDER TO MURDER' in df_2014_processed.columns:
    # Use the total if available, otherwise sum components
    pass

df_2014_processed['KIDNAPPING AND ABDUCTION OF WOMEN AND GIRLS'] = df_2014_processed.get('KIDNAPPING & ABDUCTION OF WOMEN TO COMPEL HER FOR MARRIAGE', 0)
df_2014_processed['KIDNAPPING AND ABDUCTION OF OTHERS'] = df_2014_processed.get('OTHER KIDNAPPING', 0)

# Aggregate DACOITY
dacoity_cols = ['DACOITY', 'DACOITY WITH MURDER', 'OTHER DACOITY']
available_dacoity = [col for col in dacoity_cols if col in df_2014_processed.columns]
if available_dacoity:
    df_2014_processed['DACOITY_TOTAL'] = df_2014_processed[available_dacoity].sum(axis=1, skipna=True)

df_2014_processed['PREPARATION AND ASSEMBLY FOR DACOITY'] = df_2014_processed.get('MAKING PREPARATION AND ASSEMBLY FOR COMMITTING DACOITY', 0)

# ROBBERY stays the same
df_2014_processed['ROBBERY'] = df_2014_processed.get('ROBBERY', 0)

# Aggregate BURGLARY
burglary_cols = ['CRIMINAL TRESPASS/BURGLARY', 'CRIMINAL TRESPASS OR BURGLARY', 'HOUSE TRESPASS & HOUSE BREAKING']
available_burglary = [col for col in burglary_cols if col in df_2014_processed.columns]
if available_burglary:
    df_2014_processed['BURGLARY'] = df_2014_processed[available_burglary].sum(axis=1, skipna=True)

# THEFT columns
df_2014_processed['THEFT'] = df_2014_processed.get('THEFT', 0)
df_2014_processed['AUTO THEFT'] = df_2014_processed.get('AUTO THEFT', 0)
df_2014_processed['OTHER THEFT'] = df_2014_processed.get('OTHER THEFTS', 0)

# Aggregate RIOTS
riots_cols = [col for col in df_2014_processed.columns if col.startswith('RIOTS')]
if riots_cols:
    df_2014_processed['RIOTS_TOTAL'] = df_2014_processed[riots_cols].sum(axis=1, skipna=True)

# Other columns that map directly or similarly
df_2014_processed['CRIMINAL BREACH OF TRUST'] = df_2014_processed.get('CRIMINAL BREACH OF TRUST', 0)
df_2014_processed['CHEATING'] = df_2014_processed.get('CHEATING', 0)

# Aggregate COUNTERFEITING
counter_cols = [col for col in df_2014_processed.columns if 'COUNTER' in col or 'FORGERY' in col]
if counter_cols:
    df_2014_processed['COUNTERFIETING'] = df_2014_processed[counter_cols].sum(axis=1, skipna=True)

df_2014_processed['ARSON'] = df_2014_processed.get('ARSON', 0)

# Aggregate HURT
hurt_cols = ['GRIEVOUS HURT', 'HURT', 'ACID ATTACK', 'ATTEMPT TO ACID ATTACK']
available_hurt = [col for col in hurt_cols if col in df_2014_processed.columns]
if available_hurt:
    df_2014_processed['HURT/GREVIOUS HURT'] = df_2014_processed[available_hurt].sum(axis=1, skipna=True)

df_2014_processed['DOWRY DEATHS'] = df_2014_processed.get('DOWRY DEATHS', 0)

# Aggregate assault on women
assault_cols = ['ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY', 'SEXUAL HARASSMENT', 
                'ASSAULT OR USE OF CRIMINAL FORCE TO WOMEN WITH INTENT TO DISROBE', 
                'VOYEURISM', 'STALKING', 'OTHER ASSAULT ON WOMEN']
available_assault = [col for col in assault_cols if col in df_2014_processed.columns]
if available_assault:
    df_2014_processed['ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY'] = df_2014_processed[available_assault].sum(axis=1, skipna=True)

# Insult to modesty - aggregate all related columns
modesty_cols = ['INSULT TO THE MODESTY OF WOMEN', 'AT OFFICE PREMISES', 'OTHER PLACES RELATED TO WORK', 
                'IN PUBLIC TRANSPORT SYSTEM', 'PLACES OTHER THAN 231, 232 & 233']
available_modesty = [col for col in modesty_cols if col in df_2014_processed.columns]
if available_modesty:
    df_2014_processed['INSULT TO MODESTY OF WOMEN'] = df_2014_processed[available_modesty].sum(axis=1, skipna=True)

df_2014_processed['CRUELTY BY HUSBAND OR HIS RELATIVES'] = df_2014_processed.get('CRUELTY BY HUSBAND OR HIS RELATIVES', 0)
df_2014_processed['IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES'] = df_2014_processed.get('IMPORTATION OF GIRLS FROM FOREIGN COUNTRY', 0)

# Aggregate negligence deaths
negligence_cols = ['CAUSING DEATH BY NEGLIGENCE', 'DEATHS DUE TO NEGLIGENT DRIVING/ACT', 'DEATHS DUE TO OTHER CAUSES']
available_negligence = [col for col in negligence_cols if col in df_2014_processed.columns]
if available_negligence:
    df_2014_processed['CAUSING DEATH BY NEGLIGENCE'] = df_2014_processed[available_negligence].sum(axis=1, skipna=True)

# Aggregate OTHER IPC CRIMES (including all new categories in 2014)
other_ipc_base = df_2014_processed.get('OTHER IPC CRIMES', 0)
new_2014_cols = ['OFFENCES AGAINST STATE', 'SEDITION', 'OTHER OFFENCES AGAINST STATE', 
                 'OFFENCES PROMOTING ENMITY BETWEEN DIFFERENT GROUPS', 'PROMOTING ENMITY BETWEEN DIFFERENT GROUPS',
                 'IMPUTATION, ASSERTIONS PREJUDICIAL TO NATIONAL INTEGRATION', 'EXTORTION', 
                 'DISCLOSURE OF IDENTITY OF VICTIMS', 'INCIDENCE OF RASH DRIVING', 
                 'HUMANTRAFFICKING', 'UNNATURAL OFFENCE']
available_new = [col for col in new_2014_cols if col in df_2014_processed.columns]
if available_new:
    df_2014_processed['OTHER IPC CRIMES'] = other_ipc_base + df_2014_processed[available_new].sum(axis=1, skipna=True)
else:
    df_2014_processed['OTHER IPC CRIMES'] = other_ipc_base

# Use the total cognizable IPC crime if available
if 'TOTAL COGNIZABLE IPC CRIME' in df_2014_processed.columns:
    df_2014_processed['TOTAL IPC CRIMES'] = df_2014_processed['TOTAL COGNIZABLE IPC CRIME']

# Now create the final standardized DataFrame for 2014 with only the columns from earlier years
standard_columns = df_2001_2012.columns.tolist()

# Rename STATE/UT column
df_2014_processed.rename(columns={'STATES/UTS': 'STATE/UT'}, inplace=True)

# Create final 2014 dataframe with standard columns
df_2014_final = pd.DataFrame()
for col in standard_columns:
    if col in df_2014_processed.columns:
        df_2014_final[col] = df_2014_processed[col]
    elif col == 'RAPE':
        df_2014_final[col] = df_2014_processed.get('RAPE_TOTAL', 0)
    elif col == 'DACOITY':
        df_2014_final[col] = df_2014_processed.get('DACOITY_TOTAL', 0)
    elif col == 'RIOTS':
        df_2014_final[col] = df_2014_processed.get('RIOTS_TOTAL', 0)
    else:
        df_2014_final[col] = 0

# Ensure all three dataframes have the same columns
for df in [df_2001_2012, df_2013]:
    for col in standard_columns:
        if col not in df.columns:
            df[col] = 0

# Concatenate all three dataframes
merged_df = pd.concat([df_2001_2012, df_2013, df_2014_final], ignore_index=True)

# Fill NaN values with 0
merged_df = merged_df.fillna(0)

# Convert numeric columns to appropriate types
numeric_cols = merged_df.columns.difference(['STATE/UT', 'DISTRICT'])
for col in numeric_cols:
    if col == 'YEAR':
        merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce').astype('Int64')
    else:
        merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce').fillna(0).astype(int)

# Sort by year
merged_df = merged_df.sort_values('YEAR').reset_index(drop=True)

# Save the merged file
merged_df.to_csv('delhi_merged_IPC_2001_2014.csv', index=False)

print("Merge completed successfully!")
print(f"\nShape of merged dataframe: {merged_df.shape}")
print(f"\nYears covered: {merged_df['YEAR'].min()} to {merged_df['YEAR'].max()}")
print(f"\nColumns in merged file: {len(merged_df.columns)}")
print("\nSample of merged data:")
print(merged_df.head())
print("\nColumn names:")
print(merged_df.columns.tolist())