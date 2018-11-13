'''reads the input data (users and media) and creates a ratings matrix
from that information. the data is also split into train and test sets
within this file'''
from __future__ import absolute_import, division, print_function,\
   unicode_literals
import warnings
import generate_users
import generate_media
import generate_ratings
import vars
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")


def get_input_data(bucket,key, num_users, media_per_user):
    '''generate users, media, ratings'''
    users = generate_users.generate_users(count=vars.NUM_USERS)
    media = generate_media.generate(bucket=vars.DATA_BUCKET, key=vars.DATA_KEY)
    usr_ratings, users, names, media_averages = generate_ratings.\
        generate(users, media, count=vars.NUM_ITEMS)
    decoded_media = generate_media.decode(media, media_averages)
    ratings_matrix, lookup = generate_ratings.\
        create_ratings_matrix(usr_ratings, names, media)
    return media, usr_ratings, users, names,\
        ratings_matrix, decoded_media, lookup


def train_test_split(ratings_matrix, test_split_ratio):
    '''split matrices into tain and test data sets'''
    split = int(ratings_matrix.shape[0] - ((test_split_ratio / 100) *
                ratings_matrix.shape[0]))
    train_data = ratings_matrix[:split]
    test_data = ratings_matrix[split:]
    return train_data, test_data
