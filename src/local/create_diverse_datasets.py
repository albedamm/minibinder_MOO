from sklearn.cluster import KMeans

# Extract the column of interest for clustering
pae_values = data[['pae_interaction_HLA_B_0801_NLFRRVWEL']]

# Use KMeans to cluster into 500 groups for diverse sampling
kmeans = KMeans(n_clusters=500, random_state=42)
data['cluster'] = kmeans.fit_predict(pae_values)

# From each cluster, select one representative binder
diverse_sample = data.groupby('cluster').apply(lambda x: x.sample(1)).reset_index(drop=True)

# Drop the cluster column and save the diverse dataset
diverse_sample = diverse_sample.drop(columns=['cluster'])

# Display the dataset to the user
import ace_tools as tools; tools.display_dataframe_to_user(name="Diverse Dataset of 500 Binders", dataframe=diverse_sample)
