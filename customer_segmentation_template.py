
import pandas as pd
import numpy as np

from sklearn.mixture import GaussianMixture
from sklearn.model_selection import train_test_split

from sklearn.preprocessing import OneHotEncoder
from sklearn.cluster import KMeans
import matplotlib.pylab as plt

pd.set_option('display.max_columns', 25)


# ------ Define functions ------
def run_kmeans(n_clusters_f, init_f, df_f):
    
    ##### Complete this function
    # This function should at least take a dataframe as an argument. I have suggested additional arguments you may
    # want to provide, but these can be changed as you need to fit your solution.
    # The output of this function should be the input data frame will the model object KMeans and a data summary. The
    # function will need to add an additional column to the input dataframe called 'predict_cluster_kmeans'
    # that contains the cluster labels assigned by the algorithm.

    k_means_model_f = KMeans(n_clusters=n_clusters_f,init=init_f).fit(df_f)
    df_f['predict_cluster_kmeans'] = k_means_model_f.labels_
    df_f['predict_cluster_kmeans'] = df_f['predict_cluster_kmeans'].astype(int)

    # summarize cluster attributes
    k_means_model_f_summary = df_f.groupby('predict_cluster_kmeans').agg(attribute_summary_method_dict)
    return k_means_model_f, k_means_model_f_summary

# ------ Import data ------

df_transactions = pd.read_csv('transactions_n100000.csv') #7 columns
# ------ Engineer features -----
# --- convert from long to wide
df = df_transactions.pivot(index='ticket_id', columns='item_name', values='item_count').fillna(0)
df_transactions.reset_index(inplace=True)
df_transactions.drop(columns='index', inplace=True)

# --- add back date and location
df = df.merge(df_transactions[['ticket_id', 'location', 'order_timestamp']].drop_duplicates(), how='left', on='ticket_id')

df1 = df.order_timestamp

# --- extract hour of day from datetime

###df['hour'] = df2.order_timestamp.apply(lambda x: x.hour)
time=df1.values
hour = [x.split(' ')[1][:2] for x in time]
for i in hour:
    i = int(i)
df['hour']=hour


# --- convert categorical store variables to dummies
encoded_data = OneHotEncoder()
encoded_data.fit(np.array(df['location']).reshape(-1,1))  
encoded_data.categories_##### use sklearn.preprocessing.OneHotEncoder() to create a class object called encoded_data (see documentation for OneHotEncoder online)
##### call the method used to fit data for a OneHotEncorder object. Note: you will have to reshape data from a column of the data frame. useful functions may be DataFrame methods .to_list(), .reshape(), and .shape()
col_map_store_binary = dict(zip(list(encoded_data.get_feature_names()), ['store_' + x.split('x0_')[1] for x in encoded_data.get_feature_names()]))
df_store_binary = pd.DataFrame(encoded_data.transform(X=np.array(df['location'].tolist()).reshape(df.shape[0], 1)).toarray())
df_store_binary.columns = encoded_data.get_feature_names()
df_store_binary.rename(columns=col_map_store_binary, inplace=True)

df = pd.concat([df, df_store_binary], axis=1)
df['burger'] = df['burger'].astype(int)
df['fries'] = df['fries'].astype(int)
df['salad'] = df['salad'].astype(int)
df['shake'] = df['shake'].astype(int)
df['hour'] = df['hour'].astype(int)
df['location'] = df['location'].astype(int)
df['store_1.0'] = df['store_1.0'].astype(int)
df['store_2.0'] = df['store_2.0'].astype(int)
df['store_3.0'] = df['store_3.0'].astype(int)
df['store_4.0'] = df['store_4.0'].astype(int)
df['store_5.0'] = df['store_5.0'].astype(int)
df['store_6.0'] = df['store_6.0'].astype(int)
df['store_7.0'] = df['store_7.0'].astype(int)
df['store_8.0'] = df['store_8.0'].astype(int)
df['store_9.0'] = df['store_9.0'].astype(int)

