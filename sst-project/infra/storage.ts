export const s3list = ["bucket1", "bucket2"];

export const buckets = [];
for (const bucket of s3list) {
  buckets.push(new sst.aws.Bucket(bucket));
}
