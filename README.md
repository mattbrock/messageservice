# MessageService (for DevOps technical challenge)

All the code needed to provision and deploy a service that serves an HTML containing a dynamic string which can be changed without redeploying.

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

**N.B.** The AWS CLI environment needs to be set up and configured for the AWS account that's being used.
## Local development of MessageService Python application

### Local development

Need to `cd` to the _service_ subdirectory of the _messageservice_ directory.

Significant files:

* _copy-to-ansible.sh_ - to copy changes to Ansible folder for deployment.
* _index.html_ - main index page with Jinja2 templating for dynamic string.
* _message.dat_ - file containing dynamic string.
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

## Current solution, other options, improvements and embellishments

I interpreted this requirement as a web application serving content which can be changed via an admin backend (as per the requirement to change the content without redeploying anything), which has been simplified in such a way that it can be presented as a technical challenge which won't take an unrealistic amount of time to create.

As such I put together the application as a Python app which serves the content and also provides a very rudimentary API for changing the content. The Python code is really there as a rough proof of concept. Software developers would of course take this and produce something much better which could be developed into a more advanced application. Currently the app's use of the Python CGI module would need to be dropped ASAP since that module is now deprecated, but this is probably irrelevant anyway as software developers would do it differently.

Another way to solve it might have been to provide an upload mechanism to change the content without redeploying, which could have been written into the app, or uploaded to an S3 bucket, or uploaded via FTP, etc.

The API functionality is completely insecure currently, so it should be secured with system of API access keys. The very generic POST request should be developed into a proper API solution with relevant URI paths. The API could also be split off into a separate app and could ultimately be developed into a full admin backend interface. The app could then be run as a separate service which might be useful in terms of managing load on the main web app separately from the admin app, since a busy web application tends to have a different kind of load profile from a backend admin application.

Currently everything is in a single repository, and the application is developed locally and then the pertinent files are transferred via a script to the deployment folder to be deployed as part of the Ansible setup. This is fine as a proof of concept but wouldn't work well in an environment with multiple developers, separate development/DevOps teams, etc. So I'd want to split the application code into a separate repository, then it could be pulled direct from GitHub to server instances as needed. To improve on that further, it could be split into multiple repositories for different parts of the app (web frontend, admin backend, etc.), then ultimately could be set up with workflows/pipelines on GitHub Actions or similar to auto-deploy as needed (from push triggers, pull requests, etc. as preferred).

The infrastructure as defined and provisioned by the Terraform configuration is fine as far as it goes. 


??? SHOW EXAMPLES OF APP IN ACTION ???

## Improvements

### Terraform

* Create and use dedicated security group.
* Specify SSH key.
* Specify VPC and subnets etc.
* Separate workspaces.

### Infrastructure

* TLS.
* Auto-scaling.
* Spread across multiple AZs.
* Load balancer.
* Put data in database.
### Containerisation