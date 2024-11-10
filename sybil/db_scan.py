from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

# Normalize the features
X_numeric = X.drop(columns=["user_id", "daily_pattern"])  # Keep only numerical features
X_scaled = StandardScaler().fit_transform(X_numeric)

# Apply DBSCAN
dbscan = DBSCAN(eps=0.5, min_samples=5)  # Tune these parameters
X['cluster'] = dbscan.fit_predict(X_scaled)

# Identify potential Sybils by looking at clusters with multiple users
sybil_clusters = X[X['cluster'] != -1].groupby('cluster').filter(lambda x: len(x) > 1)
