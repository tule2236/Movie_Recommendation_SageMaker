## Training and prediction in Sagemaker using Tensorflow ##

SageMaker is a machine learning service that enables users to build, train and deploy
machine learning models. Inference requests can then be made to the service
which  can be intergrated into the users applications.

### Workflow: ###

Preprocess the data
* In our case we call the function in the `generate.py` and `preprocess.py` modules
  and receive a training and testing set from the original data collected from TMDB..
* The train and test data must then be uploaded to an s3 bucket where SageMaker can
  access and use them for training and evaluation.
* For our purposes we will combine and transform the TMDB movie and user data into a
  matrix of ratings. Each row represents a user and each column a movie. Each cell in the matrix
  is a users rating for the corresponding movie.

Train and evaluate the model
* SageMaker offers several built-in learning algorithms to train on however we will use our own.
* Sagemaker uses Tensorflow Estimators which allow us to run our own Tensorflow ML algorithms on Sagemaker.
  You can write an  Estimator yourself but Tensorflow provides canned Estimators that we will modify.
  The KMeansClustering Estimator will be our learning algorithm.

Deploy the model
* SageMaker provides model hosting services to deploy a model. An ML compute instance is launched and the model and inference code
  are deployed on it. We then get an HTTPS endpoint back where the model is made available to provide inferences.
* To make requests to the endpoint we must make `InvokeEndpoint` operation requests. These requests can be made in one
  of 3 ways:
    * By calling the `predict(data)` function of the predictor object we get back after we call `deploy()` on the estimator.
    * Using the boto3 `Sagemaker.runtime` client. i.e `client = boto3.client('sagemaker-runtime')` and calling the
    `client.invoke_endpoint()` function.
    * The AWS CLI Sagemaker `invoke-endpoint` command.
* More information about calling the prediction endpoint can be found [here](https://docs.aws.amazon.com/sagemaker/latest/dg/API_runtime_InvokeEndpoint.html).

Remove the endpoint
* So we do not incur unecessary costs, we remove the endpoint whenever we are finished by
  running `sagemaker.session.delete_endpoint(predictor.endpoint)`. The endpoint can also be removed
  via the AWS Console

### Important Files: ###

Within this repo, 3 files have been created to work with Sagemaker to train the model and get predictions:

`kmeans_clustering.py` - This is the entry point to training and the script that gets passed to Sagemaker.
Within this file, a set of functions must be created that Sagemaker will call during training.

`preprocess.py` - Reads in the input data (users and movies) and creates a ratings matrix from that information. The data is also
split into train and test sets within this file.

`sm_learner.py` - Starting point of the train/predict process. This file has all the Sagemaker logic including
creating the `estimator = sagemaker.tensorflow.TensorFlow()` estimator object which trains the
model created from our entry-point script. Training is done by calling
`estimator.fit(<training_data_path>)` and providing the path to the training file located
in our s3. Then we call `predictor = estimator.deploy()` which creates a Sagemaker endpoint instance.
* `BUCKET_NAME` - S3 bucket where our training data, custom script, and model will reside
* `TRAINING_DATA_PATH` - path to the training data within the s3 bucket
* `ENTRY_POINT_SCRIPT` - name of the script SageMaker run as the entry point to training.
* `TEST_SPLIT_RATIO` - ratio of the dataset we use for evaluation.
* `PREDICT_NUM_USERS` - the amounbt of users we want to generate during testing of the endpoint.

The `predictor` object that's returned is a `sagemaker.predictor.RealTimePredictor`. Now we can pass
data in to this predictor by calling `results = predictor.predict([6.4, 3.2, 4.5, 1.5])` and we get back
the inference results from the endpoint.

The functions needed in `kmeans_clustering.py` along with a detailed explanation of using Tensorflow with
Sagemaker can be found on the sagemaker-python-sdk github at: [Tensorflow on Sagemaker](https://github.com/aws/sagemaker-python-sdk/blob/master/src/sagemaker/tensorflow/README.rst).
