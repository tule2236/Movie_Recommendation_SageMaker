'''generate fake ratings of media users'''
import random
import collections
import numpy as np
import vars


def generate(users, media, count=vars.NUM_ITEMS):
    """ Generate random ratings for users. Should eventually parse tmdb for
    real data to cache, but for now and possibly for test cases for
    expediency, randomizing this. """
    weights = media[vars.MEDIA_POPULARITY_FIELD]
    names = []
    usr_ratings = []
    media_ratings = {}
    media_averages = {}

    # Create an empty users x medias matrix used to store media ratings
    for user in users:
        consumed_media = media.sample(n=count, weights=weights)
        ratings = {}
        for media_idx in consumed_media.index:
            # user liking media should be consistent with popularity and avg
            # ratings, so fit a distribution on 1-10 :)
            average = media.iloc[media_idx][vars.AVG_RATING_FIELD]
            rating = max(min(10, average + random.gauss(0, 1)), 0)
            ratings[media.iloc[media_idx][vars.MEDIA_ID_FIELD]] = \
                rating
        user['ratings'] = ratings
        names.append(user['name'])
        usr_ratings.append(ratings)
        for med_id, value in ratings.items():
            if med_id in media_ratings:
                media_ratings[med_id].append(value)
            else:
                media_ratings[med_id] = [value]
    for med_id, r_list in media_ratings.items():
        avg = 0
        for rat in r_list:
            avg += rat
        avg = avg / len(r_list)
        media_averages[med_id] = avg
    return usr_ratings, users, names, media_averages


def create_ratings_matrix(usr_ratings, names, d_frame):
    """ Create the ratings matrix that will be used
    for training and predictions.
    """
    user_idx = 0
    r_mtx = np.zeros((len(names), d_frame.shape[0]), dtype=np.float32)
    user_to_idx = {}
    idx_to_user = {}
    for u_r in usr_ratings:
        for tmdb_id in u_r.keys():
            media_idx = d_frame[d_frame[vars.MEDIA_ID_FIELD] == tmdb_id].index[0]
            # media_idx = d_frame[d_frame[vars.MEDIA_ID_FIELD]
            #                     == tmdb_id].index[0]
            r_mtx[user_idx, media_idx] = u_r[tmdb_id]

        # Build user indexes
        user_to_idx[names[user_idx]] = user_idx
        idx_to_user[user_idx] = names[user_idx]
        user_idx += 1

    lookup_table = create_mapping(user_to_idx, idx_to_user)
    return r_mtx, lookup_table


def create_mapping(u_to_i, i_to_u):
    """ create mapping """
    return IndexLookup(u_to_i, i_to_u)


IndexLookup = collections.namedtuple('IndexLookup', ['user_to_idx',
                                                     'idx_to_user'])
