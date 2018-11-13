'''train the data and deploy the endpoint on Sagemaker.
This will be run only once.'''
from __future__ import absolute_import, division, print_function,\
    unicode_literals
import warnings
from sm_learner import SMLearner
import vars
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")


def train_and_deploy():
    '''this function orchestrates the initial deployment to sagemaker'''
    learner = SMLearner(num_clusters=vars.NUM_CLUSTERS,
                        test_split_ratio=vars.TEST_SPLIT_RATIO)
    learner.process_input_data(raw_data_path=vars.RAW_DATA_PATH,
                               n_users=vars.NUM_USERS,
                               n_media=vars.NUM_MEDIA)
    train, test = learner.split_ratings_matrix()
    learner.upload_train_test_data_to_s3(train, test)
    # learner.fit_and_deploy()
    # user_clusters = learner.predict_clusters(n_users=vars.NUM_USERS,
    #                                          n_media=vars.NUM_MEDIA)
    # print('Prediction array:\n\n{}'.format(user_clusters))
    # learner.process_metrics(labels=user_clusters)


def lambda_handler(event, context):
    train_and_deploy()