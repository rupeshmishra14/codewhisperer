import os.path

from aws_cdk.aws_s3_assets import Asset

from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    App, Stack
)

from constructs import Construct

dirname = os.path.dirname(__file__)

#create a ec2 instance using aws cdk
class EC2InstanceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        #connect with AWS account 
        self.account = os.environ["CDK_DEFAULT_ACCOUNT"]
        self.region = os.environ["CDK_DEFAULT_REGION"]

        # The code that defines your stack goes here
        vpc = ec2.Vpc(
            self, "VPC",
            max_azs=2
        )

        # create an asset that will be used as part of the instance user data
        asset = Asset(self, "Asset", path=os.path.join(dirname, "user-data.sh"))
        local_path = asset.add_property_override("LocalPath", "/tmp/user-data.sh").local_path

        # create a role that will be used by the ec2 instance
        role = iam.Role(
            self, "InstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")]
        )

        # create the instance using the asset and role
        instance = ec2.Instance(
            self, "Instance",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            vpc=vpc,
            role=role,
        )

        #create security group for the instance
        security_group = ec2.SecurityGroup(
            self, "SecurityGroup",
            vpc=vpc,
            description="Allow SSH (TCP port 22) in",
            allow_all_outbound=True
        )

        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22),
        )

app = App()
EC2InstanceStack(app, "EC2InstanceStack")
app.synth()
