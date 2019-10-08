# Simple web site on AWS.
[![Build Status](https://travis-ci.com/MTB90/terraform-aws-ecs.svg?branch=master)](https://travis-ci.com/MTB90/terraform-aws-ecs)
[![codecov.io](https://codecov.io/github/MTB90/terraform-aws-ecs/coverage.svg?branch=master)](https://codecov.io/github/MTB90/terraform-aws-ecs?branch=master)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

List of used AWS components:
- VPC, Subnets, Internet gateway
- Bastion, Nat-Instance
- Security groups
- EC2, ALB
- ROUTE53 zone
- ECS cluster, ECS service, ECS task definition, ECR
- App autoscaling target/policy (ECS task)
- Autoscaling group/policy (EC2)
- COGNITO
- Cloudwatch (logs EC2/Task)
- Dynamodb

### AWS web site configuration

1) AWS:
	- certificate for your domain name
	- EC2 key
	- ECR repository named photorec

2) Update file envfile with your variables: AWS_PROFILE, AWS_ACCOUNT_ID, REGION
3) Update file terraform/main.tf for tfstate location
4) Update file terraform/variables.tf: 
	- bastion_sq_inbaound_rule: with your ip e.g 190.32.43.2/32
	- bastion_key_name: name of ec2 key
	- domain: your domain name for which you request certificate
	- certificate_arn: provide cert arn
	- cname_records: CNAME record to the DNS configuration for your domain
5) Deployment:

Setup environment:
```bash
$ make ecr-push-image
$ make tf-create 
```
Create new image and update service:
```bash
$ make ecr-push-image
$ make ecr-update-service
``` 
Destroy environment:
```bash
$ make tf-destroy
```