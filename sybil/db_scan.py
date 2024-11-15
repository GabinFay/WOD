import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Load the data from CSV
file_path = 'user_data_features.csv'
X = pd.read_csv(file_path)

# Handle NaN values by imputing with the mean of each column
imputer = SimpleImputer(strategy='mean')
X_numeric = X.drop(columns=["user_id"])  # Keep all columns except 'user_id'
X_imputed = imputer.fit_transform(X_numeric)

# Normalize the features
X_scaled = StandardScaler().fit_transform(X_imputed)

# Apply DBSCAN
dbscan = DBSCAN(eps=0.5, min_samples=25)  # Tune these parameters
X['cluster'] = dbscan.fit_predict(X_scaled)

# Identify potential Sybils by looking at clusters with multiple users
sybil_clusters = X[X['cluster'] != -1].groupby('cluster').filter(lambda x: len(x) > 1)

# Logic to deduce if Sybils are found
if not sybil_clusters.empty:
    print(f"Potential Sybil clusters found: {sybil_clusters['cluster'].unique()}")
    print(f"Number of users in potential Sybil clusters: {len(sybil_clusters)}")
else:
    print("No potential Sybil clusters found.")

# Perform PCA for visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Plot the PCA results
plt.figure(figsize=(10, 7))
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=X['cluster'], cmap='viridis', marker='o', edgecolor='k', s=50)
plt.title('PCA of User Data')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.colorbar(label='Cluster Label')
plt.show()
