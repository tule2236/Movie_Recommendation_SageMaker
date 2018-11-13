

def predict_clusters(self, n_users, n_media):
        '''obtain inference results from the endpoint'''
        # self.process_input_data(raw_data_path=vars.RAW_DATA_PATH,
        #                         n_users=vars.NUM_USERS,
        #                         n_media=vars.NUM_MEDIA)
        mtx = tf.make_tensor_proto(values=self.ratings_matrix,
                                   shape=list(self.ratings_matrix.shape),
                                   dtype=tf.float32)
        result = self.predictor.predict(mtx)
        # cluster_int64 = result['outputs']['output']['int64_val']
        cluster_int64 = result['outputs']['output']['int64Val']
        clusters = map(int, cluster_int64)
        return clusters

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


training_job_name = tf_estimator.latest_training_job.name

# after some time, or in a separate python notebook, we can attach to it again.

estimator = TensorFlow.attach(training_job_name=training_job_name)

predictor = estimator.\
            deploy(initial_instance_count=vars.TRAIN_INSTANCE_COUNT,
                   instance_type=vars.TRAIN_INSTANCE_TYPE)


user_clusters = predict_clusters(n_users=vars.NUM_USERS,
                                             n_media=vars.NUM_MEDIA)


print('Prediction array:\n\n{}'.format(user_clusters))
process_metrics(labels=user_clusters)

# recomm_media = recommendations.generate_recommendations(learner.media, learner.names, learner.final,
#                                              learner.ratings_matrix,  # new user matrix
#                                              user_clusters, learner.lookup)
