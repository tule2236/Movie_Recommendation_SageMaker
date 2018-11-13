'''generarte interesting superlatives for the dashboard'''
import csv
import vars
import boto3
import pandas as pd

def users_highest_lowest_ratings(final):
    """ calculate users with top 10 highest ratings
    users with top 10 lowest ratings
    """
    ratings = {}
    for line in final:
        if line[0] in ratings.keys():
            ratings[line[0]].append(line[4])
        else:
            ratings[line[0]] = [line[4]]
    averages = {}
    for (name, rating_list) in ratings.items():
        avg = 0
        for rate in rating_list:
            avg += rate
        avg = avg/len(rating_list)
        averages[name] = avg
    sorted_avgs = sorted(averages.items(), key=lambda x: x[1])
    top_ten = {}
    bottom_ten = {}
    for i in range(10):
        bottom_ten[sorted_avgs[i][0]] = sorted_avgs[i][1]
        line = i + 1
        top_ten[sorted_avgs[-line][0]] = sorted_avgs[-line][1]
    return (top_ten, bottom_ten)


def best_worst_media_per_group(final):
    '''
    calculate top media for each kmeans group and
    bottom media for each kmeans group (most liked
    and least liked, on average)
    '''
    groups_media = {}
    for line in final:
        if line[1] in groups_media:
            if line[3] in groups_media[line[1]]:
                groups_media[line[1]][line[3]].append(line[4])
            else:
                groups_media[line[1]][line[3]] = [line[4]]
        else:
            groups_media[line[1]] = {line[3]: [line[4]]}
    for group in groups_media:
        for media in groups_media[group]:
            avg = 0
            for rating in groups_media[group][media]:
                avg += rating
            avg = avg / len(groups_media[group][media])
            groups_media[group][media] = avg
    for group in groups_media:
        sorted_group_media = sorted(groups_media[group].items(),
                                    key=lambda x: x[1])
        groups_media[group] = sorted_group_media
    top_media_per_group = {}
    bottom_media_per_group = {}
    for group in groups_media:
        bottom = {}
        top = {}
        for i in range(10):
            bottom[groups_media[group][i][0]] = groups_media[group][i][1]
            line = i + 1
            top[groups_media[group][-line][0]] = groups_media[
                group][-line][1]
        top_media_per_group[group] = top
        bottom_media_per_group[group] = bottom
    return (top_media_per_group, bottom_media_per_group)

def convert_df_to_json(df):    
    jsonFile = df.to_json(orient='records')
    return jsonFile

def write_superlatives(top_ten, bottom_ten,
                       top_media_per_group,
                       bottom_media_per_group,
                       path_prefix=vars.JSON_SUPERLATIVES):
    ''' docstring'''
    client = boto3.client('s3')
    
    ###################################################################
    ## TOP_TEN_USER
    top_rating_user = pd.DataFrame(columns=["rank", "name", "value"])   
    rank= 1
    ct = 0
    for key, value in top_ten.items():
        top_rating_user.at[ct,'rank'] = str(rank)
        top_rating_user.at[ct,'name'] = key
        top_rating_user.at[ct,'value'] = value
        rank += 1   
        ct += 1
    top_rating_user = convert_df_to_json(top_rating_user)       
    client.put_object(Body=bytes(top_rating_user.encode('utf-8')), Bucket=vars.JSON_BUCKET, Key=path_prefix+vars.TOP_RATING_USERS_PATH)
    
    ###################################################################
    ## BOTTOM_TEN_USER
    bottom_rating_user = pd.DataFrame(columns=["rank", "name", "value"])   
    rank= 1
    ct = 0
    for key, value in bottom_ten.items():
        bottom_rating_user.at[ct,'rank'] = str(rank)
        bottom_rating_user.at[ct,'name'] = key
        bottom_rating_user.at[ct,'value'] = value
        rank += 1  
        ct += 1
    bottom_rating_user=convert_df_to_json(bottom_rating_user)       
    client.put_object(Body=bytes(bottom_rating_user.encode('utf-8')), Bucket=vars.JSON_BUCKET, Key=path_prefix+vars.BOTTOM_RATING_USERS_PATH)
    
    ###################################################################
    ## TOP_MEDIA_PER_GROUP
    top_per_group = pd.DataFrame(columns=["group", "rank", "title", "value"]) 
    ct = 0 
    for group, _ in top_media_per_group.items():
            i = 1
            for media, rating in top_media_per_group[group].items():
                top_per_group.at[ct, "group"] = str(group)
                top_per_group.at[ct, "rank"] = str(i)
                top_per_group.at[ct, "title"] = media
                top_per_group.at[ct, "value"] = rating
                i += 1
                ct += 1
    top_per_group = convert_df_to_json(top_per_group) 
    client.put_object(Body=bytes(top_per_group.encode('utf-8')), Bucket=vars.JSON_BUCKET, Key=path_prefix+vars.TOP_PER_GROUP_PATH)
    
    ###################################################################
    ## BOTTOM_MEDIA_PER_GROUP    
    bottom_per_group = pd.DataFrame(columns=["group", "rank", "title", "value"]) 
    ct = 0 
    for group, _ in bottom_media_per_group.items():
            i = 1
            for media, rating in bottom_media_per_group[group].items():
                bottom_per_group.at[ct, "group"] = str(group)
                bottom_per_group.at[ct, "rank"] = str(i)
                bottom_per_group.at[ct, "title"] = media
                bottom_per_group.at[ct, "value"] = rating
                i += 1
                ct += 1
    bottom_per_group = convert_df_to_json(bottom_per_group) 
    client.put_object(Body=bytes(bottom_per_group.encode('utf-8')), Bucket=vars.JSON_BUCKET, Key=path_prefix+vars.BOTTOM_PER_GROUP_PATH)
