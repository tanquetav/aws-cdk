```
aws cloudformation create-stack --template-body file://cloudformation.yaml  --stack-name cloudformation --capabilities CAPABILITY_NAMED_IAM

aws cloudformation delete-stack --stack-name cloudformation
```
