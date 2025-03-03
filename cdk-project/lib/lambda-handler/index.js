const { S3Client, ListObjectsV2Command } = require("@aws-sdk/client-s3");

exports.handler = async (event) => {
  // Extract specific properties from the event object
  const client = new S3Client();
  const input = {
    Bucket: process.env.BUCKET_NAME,
  };
  const command = new ListObjectsV2Command(input);
  const response2 = await client.send(command);

  return {
    body: JSON.stringify(response2, null, 2),
    statusCode: 200,
  };
};
