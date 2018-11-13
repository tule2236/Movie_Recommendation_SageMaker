'''this file contains all the sagemaker logic'''
from __future__ import absolute_import, division, print_function,\
    unicode_literals
import warnings
import boto3
import numpy as np
from preprocess import get_input_data, train_test_split
import formatting
import generate_superlatives
from sagemaker.tensorflow import TensorFlow
import sagemaker
# import tensorflow as tf
import vars
import recommendations

warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")


class SMLearner:
    '''defines a class for starting the training/prediction process.'''
    def __init__(self, num_clusters, test_split_ratio):
        '''initialize an sm_learner instance'''
        self.num_clusters = num_clusters
        self.test_split_ratio = test_split_ratio

    def process_input_data(self, bucket,key, n_users, n_media):
        '''gather input data and process for training'''
        self.media, self.usr_ratings, self.users, self.names,\
            self.ratings_matrix, self.decoded_media,\
            self.lookup = get_input_data(bucket=vars.DATA_BUCKET, key=vars.DATA_KEY,
                                         num_users=vars.NUM_USERS,
                                         media_per_user=vars.NUM_MEDIA)

    def process_metrics(self, labels):
        '''calculate superlatives from given data'''
        self.final = formatting.format_data(self.usr_ratings, self.names,
                                       self.ratings_matrix,
                                       self.decoded_media, self.num_clusters,
                                       labels)
        
        recommendations.write_data(self.final)
        
        top_users, bottom_users = generate_superlatives.\
            users_highest_lowest_ratings(self.final)
        top_media_per_group, bottom_media_per_group = generate_superlatives.\
            best_worst_media_per_group(self.final)
        generate_superlatives.write_superlatives(top_users, bottom_users,
                                                 top_media_per_group,
                                                 bottom_media_per_group)

    def split_ratings_matrix(self):
        '''process and split the matrix of user ratings given the ratio of
        the dataset used for evaluation'''
        train, test = train_test_split(self.ratings_matrix,
                                       self.test_split_ratio)
        return train, test

    def upload_train_test_data_to_s3(self, train, test):
        '''obtains the training file from s3'''
        # Save the train and test data locally
        np.savetxt(vars.TRAIN_CSV_LOC, train, delimiter=",")
        np.savetxt(vars.TEST_CSV_LOC, test, delimiter=",")
        # Upload the files to the s3 bucket
        self.upload_file_to_s3(vars.TRAIN_CSV_LOC,
                               vars.TRAIN_CSV_S3)
        self.upload_file_to_s3(vars.TEST_CSV_LOC,
                               vars.TEST_CSV_S3)

    def upload_file_to_s3(self, src, dest):
        '''upload the training file to s3'''
        # Upload file to s3 bucket
        session = boto3.session.Session()
        bucket = session.resource('s3').Bucket(vars.BUCKET_NAME)
        bucket.upload_file(src, dest)

    def fit_and_deploy(self):
        '''trains the model created from our entry-point'''
        # Bucket location to save your custom code in tar.gz format.
        vars.CODE_UPLOAD_PATH = vars.CODE_UPLOAD_PATH.\
            format(vars.BUCKET_NAME)
        # Bucket location where results of model training are saved.
        vars.ARTIFACTS_PATH = vars.ARTIFACTS_PATH.\
            format(vars.BUCKET_NAME)
        self.estimator = TensorFlow(
            entry_point=vars.ENTRY_POINT_SCRIPT,
            role=sagemaker.get_execution_role(),
            output_path=vars.ARTIFACTS_PATH,
            code_location=vars.CODE_UPLOAD_PATH,
            train_instance_count=vars.TRAIN_INSTANCE_COUNT,
            train_instance_type=vars.TRAIN_INSTANCE_TYPE,
            training_steps=vars.TRAINING_STEPS,
            evaluation_steps=vars.EVALUATION_STEPS,
            hyperparameters={'num_clusters': self.num_clusters}
        )
        self.estimator.fit(str(vars.TRAINING_DATA_PATH), wait=False)
        self.predictor = self.estimator.\
            deploy(initial_instance_count=vars.TRAIN_INSTANCE_COUNT,
                   instance_type=vars.TRAIN_INSTANCE_TYPE)

    # def predict_clusters(self, n_users, n_media):
    #     '''obtain inference results from the endpoint'''
    #     # self.process_input_data(raw_data_path=vars.RAW_DATA_PATH,
    #     #                         n_users=vars.NUM_USERS,
    #     #                         n_media=vars.NUM_MEDIA)
    #     mtx = tf.make_tensor_proto(values=self.ratings_matrix,
    #                                shape=list(self.ratings_matrix.shape),
    #                                dtype=tf.float32)
    #     result = self.predictor.predict(mtx)
    #     # cluster_int64 = result['outputs']['output']['int64_val']
    #     cluster_int64 = result['outputs']['output']['int64Val']
    #     clusters = map(int, cluster_int64)
    #     return clusters
