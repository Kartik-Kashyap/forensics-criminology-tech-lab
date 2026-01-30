import pandas as pd

# ================================================================
# 1. Read the files (adjust paths if needed)
# ================================================================
df_old = pd.read_csv("delhi_only_dstrIPC.csv")          # 2001-2012
df_2013 = pd.read_csv("delhi_only_dstrIPC_2013.csv")    # 2013
df_2014 = pd.read_csv("delhi_only_dstrIPC_2014.csv")    # 2014

# Standardize column names - remove extra spaces, make consistent
for df in [df_old, df_2013, df_2014]:
    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

# ================================================================
# 2. Define the target (final) column names = those from 2001-2013 files
# ================================================================
target_columns = [
    'STATE/UT', 'DISTRICT', 'YEAR',
    'MURDER', 'ATTEMPT TO MURDER', 'CULPABLE HOMICIDE NOT AMOUNTING TO MURDER',
    'RAPE', 'CUSTODIAL RAPE', 'OTHER RAPE',
    'KIDNAPPING & ABDUCTION',
    'KIDNAPPING AND ABDUCTION OF WOMEN AND GIRLS', 'KIDNAPPING AND ABDUCTION OF OTHERS',
    'DACOITY', 'PREPARATION AND ASSEMBLY FOR DACOITY', 'ROBBERY',
    'BURGLARY', 'THEFT', 'AUTO THEFT', 'OTHER THEFT',
    'RIOTS',
    'CRIMINAL BREACH OF TRUST', 'CHEATING', 'COUNTERFIETING',
    'ARSON', 'HURT/GREVIOUS HURT',
    'DOWRY DEATHS',
    'ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY',
    'INSULT TO MODESTY OF WOMEN',
    'CRUELTY BY HUSBAND OR HIS RELATIVES',
    'IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES',
    'CAUSING DEATH BY NEGLIGENCE',
    'OTHER IPC CRIMES', 'TOTAL IPC CRIMES'
]

# ================================================================
# 3. Prepare 2001-2013 data (very similar → just concat)
# ================================================================
df_2001_2013 = pd.concat([df_old, df_2013], ignore_index=True)

# Make sure we have all target columns (some might be missing)
df_2001_2013 = df_2001_2013.reindex(columns=target_columns)

# ================================================================
# 4. Map 2014 columns → best effort matching
# ================================================================
mapping_2014_to_old = {
    'States/UTs':                              'STATE/UT',
    'District':                                 'DISTRICT',
    'Year':                                     'YEAR',
    
    'Murder':                                   'MURDER',
    'Attempt to commit Murder':                 'ATTEMPT TO MURDER',
    'Culpable Homicide not amounting to Murder':'CULPABLE HOMICIDE NOT AMOUNTING TO MURDER',
    
    # Rape - best approximation (total rape)
    'Rape':                                     'RAPE',
    # If you want to split:
    # 'Custodial Rape' + 'Custodial_Gang Rape' + 'Custodial_Other Rape' → CUSTODIAL RAPE
    # 'Rape other than Custodial' + 'Rape_Gang Rape' + 'Rape_Others' → OTHER RAPE
    # But for simplicity we take total 'Rape' → 'RAPE'
    
    'Kidnapping & Abduction_Total':             'KIDNAPPING & ABDUCTION',
    # The sub-categories don't match perfectly → we skip most of them
    
    'Dacoity':                                  'DACOITY',
    'Making Preparation and Assembly for committing Dacoity': 'PREPARATION AND ASSEMBLY FOR DACOITY',
    'Robbery':                                  'ROBBERY',
    
    'Criminal Trespass or Burglary':            'BURGLARY',   # closest match
    'Theft':                                    'THEFT',
    'Auto Theft':                               'AUTO THEFT',
    # 'Other Thefts' → OTHER THEFT
    
    'Riots':                                    'RIOTS',
    
    'Criminal Breach of Trust':                 'CRIMINAL BREACH OF TRUST',
    'Cheating':                                 'CHEATING',
    'Counterfeiting':                           'COUNTERFIETING',   # note spelling
    
    'Arson':                                    'ARSON',
    'Grievous Hurt':                            'HURT/GREVIOUS HURT',  # partial match (Hurt is separate)
    # 'Hurt' exists but we map only Grievous → you can adjust
    
    'Dowry Deaths':                             'DOWRY DEATHS',
    'Assault on Women with intent to outrage her Modesty': 'ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY',
    'Insult to the Modesty of Women':           'INSULT TO MODESTY OF WOMEN',
    'Cruelty by Husband or his Relatives':      'CRUELTY BY HUSBAND OR HIS RELATIVES',
    'Importation of Girls from Foreign Country':'IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES',
    'Causing Death by Negligence':              'CAUSING DEATH BY NEGLIGENCE',
    
    'Other IPC crimes':                         'OTHER IPC CRIMES',
    'Total Cognizable IPC crime':               'TOTAL IPC CRIMES'
}

# Create 2014 version with renamed columns
df_2014_renamed = df_2014.rename(columns=mapping_2014_to_old)

df_2014_renamed['CUSTODIAL RAPE'] = df_2014[['Custodial Rape','Custodial_Gang Rape','Custodial_Other Rape']].sum(axis=1, skipna=True)
df_2014_renamed['OTHER RAPE'] = df_2014[['Rape other than Custodial','Rape_Gang Rape','Rape_Others']].sum(axis=1, skipna=True)
df_2014_renamed['RAPE'] = df_2014_renamed['CUSTODIAL RAPE'] + df_2014_renamed['OTHER RAPE']

# Keep only columns that exist in target + fill missing with NaN
df_2014_aligned = df_2014_renamed.reindex(columns=target_columns)

# ================================================================
# 5. Final concatenation
# ================================================================
df_final = pd.concat([df_2001_2013, df_2014_aligned], ignore_index=True)

# Optional: sort by year and district for nicer view
df_final = df_final.sort_values(['YEAR', 'DISTRICT'])

# ================================================================
# 6. Save and check
# ================================================================
df_final.to_csv("delhi_crime_2001_2014_merged.csv", index=False)

print("Merged file saved: delhi_crime_2001_2014_merged.csv")
print("Shape:", df_final.shape)
print("\nYears present:", sorted(df_final['YEAR'].unique()))
print("\nMissing values per column:\n", df_final.isna().sum())