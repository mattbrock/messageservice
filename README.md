# MessageService

All the code needed to provision and deploy a service that serves an HTML page containing a dynamic string which can be changed without redeploying.

This solution was developed in a response to a specific technical challenge, but it could also serve as a useful starting point for projects generally, bearing in mind the considerations in the discussion points at the bottom of this document for improvements going forward.

## Components

* Python application "MessageService" in _service_ subfolder, which provides the required application functionality and can be developed locally, then included in a deployment.
* Terraform configuration in _terraform_ subfolder, for provisioning an EC2 instance on which to run the application and an nginx frontend proxy for the application.
* Ansible configuration in _ansible_ subfolder, for deploying all required tools, services, dependencies on the EC2 instance as required, and currently also for deploying the application.

## Local requirements

* Python
* Boto
* AWS CLI
* Terraform
* Ansible

**N.B.** The AWS CLI environment needs to be set up and configured for the AWS account that's being used. See [Amazon's documentation](https://aws.amazon.com/cli/) for further information (though if using macOS I would suggest
installing via [Homebrew](https://brew.sh/) for simplicity, rather than bothering with the separate installer).

## MessageService Python application

### Local development

Need to `cd` to the _service_ subdirectory of the _messageservice_ directory.

Significant files:

* _copy-to-ansible.sh_ - to copy changes to Ansible folder for deployment.
* _index.html_ - main index page with Jinja2 templating for dynamic string.
* _message.dat_ - text file containing dynamic string.
* _requirements.txt_ - Python requirements (not currently used, but could be useful with a proper code deployment system).
* _server.py_ - Python application to server content and handle changes to dynamic string.

Activate virtualenv in dev environment:

```
python3 -m venv .venv
source .venv/bin/activate
pip3 install jinja2
pip freeze > requirements.txt # this isn't used currently but could be useful in a proper code deployment
```

Make changes as desired.

### Local testing

Start server:

```
python3 server.py
```

In another terminal window, make request:

```
curl localhost:8080
```

Change message:

```
curl -d "message=new+message" localhost:8080
```

### Exit virtualenv

```
deactivate
```

### Copy changes for deployment

```
./copy-to-ansible.sh
```

## Terraform

Need to `cd` to the _terraform_ subdirectory of the _messageservice_ directory.

Significant files:

* _ec2instance.tf_ - EC2 instance definition.
* _main.tf_ - AWS settings and Amazon Linux 2023 AMI definition.
* _userdata.sh_ - EC2 user data (used to add public keys for SSH access).
* _versions.tf_ - Specification for Terraform and provider versions.

**N.B.** Currently there is no Security Group setup or references, so ensure your default Security Group has inbound permissions for SSH, ideally locked to your own IP address for security, and inbound permissions for HTTP.
You could also add inbound permission for port 8080 locked to your own IP address, if you need to bypass nginx and check the Python app response directly.

If not previously initialised:

```
terraform init
```

See the changes that will be made:

```
terraform plan
```

Apply changes:

```
terraform apply
```

See current state:

```
terraform show
```

Destroy infrastructure (use with caution!):

```
terraform destroy
```

## Ansible

Need to `cd` to the _ansible_ subdirectory of the _messageservice_ directory.

Significant files/folders:

* _group_vars/_ - variable definitions for host groups being used (only the "messageservice" group currently) to set use of sudo and SSH params etc.
* _messageservice.sh_ - Bash script to generate dynamic inventory based on how instances are tagged (only "messageservice" group currently) (some Python/boto solution would be better, but this works as a quick and effective solution).
* _messageservice.yml_ - YAML playbook to deploy onto the EC2 instance(s) in use, which includes everything in the _roles/messageservice_ subdirectory.
* _roles/_ - contains subdirectories for different role types (currently only "messageservice" role) with subdirectories for playbooks and files to run all tasks, deploy all files, and run handlers as needed.

Deploy the whole configuration for "messageservice" role to "messageservice" host group:

```
ansible-playbook -i messageservice.sh messageservice.yml
```

## Testing/usage

Once the whole application is provisioned and deployed, get the public DNS of the instance from `terraform show` or from the EC2 web console.

Check the application is responding correctly:

```
$ curl http://INSTANCE_PUBLIC_DNS/
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Message Service</title>
</head>
<body>
  <h1>The saved string is dynamic string</h1>
</body>
</html>

```

Change the message (the dynamic string) by supplying the new string in the "message" data element via a POST request:

```
$ curl -d "message=NEW_MESSAGE_HERE" http://INSTANCE_PUBLIC_DNS/
Received new message: NEW_MESSAGE_HERE
```

The message in the dynamic string should now have changed accordingly:

```
$ curl http://INSTANCE_PUBLIC_DNS/
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Message Service</title>
</head>
<body>
  <h1>The saved string is NEW_MESSAGE_HERE</h1>
</body>
</html>

```

## Current solution, other options, improvements and embellishments

### Current solution

I interpreted this requirement as a web application serving content which can be changed via an admin backend (as per the requirement to change the content without redeploying anything), which has been simplified in such a way that it can be presented as a technical challenge which won't take an unrealistic amount of time to create.

As such I put together the application as a Python app which serves the content and also provides a very rudimentary API for changing the content. The Python code is really there as a rough proof of concept. Software developers would of course take this and produce something much better which could be developed into a more advanced application. Currently the app's use of the Python CGI module would need to be dropped ASAP since that module is now deprecated, but this is probably irrelevant anyway as software developers would do it differently.

Another way to solve it might have been to provide an upload mechanism to change the content without redeploying, which could have been written into the app, or uploaded to an S3 bucket, or uploaded via FTP, etc.

There's very little in the way of code comments due to time constraints. With more time, this would be one of the first issues to rectify.

### Application and API improvements

The API functionality is completely insecure currently, so it should be secured with system of API access keys. The very generic POST request should be developed into a proper API solution with relevant URI paths. The API could also be split off into a separate app and could ultimately be developed into a full admin backend interface. The app could then be run as a separate service which might be useful in terms of managing load on the main web app separately from the admin app, since a busy web application tends to have a different kind of load profile from a backend admin application. To encrypt traffic for proper security, the application should be moved from HTTP to HTTPS with the addition of TLS certificates.

### Repository and deployment improvements

Currently everything is in a single repository, and the application is developed locally and then the pertinent files are transferred via a script to the deployment folder to be deployed as part of the Ansible setup. This is fine as a proof of concept but wouldn't work well in an environment with multiple developers, separate development/DevOps teams, etc. So I'd want to split the application code into a separate repository, then it could be pulled direct from GitHub to server instances as needed. To improve on that further, it could be split into multiple repositories for different parts of the app (web frontend, admin backend, etc.), then ultimately could be set up with workflows/pipelines on GitHub Actions or similar to auto-deploy as needed (from push triggers, pull requests, etc. as needed).

### Infrastructure improvements

The infrastructure as defined and provisioned by the Terraform configuration is fine as far as it goes. Obvious improvements would be to manage the instance's Security Group via Terraform, and also definition of an SSH keypair for more resilient management. It could also go further and define VPC info, subnet info, etc.

Depending on the amount of traffic expected, auto-scaling could be set up for the EC2 instances to handle higher load and traffic spikes without incurring unneeded costs by having additional instances sitting there largely unused at quiet times. Using multiple instances would require a load balancer in front of the application to distribute requests across the instances, such as an Application Load Balancer set up within EC2. This could also be expanded to spread instances across multiple Availability Zones for more resiliency.

### Shared storage/database improvements
 
With more than one instance running as a result of scaling or auto-scaling, it would be necessary for the file containing the dynamic string to be readable and writable across all instances, so it could be stored on an S3 bucket or via a shared file system such as NFS or EFS. If the app were expanded further then ultimately the shared string could be placed in a database solution of some kind, for which there are various possibilities to consider such as MySQL or similar, on an instance or managed within RDS (using Aurora if auto-scaling is needed on the database tier), or perhaps MongoDB or DynamoDB if the app does not go beyond the requirement for key/value storage, or even Redis/ElastiCache if in-memory storage is deemed adequate.

If the app were further developed to cope with an environment with multiple developers and separate teams, separate repositories and deployment workflows etc., separate Terraform workspaces would be set up to handle separate environments for development, testing and production in order to keep things safely isolated. Terraform should also have a centralised state/locking setup (e.g. with S3 and DynamoDB) for safe handling of the Terraform state across multiple users.

### Containerisation

Another option for improvement would be to containerise the Python app and nginx proxy, which would allow a more streamlined development flow for developers to build into containers then pull the container image directly into testing or production environments. This could allow for simpler scaling and infrastructure management if the app were further developed into a more complex system of microservices communicating via APIs. To start with, a container runtime e.g. Docker could be installed on the EC2 instance, but as it grows it may make more sense for ease of scaling and managing time/costs to use a dedicated service such as ECS, which could be built on EC2 or it may make more sense to consider a serverless solution such as Fargate in order to reduce administrative complexity. If the app was expected to pass a certain level of complexity then a Kubernetes solution could be evaluated.

All of these options do not need to be run on AWS. Other cloud solutions such as GCP and Azure could be considered, as they all have equivalent services to the ones mentioned above.
