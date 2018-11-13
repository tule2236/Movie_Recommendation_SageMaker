'''format the data for use by other functions'''


def format_data(usr_ratings, name_list, ratings_matrix,
                media, ngroups, group_labels):
    """
    Calculate kmeans. Group_labels is a list where the nubmer at each
    index is the the group number of that user. Then, put the data
    in the correct format for the csv file.
    """
    # kmeans = KMeans(n_clusters=ngroups).fit(ratings_matrix)
    # group_labels = kmeans.labels_.tolist()
    index = 0
    final = []
    while index < len(group_labels):
        for media_id in usr_ratings[index]:
            cur = []
            cur.append(name_list[index])
            cur.append(group_labels[index])
            cur.append(media_id)
            name = media[media_id]
            cur.append(name)
            cur.append(usr_ratings[index][media_id])
            final.append(cur)
        index += 1
    return final