# ------ RUN CLUSTERING -----
# --- set parameters
n_clusters = 3
init_point_selection_method = 'k-means++'

# --- select data
cols_for_clustering = ['burger','fries','salad','shake','hour','store_1.0','store_2.0','store_3.0','store_4.0','store_5.0','store_6.0','store_7.0','store_8.0','store_9.0'] ##### specify list of attributes on which to base clusters
df_cluster = df.loc[:, cols_for_clustering]
# --- split to test and train
df_cluster_train, df_cluster_test, _, _, = train_test_split(df_cluster, [1]*df_cluster.shape[0], test_size=0.33)   # ignoring y values for unsupervised

# --- fit model
attribute_summary_method_dict = {'burger': np.mean, 'fries': np.mean, 'salad': np.mean, 'shake': np.mean, 'hour': np.mean, 'store_1.0': sum, 'store_4.0': sum, 'store_6.0': sum, 'store_3.0': sum, 'store_9.0': sum, 'store_2.0': sum, 'store_8.0': sum, 'store_5.0': sum, 'store_7.0': sum}
col_output_order = ['burger', 'fries', 'salad', 'shake', 'hour', 'store_1.0', 'store_2.0', 'store_3.0', 'store_4.0', 'store_5.0', 'store_6.0', 'store_7.0', 'store_8.0', 'store_9.0'] ##### specify order of output columns for easy of readability

# training data
train_model, train_model_summary = run_kmeans(n_clusters, init_point_selection_method, df_cluster_train.reindex())
# testing data
test_model, test_model_summary = run_kmeans(n_clusters, init_point_selection_method, df_cluster_test.reindex())
# all data
model, model_summary = run_kmeans(n_clusters, init_point_selection_method, df_cluster)

# --- run for various number of clusters
##### add the code to run the clustering algorithm for various numbers of clusters
wcss = []
for i in range(1,10):
    kmeans = KMeans(n_clusters=i, init=init_point_selection_method).fit(df_cluster)
    wcss.append(kmeans.inertia_)

# --- draw elbow plot
##### create an elbow plot for your numbers of clusters in previous step
plt.plot(range(1, 10), wcss)
plt.title('Elbow Method')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.show()

# --- output tagged data for examination ----
store_col_names = ['store_1.0', 'store_2.0', 'store_3.0', 'store_4.0', 'store_5.0', 'store_6.0', 'store_7.0', 'store_8.0', 'store_9.0']
df_cluster['store'] = None
for t_col in store_col_names:
    df_cluster.loc[df_cluster[t_col] == 1, 'store'] = t_col.split('_')[1]
#df_cluster['store'] = df_cluster['store'].astype(int)
df_cluster.to_csv('clustering_output.csv')
print(df_cluster.head())

# assign cluster mode to location
df_transactions['location'] = df_transactions['location'].astype(str)
df_transactions['lat'] = df_transactions['lat'].astype(float)
df_transactions['long'] = df_transactions['long'].astype(float)


t_df = df_cluster.groupby('store')['predict_cluster_kmeans'].apply(lambda x: x.mode()).reset_index()[['store', 'predict_cluster_kmeans']]



df_transactions[['location', 'lat', 'long']].drop_duplicates().merge(t_df, how='left', left_on='location', right_on='store').to_csv('store_locations.csv')

# ---- Bonus code (not part of assignment) ------
# GMM
gmm_model = GaussianMixture(n_components=3, covariance_type='full')
gmm_predicted_cluster = gmm_model.fit_predict(df_cluster)
df_cluster['predict_cluster_gmm'] = gmm_predicted_cluster
gmm_model.weights_
gmm_model.means_
gmm_model.converged_
gmm_model_summary = df_cluster.groupby('predict_cluster_gmm').agg(attribute_summary_method_dict)
gmm_model_summary[col_output_order].to_csv('gmm_cluster_summary.csv')
