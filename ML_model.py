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
from nltk.corpus import stopwords


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

mentors = Mentor.query.all()
mentees = Mentee.query.all()

dict = {"id":[], "role":[], "hobbies":[], "interest":[], "lat":[], "long":[], "time":[],
        "bq1":[], "bq2":[]}

for mentor in mentors:
    dict["id"].append(mentor.user_id)
    dict["role"].append("MENTOR")
    dict["hobbies"].append(mentor.hobbies)
    dict["lat"].append(mentor.lat)
    dict["long"].append(mentor.long)
    dict["time"].append(mentor.time_delta+12)
    dict["interest"].append(mentor.expertise_1)
    dict["bq1"].append(mentor.bq_1)
    dict["bq2"].append(mentor.bq_2)

for mentee in mentees:
    dict["id"].append(mentee.user_id)
    dict["role"].append("MENTEE")
    dict["hobbies"].append(mentee.hobbies)
    dict["lat"].append(mentee.lat)
    dict["long"].append(mentee.long)
    dict["time"].append(mentee.time_delta+12)
    dict["interest"].append(mentee.aspiration)
    dict["bq1"].append(mentee.bq_1)
    dict["bq2"].append(mentee.bq_2)

df = pd.DataFrame(dict)

vectorizer = CountVectorizer()
words = df["hobbies"].tolist()+df["interest"].tolist()+df["bq1"].tolist()+df["bq2"].tolist()
vectorizer.fit(words)
vectors = vectorizer.transform(["Sergio Perez is a World champion", "Pancakes is my favourite food"]).toarray()
print(cosine_diff_vectors(vectors))

distance_matrix = np.zeros([df.shape[0], df.shape[0]])
for i in range(distance_matrix.shape[0]):
    for j in range(distance_matrix.shape[1]):
        dist = 0
        if i != j:
            dist += (1/3)*cosine_diff_vectors(vectorizer.transform([df["hobbies"][i], df["hobbies"][j]]).toarray())
            dist += cosine_diff_vectors(vectorizer.transform([df["interest"][i], df["interest"][j]]).toarray())
            dist += (1/3)*cosine_diff_vectors(vectorizer.transform([df["bq1"][i], df["bq1"][j]]).toarray())
            dist += (1/3)*cosine_diff_vectors(vectorizer.transform([df["bq2"][i], df["bq2"][j]]).toarray())
            dist += min(abs(df["time"][i]-df["time"][j]), 24-abs((df["time"][i]-df["time"][j])))/12
            dist += distance(df["lat"][i], df["lat"][j], df["long"][i], df["long"][j])/max_dist_between_coordinates
            distance_matrix[i][j] = dist/4
    if i%10==0:
        print(i)

print(distance_matrix)
# for i in range(distance_matrix.shape[0]):
#     for j in range(distance_matrix.shape[1]):
#         if distance_matrix[i][j] >0.05 and distance_matrix[i][j] < 0.6:
#             print(distance_matrix[i][j])

clustering = DBSCAN(eps=0.481, min_samples=1, metric="precomputed").fit(distance_matrix)
print(clustering.labels_)
