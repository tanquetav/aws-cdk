from cdktf import TerraformAsset, AssetType
from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket
from cdktf_cdktf_provider_aws.s3_object import S3Object


def lambda_source(stack):
    # Create Lambda executable
    asset = TerraformAsset(
        stack, "lambda-asset", path="lib/lambda-handler/", type=AssetType.ARCHIVE
    )

    # Create unique S3 bucket that hosts Lambda executable
    bucket = S3Bucket(
        stack,
        "bucket32432",
        bucket_prefix="cdktf-lambda",
    )

    # Upload Lambda zip file to newly created S3 bucket
    lambda_archive = S3Object(
        stack,
        "lambda-archive",
        bucket=bucket.bucket,
        key=asset.file_name,
        source=asset.path,
    )

    return bucket, lambda_archive
