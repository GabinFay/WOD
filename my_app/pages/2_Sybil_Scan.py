import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA

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
dbscan = DBSCAN(eps=0.5, min_samples=5)  # Tune these parameters
X['cluster'] = dbscan.fit_predict(X_scaled)

# Identify potential Sybils by looking at clusters with multiple users
sybil_clusters = X[X['cluster'] != -1].groupby('cluster').filter(lambda x: len(x) > 1)

# Display Sybil scan results
st.title('Sybil Scan Results')
if not sybil_clusters.empty:
    st.write(f"Potential Sybil clusters found: {sybil_clusters['cluster'].unique()}")
    st.write(f"Number of users in potential Sybil clusters: {len(sybil_clusters)}")
else:
    st.write("No potential Sybil clusters found.")

# Perform PCA for visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Plot the PCA results
fig, ax = plt.subplots(figsize=(10, 7))
scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=X['cluster'], cmap='viridis', marker='o', edgecolor='k', s=50)
ax.set_title('PCA of User Data')
ax.set_xlabel('PCA Component 1')
ax.set_ylabel('PCA Component 2')
plt.colorbar(scatter, ax=ax, label='Cluster Label')

# Display the plot in Streamlit
st.pyplot(fig) 