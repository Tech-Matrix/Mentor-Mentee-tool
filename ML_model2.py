from project import db
from project.models import User, Mentor, Mentee
import pandas as pd
import numpy as np
import string
import gower
from math import radians, cos, sin, asin, sqrt
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from nltk.corpus import stopwords

def model():

    stop_words = stopwords.words('english')


    def clean_string(text):
        text = ''.join([word for word in text if word not in string.punctuation])
        text = text.lower()
        text = ' '.join([word for word in text.split() if word not in stop_words])
        return text


    def cosine_diff_vectors(vectors):
        v1 = vectors[0]
        v2 = vectors[1]
        v1 = v1.reshape(1, -1)
        v2 = v2.reshape(1, -1)
        return 1-cosine_similarity(v1, v2)[0][0]


    def distance(lat1, lat2, lon1, lon2):
        # The math module contains a function named
        # radians which converts from degrees to radians.
        lon1 = radians(lon1)
        lon2 = radians(lon2)
        lat1 = radians(lat1)
        lat2 = radians(lat2)

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

        c = 2 * asin(sqrt(a))

        # Radius of earth in kilometers. Use 3956 for miles
        r = 6371

        # calculate the result
        return c*r

    max_dist_between_coordinates = distance(0, 0, 0, 180)

    # mentors = Mentor.query.all()
    # mentees = Mentee.query.all()
    users = User.query.all()

    dict = {"id":[], "role":[], "hobbies":[], "interest":[], "lat":[], "long":[], "time":[],
            "bq1":[], "bq2":[]}

    # for mentor in mentors:
    #     dict["id"].append(mentor.user_id)
    #     dict["role"].append("MENTOR")
    #     dict["hobbies"].append(clean_string(mentor.hobbies)+" ")
    #     dict["lat"].append(mentor.lat)
    #     dict["long"].append(mentor.long)
    #     dict["time"].append(mentor.time_delta+12)
    #     dict["interest"].append(mentor.expertise_1+" ")
    #     dict["bq1"].append(clean_string(mentor.bq_1)+" ")
    #     dict["bq2"].append(clean_string(mentor.bq_2)+" ")
    #
    # for mentee in mentees:
    #     dict["id"].append(mentee.user_id)
    #     dict["role"].append("MENTEE")
    #     dict["hobbies"].append(clean_string(mentee.hobbies)+" ")
    #     dict["lat"].append(mentee.lat)
    #     dict["long"].append(mentee.long)
    #     dict["time"].append(mentee.time_delta+12)
    #     dict["interest"].append(mentee.aspiration+" ")
    #     dict["bq1"].append(clean_string(mentee.bq_1)+" ")
    #     dict["bq2"].append(clean_string(mentee.bq_2)+" ")

    for user in users:
        if user.urole == "MENTOR":
            mentor = user.mentor
            dict["id"].append(mentor.user_id)
            dict["role"].append("MENTOR")
            dict["hobbies"].append(clean_string(mentor.hobbies)+" ")
            dict["lat"].append(mentor.lat)
            dict["long"].append(mentor.long)
            dict["time"].append(mentor.time_delta+12)
            dict["interest"].append(mentor.expertise_1+" ")
            dict["bq1"].append(clean_string(mentor.bq_1)+" ")
            dict["bq2"].append(clean_string(mentor.bq_2)+" ")

        elif user.urole == "MENTEE":
            mentee = user.mentee
            dict["id"].append(mentee.user_id)
            dict["role"].append("MENTEE")
            dict["hobbies"].append(clean_string(mentee.hobbies)+" ")
            dict["lat"].append(mentee.lat)
            dict["long"].append(mentee.long)
            dict["time"].append(mentee.time_delta+12)
            dict["interest"].append(mentee.aspiration+" ")
            dict["bq1"].append(clean_string(mentee.bq_1)+" ")
            dict["bq2"].append(clean_string(mentee.bq_2)+" ")


    all_df = pd.DataFrame(dict)
    df = all_df.drop(["id", "role"], axis=1)

    temp_df = df[["lat", "long", "time"]]
    df.drop(["lat", "long", "time"], axis=1, inplace=True)

    scaler = MinMaxScaler()
    temp_df = pd.DataFrame(
            scaler.fit_transform(temp_df),
            columns=temp_df.columns
        )
    df = df.join(temp_df)
    # print(df)
    # print(df.columns)


    df["text"] = df["interest"]+df["hobbies"]+df["bq1"]+df["bq2"]
    df.drop(["hobbies", "interest", "bq1", "bq2"], axis=1, inplace=True)
    # print(df)
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(df["text"])
    df_wrds = pd.DataFrame(vectors.toarray(), columns=vectorizer.get_feature_names())
    new_df = pd.concat([df, df_wrds], axis=1)
    new_df.drop(["text"], axis=1, inplace=True)


    pca = PCA()
    df_pca = pca.fit_transform(new_df)
    # Plotting to determine how many features should the dataset be reduced to
    plt.style.use("bmh")
    plt.figure(figsize=(14,14))
    plt.plot(range(1,df_pca.shape[0]+1), pca.explained_variance_ratio_.cumsum())
    # plt.show()

    # Finding the exact number of features that explain at least 95% of the variance in the dataset
    total_explained_variance = pca.explained_variance_ratio_.cumsum()
    n_over_95 = len(total_explained_variance[total_explained_variance>=.95])
    n_to_reach_95 = df_pca.shape[1] - n_over_95

    # Printing out the number of features needed to retain 95% variance
    # print(f"Number features: {n_to_reach_95}\nTotal Variance Explained: {total_explained_variance[n_to_reach_95]}")

    # Reducing the dataset to the number of features determined before
    pca = PCA(n_components=n_to_reach_95)

    # Fitting and transforming the dataset to the stated number of features and creating a new DF
    df_pca = pca.fit_transform(new_df)

    # Seeing the variance ratio that still remains after the dataset has been reduced
    # print(pca.explained_variance_ratio_.cumsum()[-1])

    # Setting the amount of clusters to test out
    cluster_cnt = [i for i in range(2, 20, 1)]

    # Establishing empty lists to store the scores for the evaluation metrics
    s_scores = []

    db_scores = []

    # Looping through different iterations for the number of clusters
    for i in cluster_cnt:
        # Hierarchical Agglomerative Clustering with different number of clusters
        hac = AgglomerativeClustering(n_clusters=i)

        hac.fit(df_pca)

        cluster_assignments = hac.labels_

        ## KMeans Clustering with different number of clusters
        # k_means = KMeans(n_clusters=i)

        # k_means.fit(df_pca)

        # cluster_assignments = k_means.predict(df_pca)

        # Appending the scores to the empty lists
        s_scores.append(silhouette_score(df_pca, cluster_assignments))

        db_scores.append(davies_bouldin_score(df_pca, cluster_assignments))


    # def plot_evaluation(y, x=cluster_cnt):
    #     """
    #     Plots the scores of a set evaluation metric. Prints out the max and min values of the evaluation scores.
    #     """
    #
    #     # Creating a DataFrame for returning the max and min scores for each cluster
    #     df = pd.DataFrame(columns=['Cluster Score'], index=[i for i in range(2, len(y) + 2)])
    #     df['Cluster Score'] = y
    #
    #     print('Max Value:\nCluster #', df[df['Cluster Score'] == df['Cluster Score'].max()])
    #     print('\nMin Value:\nCluster #', df[df['Cluster Score'] == df['Cluster Score'].min()])
    #
    #     # Plotting out the scores based on cluster count
    #     plt.figure(figsize=(16, 6))
    #     plt.style.use('ggplot')
    #     plt.plot(x, y)
    #     plt.xlabel('# of Clusters')
    #     plt.ylabel('Score')
    #     plt.show()


    # Running the function on the list of scores
    # plot_evaluation(s_scores)
    #
    # plot_evaluation(db_scores)


    # Instantiating HAC
    hac = AgglomerativeClustering(n_clusters=5)

    # Fitting
    hac.fit(df_pca)

    # Getting cluster assignments
    cluster_assignments = hac.labels_
    print(cluster_assignments)

    # Unscaling the categories then replacing the scaled values
    df = df[['text']].join(pd.DataFrame(scaler.inverse_transform(df.drop('text', axis=1)), columns=df.columns[:-1], index=df.index))

    # Assigning the clusters to each profile
    df['Cluster #'] = cluster_assignments

    # Viewing the dating profiles with cluster assignments
    # print(df)
    # print(df.columns)
    return df







# vectors = vectorizer.transform(["Sergio Perez is a World champion", "Pancakes is my favourite food"]).toarray()
# print(cosine_diff_vectors(vectors))







#
# df = df[["id", "role", "hobbies", "interest", "bq1", "bq2"]].join(
#     pd.DataFrame(
#         scaler.fit_transform(df.drop(["id", "role", "hobbies", "interest", "bq1", "bq2"], axis=1)),
#         columns=df[1:],
#         index=df.index
#     )
# )
# print(df)