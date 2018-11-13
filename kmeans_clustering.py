""" Generate module for all data """
from __future__ import absolute_import, division, print_function, \
    unicode_literals
import os
import warnings
import numpy as np
import tensorflow as tf

warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")


INPUT_TENSOR_NAME = "inputs"


def estimator_fn(run_config, params):
    '''this function is used by sagemaker'''
    return tf.contrib.factorization.KMeansClustering(num_clusters=
                                                     params['num_clusters'],
                                                     use_mini_batch=False,
                                                     feature_columns=None,
                                                     config=run_config)


def serving_input_fn(params):
    '''this function is used by sagemaker'''
    tensor = tf.placeholder(tf.float32, shape=[None, None])
    return tf.estimator.export.build_raw_serving_input_receiver_fn(
        {INPUT_TENSOR_NAME: tensor})()


def train_input_fn(training_dir, params):
    """ Returns input function that would feed the model during training """
    return generate_input_fn(training_dir, 'train.csv')


def eval_input_fn(training_dir, params):
    """ Returns input function that would feed the model during evaluation """
    return generate_input_fn(training_dir, 'test.csv')


def generate_input_fn(training_dir, training_filename):
    """ Generate all the input data needed to train and evaluate the model. """
    # Load train/test data from s3 bucket
    train = np.loadtxt(os.path.join(training_dir, training_filename),
                       delimiter=",")
    return tf.estimator.inputs.numpy_input_fn(
        x={INPUT_TENSOR_NAME: np.array(train, dtype=np.float32)},
        y=None,
        num_epochs=1,
        shuffle=False)()
