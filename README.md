
# Welcome to your CDK Python project!

![alt text](https://github.com/lehoai257/devops-awscdk/blob/main/Diagram.png)

This is a test lab for CDK development with Python.

We need to change the values of the following two variables in ec2_stack.py:
```
key_name = "key_pair_name"
```
-> Please create a key pair in EC2 and substitute in this variable.
```
CERTIFICATE= "arn_acm_certificate"
```
-> Please create an acm certificate or already have one then replace the ACM's arn in this variable. (Please use ACM on the same region)
-> Due to the cost of creating a new ACM certificate, it needs to be imported manually into the cdk.

###If you have deployed this project before, please remove ```tomcat-simple-web``` in s3 bucket.


To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
