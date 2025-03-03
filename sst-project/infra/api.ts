import { Resource } from "sst";
import { buckets, s3list } from "./storage";

const myApi = new sst.aws.Function("MyApi", {
  url: false,
  link: buckets,
  handler: "packages/functions/src/api.handler",
  environment: {
    BUCKET_ID: s3list[0],
  },
});

const api = new sst.aws.ApiGatewayV2("ApiGateway").route("ANY /", myApi.arn);
