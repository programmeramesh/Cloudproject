import logging
from abc import ABC, abstractmethod


class CloudProvider(ABC):
    """Abstract base class for cloud providers"""
    
    @abstractmethod
    def scale_up(self, target_instances, instance_type):
        pass
    
    @abstractmethod
    def scale_down(self, target_instances, instance_type):
        pass
    
    @abstractmethod
    def get_current_resources(self):
        pass
    
    @abstractmethod
    def terminate_instance(self, instance_id):
        pass
    
    @abstractmethod
    def launch_instance(self, instance_type, count=1):
        pass


class AWSProvider(CloudProvider):
    """AWS EC2 provider implementation"""
    
    def __init__(self, credentials):
        self.credentials = credentials
        self.logger = logging.getLogger(__name__)
        self.ec2_client = None
        self.autoscaling_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AWS clients"""
        try:
            import boto3
            
            self.ec2_client = boto3.client(
                'ec2',
                aws_access_key_id=self.credentials.get('access_key'),
                aws_secret_access_key=self.credentials.get('secret_key'),
                region_name=self.credentials.get('region', 'us-east-1')
            )
            
            self.autoscaling_client = boto3.client(
                'autoscaling',
                aws_access_key_id=self.credentials.get('access_key'),
                aws_secret_access_key=self.credentials.get('secret_key'),
                region_name=self.credentials.get('region', 'us-east-1')
            )
            
            self.logger.info("AWS clients initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing AWS clients: {str(e)}")
    
    def get_current_resources(self):
        """Get current EC2 instances"""
        try:
            response = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'instance-state-name', 'Values': ['running']}
                ]
            )
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'instance_id': instance['InstanceId'],
                        'instance_type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'launch_time': instance['LaunchTime'],
                        'availability_zone': instance['Placement']['AvailabilityZone']
                    })
            
            return {
                'instance_count': len(instances),
                'instances': instances,
                'instance_type': instances[0]['instance_type'] if instances else 't2.micro'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting current resources: {str(e)}")
            return {'instance_count': 0, 'instances': [], 'instance_type': 't2.micro'}
    
    def scale_up(self, target_instances, instance_type):
        """Scale up EC2 instances"""
        try:
            current = self.get_current_resources()
            current_count = current['instance_count']
            
            if target_instances <= current_count:
                return {
                    'success': True,
                    'message': 'Already at or above target instance count',
                    'action': 'scale_up',
                    'current_count': current_count,
                    'target_count': target_instances
                }
            
            instances_to_launch = target_instances - current_count
            
            # Launch new instances
            result = self.launch_instance(instance_type, instances_to_launch)
            
            return {
                'success': result['success'],
                'message': f'Launched {instances_to_launch} new instances',
                'action': 'scale_up',
                'current_count': current_count,
                'target_count': target_instances,
                'new_instances': result.get('instance_ids', [])
            }
            
        except Exception as e:
            self.logger.error(f"Error scaling up: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'action': 'scale_up'
            }
    
    def scale_down(self, target_instances, instance_type):
        """Scale down EC2 instances"""
        try:
            current = self.get_current_resources()
            current_count = current['instance_count']
            
            if target_instances >= current_count:
                return {
                    'success': True,
                    'message': 'Already at or below target instance count',
                    'action': 'scale_down',
                    'current_count': current_count,
                    'target_count': target_instances
                }
            
            instances_to_terminate = current_count - target_instances
            
            # Get instances to terminate (oldest first)
            instances = sorted(
                current['instances'],
                key=lambda x: x['launch_time']
            )
            
            terminated = []
            for i in range(instances_to_terminate):
                instance_id = instances[i]['instance_id']
                result = self.terminate_instance(instance_id)
                if result['success']:
                    terminated.append(instance_id)
            
            return {
                'success': True,
                'message': f'Terminated {len(terminated)} instances',
                'action': 'scale_down',
                'current_count': current_count,
                'target_count': target_instances,
                'terminated_instances': terminated
            }
            
        except Exception as e:
            self.logger.error(f"Error scaling down: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'action': 'scale_down'
            }
    
    def launch_instance(self, instance_type, count=1):
        """Launch new EC2 instances"""
        try:
            # Note: In production, you'd specify AMI ID, security groups, etc.
            response = self.ec2_client.run_instances(
                ImageId='ami-0c55b159cbfafe1f0',  # Example AMI (update for your region)
                InstanceType=instance_type,
                MinCount=count,
                MaxCount=count,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': 'AutoScaled-Instance'},
                            {'Key': 'ManagedBy', 'Value': 'CloudOptimizer'}
                        ]
                    }
                ]
            )
            
            instance_ids = [inst['InstanceId'] for inst in response['Instances']]
            
            self.logger.info(f"Launched {count} instances: {instance_ids}")
            
            return {
                'success': True,
                'instance_ids': instance_ids,
                'count': count
            }
            
        except Exception as e:
            self.logger.error(f"Error launching instances: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def terminate_instance(self, instance_id):
        """Terminate an EC2 instance"""
        try:
            response = self.ec2_client.terminate_instances(
                InstanceIds=[instance_id]
            )
            
            self.logger.info(f"Terminated instance: {instance_id}")
            
            return {
                'success': True,
                'instance_id': instance_id
            }
            
        except Exception as e:
            self.logger.error(f"Error terminating instance: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }


class AzureProvider(CloudProvider):
    """Azure VM provider implementation"""
    
    def __init__(self, credentials):
        self.credentials = credentials
        self.logger = logging.getLogger(__name__)
        self.compute_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Azure clients"""
        try:
            from azure.identity import ClientSecretCredential
            from azure.mgmt.compute import ComputeManagementClient
            
            credential = ClientSecretCredential(
                tenant_id=self.credentials.get('tenant_id'),
                client_id=self.credentials.get('client_id'),
                client_secret=self.credentials.get('client_secret')
            )
            
            self.compute_client = ComputeManagementClient(
                credential,
                self.credentials.get('subscription_id')
            )
            
            self.logger.info("Azure clients initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing Azure clients: {str(e)}")
    
    def get_current_resources(self):
        """Get current Azure VMs"""
        try:
            resource_group = self.credentials.get('resource_group')
            vms = list(self.compute_client.virtual_machines.list(resource_group))
            
            instances = []
            for vm in vms:
                instances.append({
                    'vm_id': vm.id,
                    'vm_name': vm.name,
                    'vm_size': vm.hardware_profile.vm_size,
                    'location': vm.location
                })
            
            return {
                'instance_count': len(instances),
                'instances': instances,
                'instance_type': instances[0]['vm_size'] if instances else 'Standard_B1s'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting Azure resources: {str(e)}")
            return {'instance_count': 0, 'instances': [], 'instance_type': 'Standard_B1s'}
    
    def scale_up(self, target_instances, instance_type):
        """Scale up Azure VMs"""
        # Implementation similar to AWS
        self.logger.info(f"Azure scale up to {target_instances} instances")
        return {'success': True, 'message': 'Azure scale up (placeholder)'}
    
    def scale_down(self, target_instances, instance_type):
        """Scale down Azure VMs"""
        self.logger.info(f"Azure scale down to {target_instances} instances")
        return {'success': True, 'message': 'Azure scale down (placeholder)'}
    
    def launch_instance(self, instance_type, count=1):
        """Launch Azure VM"""
        self.logger.info(f"Launching {count} Azure VMs")
        return {'success': True, 'message': 'Azure launch (placeholder)'}
    
    def terminate_instance(self, instance_id):
        """Terminate Azure VM"""
        self.logger.info(f"Terminating Azure VM: {instance_id}")
        return {'success': True, 'message': 'Azure terminate (placeholder)'}


class GCPProvider(CloudProvider):
    """GCP Compute Engine provider implementation"""
    
    def __init__(self, credentials):
        self.credentials = credentials
        self.logger = logging.getLogger(__name__)
        self.compute_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize GCP clients"""
        try:
            from google.cloud import compute_v1
            
            self.compute_client = compute_v1.InstancesClient()
            self.logger.info("GCP clients initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing GCP clients: {str(e)}")
    
    def get_current_resources(self):
        """Get current GCP instances"""
        try:
            project = self.credentials.get('project_id')
            zone = self.credentials.get('zone', 'us-central1-a')
            
            request = compute_v1.ListInstancesRequest(
                project=project,
                zone=zone
            )
            
            instances = []
            for instance in self.compute_client.list(request=request):
                instances.append({
                    'instance_id': instance.id,
                    'instance_name': instance.name,
                    'machine_type': instance.machine_type,
                    'status': instance.status
                })
            
            return {
                'instance_count': len(instances),
                'instances': instances,
                'instance_type': instances[0]['machine_type'] if instances else 'e2-micro'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting GCP resources: {str(e)}")
            return {'instance_count': 0, 'instances': [], 'instance_type': 'e2-micro'}
    
    def scale_up(self, target_instances, instance_type):
        """Scale up GCP instances"""
        self.logger.info(f"GCP scale up to {target_instances} instances")
        return {'success': True, 'message': 'GCP scale up (placeholder)'}
    
    def scale_down(self, target_instances, instance_type):
        """Scale down GCP instances"""
        self.logger.info(f"GCP scale down to {target_instances} instances")
        return {'success': True, 'message': 'GCP scale down (placeholder)'}
    
    def launch_instance(self, instance_type, count=1):
        """Launch GCP instance"""
        self.logger.info(f"Launching {count} GCP instances")
        return {'success': True, 'message': 'GCP launch (placeholder)'}
    
    def terminate_instance(self, instance_id):
        """Terminate GCP instance"""
        self.logger.info(f"Terminating GCP instance: {instance_id}")
        return {'success': True, 'message': 'GCP terminate (placeholder)'}


class MockProvider(CloudProvider):
    """Mock provider for testing without cloud credentials"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.instances = [
            {
                'instance_id': 'mock-instance-1',
                'instance_type': 't2.small',
                'state': 'running'
            }
        ]
    
    def get_current_resources(self):
        """Get mock resources"""
        return {
            'instance_count': len(self.instances),
            'instances': self.instances,
            'instance_type': self.instances[0]['instance_type'] if self.instances else 't2.micro'
        }
    
    def scale_up(self, target_instances, instance_type):
        """Mock scale up"""
        current_count = len(self.instances)
        for i in range(target_instances - current_count):
            self.instances.append({
                'instance_id': f'mock-instance-{current_count + i + 1}',
                'instance_type': instance_type,
                'state': 'running'
            })
        
        return {
            'success': True,
            'message': f'Scaled up to {target_instances} instances (mock)',
            'action': 'scale_up'
        }
    
    def scale_down(self, target_instances, instance_type):
        """Mock scale down"""
        self.instances = self.instances[:target_instances]
        
        return {
            'success': True,
            'message': f'Scaled down to {target_instances} instances (mock)',
            'action': 'scale_down'
        }
    
    def launch_instance(self, instance_type, count=1):
        """Mock launch"""
        new_ids = []
        for i in range(count):
            instance_id = f'mock-instance-{len(self.instances) + 1}'
            self.instances.append({
                'instance_id': instance_id,
                'instance_type': instance_type,
                'state': 'running'
            })
            new_ids.append(instance_id)
        
        return {
            'success': True,
            'instance_ids': new_ids
        }
    
    def terminate_instance(self, instance_id):
        """Mock terminate"""
        self.instances = [i for i in self.instances if i['instance_id'] != instance_id]
        
        return {
            'success': True,
            'instance_id': instance_id
        }


def get_cloud_provider(provider_type, credentials=None):
    """Factory function to get cloud provider"""
    providers = {
        'aws': AWSProvider,
        'azure': AzureProvider,
        'gcp': GCPProvider,
        'mock': MockProvider
    }
    
    provider_class = providers.get(provider_type.lower())
    
    if not provider_class:
        raise ValueError(f"Unknown provider type: {provider_type}")
    
    if provider_type.lower() == 'mock':
        return provider_class()
    else:
        return provider_class(credentials)
