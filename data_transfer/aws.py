import numpy as np
import boto3


class AWSClient():
    def __init__(self, access_key_id, secret_access_key, **kwargs):
        aws_session = boto3.session.Session(aws_access_key_id=access_key_id,
                                            aws_secret_access_key=secret_access_key);
        self.aws_access_key_id = access_key_id
        self.aws_secret_access_key = secret_access_key
        self.session = aws_session
        self.client = aws_session.client("s3")
        self.default_bucket = kwargs.get("default_bucket")

    def get_bucket_objects(self, bucket=None):
        bucket = self.default_bucket if self.default_bucket is not None else bucket
        response = self.client.list_objects(Bucket=bucket);
        objs = response.get("Contents", None)
        if objs is None:
            return []
        return [x["Key"] for x in objs]

    def save_object_into_bucket(self, obj, name, bucket=None):
        bucket = self.default_bucket if self.default_bucket is not None else bucket
        self.client.put_object(Bucket=bucket, Body=obj, Key=name);

    def delete_object_from_bucket(self, name, bucket=None):
        bucket = self.default_bucket if self.default_bucket is not None else bucket
        self.client.delete_object(Bucket=bucket, Key=name);

    def empty_bucket(self, bucket=None):
        bucket = self.default_bucket if self.default_bucket is not None else bucket
        objs = self.get_bucket_objects(bucket=bucket)
        for obj in objs:
            self.delete_object_from_bucket(name=obj, bucket=bucket)

    def get_object_url(self, name, bucket=None):
        bucket = self.default_bucket if self.default_bucket is not None else bucket
        url = self.client.generate_presigned_url(ClientMethod="get_object",
                                                 ExpiresIn=60*60*24*30,     # 30 days 
                                                 Params={"Bucket": bucket,
                                                         "Key":    name
                                                         });
        return url

    def get_filtered_bucket_objects(self, pattern, bucket=None):
        bucket = self.default_bucket if self.default_bucket is not None else bucket
        objs = self.get_bucket_objects(bucket=bucket)
        objs = [x.strip(".png") for x in objs]
        filtered = [x for x in objs if pattern in x]
        dates = [np.datetime64(x.split("_")[-1]) for x in filtered]
        idxs_argsort = np.argsort(dates)
        ordered = [filtered[i]+".png" for i in idxs_argsort]
        return ordered

    def delete_old_objects_from_bucket(self, pattern, leave_n_last=1, bucket=None):
        bucket = self.default_bucket if self.default_bucket is not None else bucket
        objs = self.get_filtered_bucket_objects(pattern=pattern, bucket=bucket)
        objs_to_delete = objs[:-leave_n_last]
        if len(objs_to_delete)==0:
            return
        for name in objs_to_delete:
            self.delete_object_from_bucket(name=name, bucket=bucket)
