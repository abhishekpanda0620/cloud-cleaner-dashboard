"""AWS Client Factory for centralized boto3 client management"""
import boto3
from typing import Optional
from functools import lru_cache
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class AWSClientFactory:
    """Factory class for creating and managing AWS service clients"""
    
    def __init__(self):
        self._session: Optional[boto3.Session] = None
    
    @property
    def session(self) -> boto3.Session:
        """Get or create boto3 session with configured credentials"""
        if self._session is None:
            try:
                self._session = boto3.Session(
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region
                )
                logger.info(f"AWS session created for region: {settings.aws_region}")
            except Exception as e:
                logger.error(f"Failed to create AWS session: {e}")
                raise
        return self._session
    
    def get_client(self, service_name: str):
        """
        Get a boto3 client for the specified AWS service
        
        Args:
            service_name: Name of the AWS service (e.g., 'ec2', 's3', 'iam')
            
        Returns:
            boto3 client for the specified service
        """
        try:
            client = self.session.client(service_name)
            logger.debug(f"Created {service_name} client")
            return client
        except Exception as e:
            logger.error(f"Failed to create {service_name} client: {e}")
            raise
    
    def get_resource(self, service_name: str):
        """
        Get a boto3 resource for the specified AWS service
        
        Args:
            service_name: Name of the AWS service (e.g., 'ec2', 's3')
            
        Returns:
            boto3 resource for the specified service
        """
        try:
            resource = self.session.resource(service_name)
            logger.debug(f"Created {service_name} resource")
            return resource
        except Exception as e:
            logger.error(f"Failed to create {service_name} resource: {e}")
            raise


@lru_cache()
def get_aws_client_factory() -> AWSClientFactory:
    """Get singleton instance of AWSClientFactory"""
    return AWSClientFactory()


# Convenience functions for getting specific clients
def get_ec2_client():
    """Get EC2 client"""
    return get_aws_client_factory().get_client('ec2')


def get_s3_client():
    """Get S3 client"""
    return get_aws_client_factory().get_client('s3')


def get_ebs_client():
    """Get EBS client (EC2 client is used for EBS operations)"""
    return get_aws_client_factory().get_client('ec2')


def get_iam_client():
    """Get IAM client"""
    return get_aws_client_factory().get_client('iam')