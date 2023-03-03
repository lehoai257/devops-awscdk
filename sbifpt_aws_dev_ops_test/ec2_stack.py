from aws_cdk import CfnOutput, Stack
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_elasticloadbalancingv2 as elb
import aws_cdk.aws_autoscaling as autoscaling
import aws_cdk.aws_certificatemanager as acm
import aws_cdk.aws_iam as iam
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_deployment as s3deploy
from constructs import Construct

ec2_type = "t2.micro"
#Please create a keypair and enter to key_name
key_name = "devops_test_key"
linux_ami = ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
    edition=ec2.AmazonLinuxEdition.STANDARD,
    virtualization=ec2.AmazonLinuxVirt.HVM,
    storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
    )

#Please modify acm arn ssl certificate
CERTIFICATE='arn:aws:acm:us-west-2:405253367546:certificate/e528c8e4-0724-4017-a9f9-a8b1b2fbc237'
    
with open("./user_data/user_data.sh") as f:
    user_data = f.read()

class CdkEc2Stack(Stack):

    def __init__(self, scope: Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        #Add role to get simple sourcecode from s3 bucket for ec2
        role = iam.Role(self, "s3RoleForTomcat", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"))

        #Create s3 bucket for store simple web sourcecode
        bucket = s3.Bucket(self, "tomcat-simple-web",
            bucket_name="tomcat-simple-web",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL)

        #Put simple sourcecode to s3 bucket
        deployment = s3deploy.BucketDeployment(self, "deployTomcatWeb",
            sources=[s3deploy.Source.asset("./sourceCode")],
            destination_bucket= bucket
        )

        #Get acm ssl certificate
        certificate = acm.Certificate.from_certificate_arn(
            self, "certificate",
            certificate_arn=CERTIFICATE,
        )

        #Create a bastion host
        bastion = ec2.BastionHostLinux(self, "TerminalVM",
            vpc=vpc,
            subnet_selection=ec2.SubnetSelection(
            subnet_type=ec2.SubnetType.PUBLIC),
            instance_name="TerminalVM",
            instance_type=ec2.InstanceType(instance_type_identifier=ec2_type))

        bastion.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"))

        #Bastion security group rule
        bastion.connections.allow_from_any_ipv4(
            ec2.Port.tcp(22), "SSH access")

        #Create ALB
        alb = elb.ApplicationLoadBalancer(self, "ALB for tomcat web",
            vpc=vpc,
            internet_facing=True,
            load_balancer_name="ALB-Tomcat-Web"
            )

        #ALB security group rule    
        alb.connections.allow_from_any_ipv4(ec2.Port.tcp(80), "Internet access ALB 80")
        alb.connections.allow_from_any_ipv4(ec2.Port.tcp(443), "Internet access ALB 443")

        #ALB listeners
        http_listener = alb.add_listener("http_listener", port=80, open=False)
        https_listener = alb.add_listener("https_listener", port=443, open=False, certificates=[certificate], protocol=elb.ApplicationProtocol.HTTPS)

        #Create autoscaling group
        self.asg = autoscaling.AutoScalingGroup(self, "myASG",
            vpc=vpc,
            role=role,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
            instance_type=ec2.InstanceType(instance_type_identifier=ec2_type),
            machine_image=linux_ami,
            key_name=key_name,
            user_data=ec2.UserData.custom(user_data),
            desired_capacity=2,
            min_capacity=2,
            max_capacity=2,
            )

        #ASG security group rule
        self.asg.connections.allow_from(alb, ec2.Port.tcp(8080), "ALB access 8080 port of EC2 in Autoscaling Group")
        self.asg.connections.allow_from(alb, ec2.Port.tcp(8443), "ALB access 8443 port of EC2 in Autoscaling Group")
        self.asg.connections.allow_from(bastion, ec2.Port.tcp(22), "Bastion host access 22 port of EC2 in Autoscaling Group")

        #Add target group
        http_listener.add_targets("addHttpTargetGroup",
            port=8080,
            protocol=elb.ApplicationProtocol.HTTP,
            targets=[self.asg])

        https_target_group = https_listener.add_targets(
            'addHttpsTargetGroup',
            targets=[self.asg],
            port=8443,
            protocol=elb.ApplicationProtocol.HTTPS,
        )
        https_target_group.configure_health_check(
            healthy_http_codes="200,301,302",
            healthy_threshold_count=3,
            unhealthy_threshold_count=5,
            path="/"
        )
    
        CfnOutput(self, "Output",value=alb.load_balancer_dns_name)