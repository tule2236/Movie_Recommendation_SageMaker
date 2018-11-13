'''calculate and output recommendations'''
import csv
import numpy as np
import boto3
import pandas as pd
from scipy.stats import pearsonr
import vars

def convert_df_to_json(df):    
    jsonFile = df.to_json(orient='records')
    return jsonFile

def write_data(formatted_list):
    """
    Write data in to the data.csv file in the dashboard/data
    directory.
    Each media rating is a separate entry with the
    following headers:
    name, group, media (id), rating
    """
    df = pd.DataFrame(formatted_list, columns=["name", "group", "mediaId", "title", "rating"])  
    jsonFile=convert_df_to_json(df)
    
    client = boto3.client('s3')
    client.put_object(Body=bytes(jsonFile.encode('utf-8')), Bucket=vars.DATA_BUCKET, Key=vars.JSON_DATA)   


def rank_user_similarity(target_user_idx, ratings_matrix, kmeans, labels=None):
    """ Ranks medias within a group based on how similar a single
    target users tastes are to each group members tastes.
    This "similarity" is determined using the
    Pearson Correlation Coefficient."""
    corr_values = {}
    # Ranking medias for current and new users
    # Get users in the same cluster as our target user
    if labels is None:
        users_in_group = np.where(kmeans == kmeans[
            target_user_idx])[0]
    # else:
    #     """this case is for new users functionality"""
    #     users_in_group = np.where(labels == kmeans.labels_[target_user_idx])
    #                                                       [0]
    target_usr_ratings_vector = ratings_matrix[target_user_idx, :]
    for u_idx in users_in_group:
        if target_user_idx != u_idx:
            user_ratings_vector = ratings_matrix[u_idx, :]
            # Ignore columns with zeros when calculating Pearson Correlation
            delete_idxs = []
            for i in range(user_ratings_vector.size):
                if (user_ratings_vector[i] == 0 or
                        target_usr_ratings_vector[i] == 0):
                    delete_idxs.append(i)
            # Calculate the pearson coefficients
            usr_ratings_vector_dense = np.delete(user_ratings_vector,
                                                 delete_idxs)
            target_ratings_vector_dense = np.delete(target_usr_ratings_vector,
                                                    delete_idxs)
            corr_value = pearsonr(usr_ratings_vector_dense,
                                  target_ratings_vector_dense)
            corr_values[u_idx] = corr_value[0]

    # Sort the coefficients in descending order and return the list
    return list(sorted(corr_values.items(), key=lambda d: d[1], reverse=True))


# *** UNUSED ****
def recommend_media(sorted_corr_values, target_user_idx, ratings_matrix):
    """ Recommend medias to the target users """
    target_usr_ratings_vector = ratings_matrix[target_user_idx, :]
    recommended_media = []
    reco_count = 0
    top_n_neighbors = 0
    for corr in sorted_corr_values:
        if top_n_neighbors >= vars.TOP_N_NEIGHBORS:
            break
        u_idx = corr[0]
        u_vector = ratings_matrix[u_idx, :]
        # Add media this user has seen but the target user has not and
        # only recommend media that are rated >= RECOM_THRESHOLD from this
        # user
        # TODO: Calculate missing ratings for target user by averaging
        # other users ratings for the missing media of the target user.
        # Also we may want to sort the media in the "recommend" variable
        # by ratings.
        idxs1 = np.where(u_vector >= vars.RECOM_THRESHOLD)[0]
        idxs2 = np.where(target_usr_ratings_vector == 0.)[0]
        recommend = np.intersect1d(idxs1, idxs2)
        # Intersection of the two lists (sorted)
        reco_count = reco_count + recommend.size
        # Count how many media we found with a score > 8
        recommended_media.extend(recommend.tolist())
        top_n_neighbors += 1

    return recommended_media


def recommend_curr_users(users, ratings_matrix, kmeans, lookup, k):
    """ make recommendations for current users (see if they exist)"""
    # Check if user exists
    recommendations = {}
    for target_user in users:
        target_user_idx = lookup.user_to_idx[target_user]
        # A list of user "u"'s top k or less recommendations
        # Add each users list of recomms to the recommendations dict
        sorted_corr_values = rank_user_similarity(target_user_idx,
                                                  ratings_matrix, kmeans)
        user_recos = recommend_media(sorted_corr_values,
                                     target_user_idx, ratings_matrix)
        recommendations[str(target_user)] = user_recos[:k]
    return recommendations


def generate_recommendations(media, names, formatted_list,ratings_matrix, kmeans, lookup):
    """ Recommend media for a list of users """
    recomm_media = recommend_curr_users(names, ratings_matrix, kmeans,
                                        lookup, vars.TOP_K)
    write_recommendations(recomm_media, media, formatted_list)
    return recomm_media

def convert_csv_to_json(df):    
    jsonFile = df.to_json(orient='records')
    return jsonFile

def write_recommendations(recs, media, formatted_list):
    """ write recommendations to a csv for reading by the dashboard """
    out = {}

    for row in formatted_list:
        if row[0] not in out.keys():
            cur_rec_id = recs[row[0]]            
            cur_rec_title = []               
            for med in cur_rec_id:
                cur_rec_title.append(media.loc[med,
                                               vars.TITLE_FIELD])
            out[row[0]] = [row[1]]  # group             
            out[row[0]].append(cur_rec_title) # recommendation
            out[row[0]].append(row[3])
                
    df = pd.DataFrame(columns=['name', 'group', 'recommendations','past_usage'])   
    ct = 0
    for key, value in out.items():
        df.at[ct,'name'] = key
        df.at[ct,'group'] = value[0]
        df.at[ct,'recommendations'] = value[1]
        df.at[ct,'past_usage'] = list(value[2:])
        ct += 1
        
    jsonFile=convert_csv_to_json(df)
    
    client = boto3.client('s3')
    client.put_object(Body=bytes(jsonFile.encode('utf-8')), Bucket=vars.DATA_BUCKET, Key=vars.JSON_REC)

# MEDIA, NAMES, RATINGS_MATRIX, KMEANS, LOOKUP = generate_data()
# generate_recommendations(MEDIA, NAMES, RATINGS_MATRIX, KMEANS, LOOKUP)
