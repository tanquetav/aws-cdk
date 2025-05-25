import { Construct } from "constructs";
import { App, Chart, ChartProps } from "cdk8s";
import * as kplus from "cdk8s-plus-28";

export class MyChart extends Chart {
  constructor(scope: Construct, id: string, props: ChartProps = {}) {
    super(scope, id, props);

    // define resources here
    const deployment = new kplus.Deployment(this, "Deployment", {
      replicas: 1,
      securityContext: {
        user: 999,
      },
      containers: [
        {
          image: "stefanprodan/podinfo:3.0.0",
          ports: [{ number: 9898 }],
        },
      ],
    });
    deployment.exposeViaIngress("/");
  }
}

const app = new App();
new MyChart(app, "cdk8s");
app.synth();
