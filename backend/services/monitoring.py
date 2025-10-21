import psutil
import time
from datetime import datetime
from threading import Thread
import logging


class WorkloadMonitor:
    """Monitor system workload metrics"""
    
    def __init__(self, interval=60):
        self.interval = interval
        self.running = False
        self.metrics_callback = None
        self.logger = logging.getLogger(__name__)
    
    def get_current_metrics(self):
        """Get current system metrics"""
        try:
            import os
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count() or 1
            try:
                cpu_freq = psutil.cpu_freq()
                cpu_frequency = cpu_freq.current if cpu_freq else 0
            except:
                cpu_frequency = 0
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024 ** 3)  # GB
            memory_total = memory.total / (1024 ** 3)  # GB
            
            # Disk metrics
            try:
                disk_path = 'C:\\' if os.name == 'nt' else '/'
                disk = psutil.disk_usage(disk_path)
                disk_percent = disk.percent
                disk_used = disk.used / (1024 ** 3)  # GB
                disk_total = disk.total / (1024 ** 3)  # GB
            except:
                disk_percent = 0
                disk_used = 0
                disk_total = 0
            
            # Network metrics
            try:
                net_io = psutil.net_io_counters()
                bytes_sent = net_io.bytes_sent / (1024 ** 2)  # MB
                bytes_recv = net_io.bytes_recv / (1024 ** 2)  # MB
                network_usage = self._calculate_network_usage(net_io)
            except:
                bytes_sent = 0
                bytes_recv = 0
                network_usage = 0
            
            # Disk I/O
            try:
                disk_io = psutil.disk_io_counters()
                read_bytes = disk_io.read_bytes / (1024 ** 2)  # MB
                write_bytes = disk_io.write_bytes / (1024 ** 2)  # MB
                disk_io_usage = self._calculate_disk_io(disk_io)
            except:
                read_bytes = 0
                write_bytes = 0
                disk_io_usage = 0
            
            metrics = {
                'timestamp': datetime.utcnow(),
                'cpu_usage': cpu_percent,
                'cpu_count': cpu_count,
                'cpu_frequency': cpu_frequency,
                'memory_usage': memory_percent,
                'memory_used_gb': round(memory_used, 2),
                'memory_total_gb': round(memory_total, 2),
                'disk_usage': disk_percent,
                'disk_used_gb': round(disk_used, 2),
                'disk_total_gb': round(disk_total, 2),
                'network_sent_mb': round(bytes_sent, 2),
                'network_recv_mb': round(bytes_recv, 2),
                'disk_read_mb': round(read_bytes, 2),
                'disk_write_mb': round(write_bytes, 2),
                'network_usage': network_usage,
                'disk_io': disk_io_usage
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def _calculate_network_usage(self, net_io):
        """Calculate network usage percentage (simplified)"""
        # This is a simplified calculation
        # In production, you'd track delta over time
        total_bytes = net_io.bytes_sent + net_io.bytes_recv
        # Assume 1 Gbps network capacity
        max_capacity = 1000 * 1024 * 1024  # bytes per second
        usage = min((total_bytes / max_capacity) * 100, 100)
        return round(usage, 2)
    
    def _calculate_disk_io(self, disk_io):
        """Calculate disk I/O percentage (simplified)"""
        total_io = disk_io.read_bytes + disk_io.write_bytes
        # Simplified calculation
        max_io = 500 * 1024 * 1024  # 500 MB/s assumed max
        usage = min((total_io / max_io) * 100, 100)
        return round(usage, 2)
    
    def get_process_metrics(self, top_n=10):
        """Get metrics for top N processes by CPU usage"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': pinfo['cpu_percent'],
                    'memory_percent': pinfo['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes[:top_n]
    
    def start_monitoring(self, callback=None):
        """Start continuous monitoring in background thread"""
        if self.running:
            self.logger.warning("Monitoring already running")
            return
        
        self.running = True
        self.metrics_callback = callback
        
        monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        
        self.logger.info(f"Started monitoring with {self.interval}s interval")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                metrics = self.get_current_metrics()
                
                if metrics and self.metrics_callback:
                    self.metrics_callback(metrics)
                
                time.sleep(self.interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(self.interval)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        self.logger.info("Stopped monitoring")
    
    def get_system_info(self):
        """Get static system information"""
        try:
            import platform
            try:
                boot_time_str = datetime.fromtimestamp(psutil.boot_time()).isoformat()
            except:
                boot_time_str = "N/A"
            
            return {
                'hostname': platform.node(),
                'platform': platform.system(),
                'platform_release': platform.release(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'cpu_count_physical': psutil.cpu_count(logical=False) or 1,
                'cpu_count_logical': psutil.cpu_count(logical=True) or 1,
                'memory_total_gb': round(psutil.virtual_memory().total / (1024 ** 3), 2),
                'boot_time': boot_time_str
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {str(e)}")
            return {}


class CloudResourceMonitor:
    """Monitor cloud resources (AWS/Azure/GCP)"""
    
    def __init__(self, provider='aws', credentials=None):
        self.provider = provider
        self.credentials = credentials
        self.logger = logging.getLogger(__name__)
    
    def get_aws_metrics(self, instance_ids=None):
        """Get AWS EC2 instance metrics"""
        try:
            import boto3
            
            ec2 = boto3.client('ec2', **self.credentials)
            cloudwatch = boto3.client('cloudwatch', **self.credentials)
            
            # Get instance information
            if instance_ids:
                response = ec2.describe_instances(InstanceIds=instance_ids)
            else:
                response = ec2.describe_instances()
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_data = {
                        'instance_id': instance['InstanceId'],
                        'instance_type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'launch_time': instance['LaunchTime'],
                        'availability_zone': instance['Placement']['AvailabilityZone']
                    }
                    
                    # Get CloudWatch metrics
                    metrics = self._get_cloudwatch_metrics(
                        cloudwatch, 
                        instance['InstanceId']
                    )
                    instance_data.update(metrics)
                    
                    instances.append(instance_data)
            
            return instances
            
        except Exception as e:
            self.logger.error(f"Error getting AWS metrics: {str(e)}")
            return []
    
    def _get_cloudwatch_metrics(self, cloudwatch, instance_id):
        """Get CloudWatch metrics for an instance"""
        from datetime import timedelta
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=5)
        
        metrics = {}
        
        # CPU Utilization
        try:
            cpu_response = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            if cpu_response['Datapoints']:
                metrics['cpu_usage'] = cpu_response['Datapoints'][0]['Average']
        except:
            metrics['cpu_usage'] = 0
        
        return metrics
    
    def get_azure_metrics(self, resource_group=None):
        """Get Azure VM metrics"""
        try:
            from azure.identity import DefaultAzureCredential
            from azure.mgmt.compute import ComputeManagementClient
            
            credential = DefaultAzureCredential()
            compute_client = ComputeManagementClient(
                credential, 
                self.credentials.get('subscription_id')
            )
            
            vms = []
            if resource_group:
                vm_list = compute_client.virtual_machines.list(resource_group)
            else:
                vm_list = compute_client.virtual_machines.list_all()
            
            for vm in vm_list:
                vm_data = {
                    'vm_id': vm.id,
                    'vm_name': vm.name,
                    'vm_size': vm.hardware_profile.vm_size,
                    'location': vm.location,
                    'provisioning_state': vm.provisioning_state
                }
                vms.append(vm_data)
            
            return vms
            
        except Exception as e:
            self.logger.error(f"Error getting Azure metrics: {str(e)}")
            return []
    
    def get_gcp_metrics(self, project_id, zone=None):
        """Get GCP Compute Engine metrics"""
        try:
            from google.cloud import compute_v1
            
            instances_client = compute_v1.InstancesClient()
            
            instances = []
            
            if zone:
                request = compute_v1.ListInstancesRequest(
                    project=project_id,
                    zone=zone
                )
                instance_list = instances_client.list(request=request)
            else:
                # List all instances across zones
                zones_client = compute_v1.ZonesClient()
                zones_request = compute_v1.ListZonesRequest(project=project_id)
                zones_list = zones_client.list(request=zones_request)
                
                instance_list = []
                for zone_obj in zones_list:
                    request = compute_v1.ListInstancesRequest(
                        project=project_id,
                        zone=zone_obj.name
                    )
                    instance_list.extend(instances_client.list(request=request))
            
            for instance in instance_list:
                instance_data = {
                    'instance_id': instance.id,
                    'instance_name': instance.name,
                    'machine_type': instance.machine_type,
                    'status': instance.status,
                    'zone': instance.zone
                }
                instances.append(instance_data)
            
            return instances
            
        except Exception as e:
            self.logger.error(f"Error getting GCP metrics: {str(e)}")
            return []
