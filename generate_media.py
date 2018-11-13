""" Generate module for media """
import warnings
import csv
import pandas as pd
import vars
import boto3

warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")


def generate(bucket, key):
    """ Returns tmdb 5000 movies. Can be given a separate path.

    Alternatively, we may want to parse and cache movies from tmdb ourselves.
    This can be done leveraging tmdbsimple and using the following logic:
    """
    import boto3
    s3 = boto3.client('s3')

    obj = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(obj['Body']) 
    return df

def convert_csv_to_json(df, export_name):    
    jsonFile = df.to_json(orient='records')
    return jsonFile

    
def decode(media, media_averages):
    """create a dict of media id to title for dashboard """
    media_dict = {}
    for _, row in media.iterrows():
        if row[vars.MEDIA_ID_FIELD] not in media_dict.keys():
            if row[vars.MEDIA_ID_FIELD] in media_averages:
                media_dict[row[vars.MEDIA_ID_FIELD]] = \
                    (row[vars.TITLE_FIELD],
                     media_averages[row[vars.MEDIA_ID_FIELD]], row[vars.MEDIA_POPULARITY_FIELD], row[vars.MEDIA_IMAGE_FIELD])
            else:
                pass
#                 media_dict[row[vars.MEDIA_ID_FIELD]] = \
#                     (row[vars.TITLE_FIELD], "")
  
    df = pd.DataFrame(columns=['media_id','title','average rating', 'popularity','imUrl'])   
    ct = 0
    for key, value in media_dict.items():
        df.at[ct,'media_id'] = key
        df.at[ct,'title'] = value[0]
        df.at[ct,'average rating'] = value[1]
        df.at[ct,'popularity'] = value[2]
        df.at[ct,'imUrl'] = value[3]
        ct += 1
        
    jsonFile=convert_csv_to_json(df, "electronics_media.json")
    
    client = boto3.client('s3')
    client.put_object(Body=bytes(jsonFile.encode('utf-8')), Bucket=vars.DATA_BUCKET, Key=vars.JSON_MEDIA)
    return media_dict
