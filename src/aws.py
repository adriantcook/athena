import sys
import logging as log
import boto3
from botocore.exceptions import UnauthorizedSSOTokenError, \
    ClientError, NoCredentialsError

log.basicConfig(
    level=log.DEBUG, 
    stream=sys.stdout,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Aws:
    def __init__(self):
        self.session = None


    def aws_account_id(self):
        sts_client = self.session.client('sts')
        identity = sts_client.get_caller_identity()
        return identity['Account']


    def create_session(self):
        self.session = boto3.Session()
        try:
            self.account_id = self.aws_account_id()
        except UnauthorizedSSOTokenError:
            print("Please run `aws sso login`.")
            sys.exit(1)
        except NoCredentialsError:
            print("Could not locate aws credentials, ensure your profile is set.")
            sys.exit(1)
        except ClientError as client_error:
            if client_error.response['Error']['Code'] == 'UnauthorizedException':
                print("Session token not found or invalid.")
                sys.exit(1)

        log.info("")
        log.info("Creating session, values:")
        log.info("\t%-15s%s", 'aws_account_id', self.account_id)
        log.info("\t%-15s%s", 'profile', self.session.profile_name)
        log.info("\t%-15s%s", 'region', self.session.region_name)
        log.info("")

        return self.session, {
            "aws_account_id": self.account_id,
            "profile": self.session.profile_name,
            "region": self.session.region_name,
        }


    def get_session(self):
        if self.session:
            return self.session, {
                "aws_account_id": self.account_id,
                "profile": self.session.profile_name,
                "region": self.session.region_name,
            }
        return self.create_session()
