import { Resource } from "sst";
import { Handler } from "aws-lambda";
import { S3Client, ListObjectsV2Command } from "@aws-sdk/client-s3";

export const handler: Handler = async (_event) => {
  // Extract specific properties from the event object
  const client = new S3Client();
  const bucketid: string = process.env.BUCKET_ID ?? "";
  const input = {
    Bucket: Resource[bucketid].name,
  };
  const command = new ListObjectsV2Command(input);
  const response2 = await client.send(command);

  return {
    body: JSON.stringify(response2, null, 2),
    statusCode: 200,
  };
};
