'''this function will be called for subsequent predictions (for new users)'''
from __future__ import absolute_import, division, print_function,\
    unicode_literals
import codecs
import json
import boto3
from sm_learner import SMLearner
import vars
def new_user():
    '''predict the clusters for new users'''
    # Example of calling the prediction endpoint via boto3
    # The parameters passed to SMLearner() don't do anything since we are not
    # training the model again
    learner = SMLearner(num_clusters=vars.NUM_CLUSTERS,
                        test_split_ratio=25)
    learner.process_input_data(raw_data_path=vars.RAW_DATA_PATH,
                               n_users=vars.NUM_USERS,
                               n_media=vars.NUM_MEDIA)
    # Convert the numpy array to a list of lists then to a json file
    b = learner.ratings_matrix.tolist()
    # Numpy array to nested lists with same data, indices
    file_path = "path.json"  # Path to dest json file
    json.dump(b, codecs.open(file_path, 'w', encoding='utf-8'),
              separators=(',', ':'), sort_keys=True, indent=4)
    # This saves the python list in .json format
    f = open("path.json", "r")
    # Invoke the endpoint via boto3
    # Must get the endpoint name
    c = boto3.client('sagemaker-runtime')
    response = c.invoke_endpoint(
        EndpointName='sagemaker-tensorflow-2018-08-27-14-36-07-416', Body=f)
    # Print the clusters
    print('Body:\n', response)
    result = response['Body'].read()
    print('Prediction result:\n', result)
    json_result = json.loads(result, encoding='utf-8')
    clusters_unicode = json_result['outputs']['output']['int64Val']
    clusters_int = map(int, clusters_unicode)
    print('Clusters:\n', clusters_int)


new_user()
