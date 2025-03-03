from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket


def s3_buckets(stack, s3list):
    s3objects = []
    for s3_name in s3list:
        s3object = S3Bucket(stack, s3_name, bucket=s3_name)
        s3objects.append(s3object)
