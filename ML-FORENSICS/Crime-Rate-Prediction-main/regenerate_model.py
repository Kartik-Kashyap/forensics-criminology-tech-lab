import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# Load data
# Cwd is c:\LOCAL_DISK-E\RESEARCH\forensic\Crime-Rate-Prediction-main
df = pd.read_excel("Dataset/new_dataset.xlsx")

# Encode City
le_city = LabelEncoder()
df['City'] = le_city.fit_transform(df['City'])

# Encode Type
le_type = LabelEncoder()
df['Type'] = le_type.fit_transform(df['Type'])

# Features: Year, City, Population, Type
X = df[['Year', 'City', 'Population (in Lakhs) (2011)+', 'Type']].values
y = df['Crime Rate'].values

# Split data
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=50)

# Train model
model = RandomForestRegressor(random_state=0)
model.fit(x_train, y_train)

# Save model
if not os.path.exists('Model'):
    os.makedirs('Model')
with open('Model/model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model regenerated successfully with encoded features.")
