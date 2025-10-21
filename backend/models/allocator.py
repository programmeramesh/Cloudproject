import logging
from datetime import datetime
from config import Config


class ResourceAllocator:
    """Dynamic resource allocation based on predictions"""
    
    def __init__(self, cloud_provider):
        self.cloud_provider = cloud_provider
        self.logger = logging.getLogger(__name__)
        self.cpu_threshold_high = Config.CPU_THRESHOLD_HIGH
        self.cpu_threshold_low = Config.CPU_THRESHOLD_LOW
        self.memory_threshold_high = Config.MEMORY_THRESHOLD_HIGH
        self.memory_threshold_low = Config.MEMORY_THRESHOLD_LOW
    
    def calculate_required_resources(self, predictions, current_allocation):
        """
        Calculate required resources based on predictions
        
        Args:
            predictions: List of predicted metrics
            current_allocation: Current resource allocation
            
        Returns:
            dict: Recommended resource allocation
        """
        try:
            # Extract predicted values
            predicted_cpu = predictions.get('cpu_usage', 0)
            predicted_memory = predictions.get('memory_usage', 0)
            predicted_network = predictions.get('network_usage', 0)
            
            # Current resources
            current_instances = current_allocation.get('instance_count', 1)
            current_instance_type = current_allocation.get('instance_type', 't2.micro')
            
            # Decision logic
            recommendation = {
                'timestamp': datetime.utcnow(),
                'action': 'maintain',
                'current_instances': current_instances,
                'recommended_instances': current_instances,
                'current_instance_type': current_instance_type,
                'recommended_instance_type': current_instance_type,
                'reason': 'Resources within normal range',
                'predicted_cpu': predicted_cpu,
                'predicted_memory': predicted_memory
            }
            
            # Scale up conditions
            if predicted_cpu > self.cpu_threshold_high or predicted_memory > self.memory_threshold_high:
                recommendation['action'] = 'scale_up'
                recommendation['recommended_instances'] = current_instances + 1
                recommendation['reason'] = f'High resource usage predicted: CPU={predicted_cpu}%, Memory={predicted_memory}%'
                
                # Consider vertical scaling if consistently high
                if predicted_cpu > 90 or predicted_memory > 90:
                    recommendation['recommended_instance_type'] = self._get_larger_instance_type(
                        current_instance_type
                    )
                    recommendation['reason'] += ' - Vertical scaling recommended'
            
            # Scale down conditions
            elif predicted_cpu < self.cpu_threshold_low and predicted_memory < self.memory_threshold_low:
                if current_instances > 1:
                    recommendation['action'] = 'scale_down'
                    recommendation['recommended_instances'] = current_instances - 1
                    recommendation['reason'] = f'Low resource usage predicted: CPU={predicted_cpu}%, Memory={predicted_memory}%'
                else:
                    # Consider smaller instance type
                    smaller_type = self._get_smaller_instance_type(current_instance_type)
                    if smaller_type != current_instance_type:
                        recommendation['action'] = 'scale_down'
                        recommendation['recommended_instance_type'] = smaller_type
                        recommendation['reason'] = 'Vertical scaling down recommended'
            
            # Calculate estimated cost
            recommendation['estimated_cost'] = self._estimate_cost(
                recommendation['recommended_instances'],
                recommendation['recommended_instance_type']
            )
            
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Error calculating required resources: {str(e)}")
            return None
    
    def _get_larger_instance_type(self, current_type):
        """Get next larger instance type"""
        # AWS instance type hierarchy (simplified)
        type_hierarchy = {
            't2.micro': 't2.small',
            't2.small': 't2.medium',
            't2.medium': 't2.large',
            't2.large': 't2.xlarge',
            't2.xlarge': 't2.2xlarge',
            't3.micro': 't3.small',
            't3.small': 't3.medium',
            't3.medium': 't3.large',
            't3.large': 't3.xlarge',
            't3.xlarge': 't3.2xlarge'
        }
        
        return type_hierarchy.get(current_type, current_type)
    
    def _get_smaller_instance_type(self, current_type):
        """Get next smaller instance type"""
        # Reverse hierarchy
        type_hierarchy = {
            't2.small': 't2.micro',
            't2.medium': 't2.small',
            't2.large': 't2.medium',
            't2.xlarge': 't2.large',
            't2.2xlarge': 't2.xlarge',
            't3.small': 't3.micro',
            't3.medium': 't3.small',
            't3.large': 't3.medium',
            't3.xlarge': 't3.large',
            't3.2xlarge': 't3.xlarge'
        }
        
        return type_hierarchy.get(current_type, current_type)
    
    def _estimate_cost(self, instance_count, instance_type):
        """Estimate hourly cost (simplified pricing)"""
        # Simplified AWS pricing (USD per hour)
        pricing = {
            't2.micro': 0.0116,
            't2.small': 0.023,
            't2.medium': 0.0464,
            't2.large': 0.0928,
            't2.xlarge': 0.1856,
            't2.2xlarge': 0.3712,
            't3.micro': 0.0104,
            't3.small': 0.0208,
            't3.medium': 0.0416,
            't3.large': 0.0832,
            't3.xlarge': 0.1664,
            't3.2xlarge': 0.3328
        }
        
        hourly_cost = pricing.get(instance_type, 0.0116) * instance_count
        daily_cost = hourly_cost * 24
        monthly_cost = daily_cost * 30
        
        return {
            'hourly': round(hourly_cost, 4),
            'daily': round(daily_cost, 2),
            'monthly': round(monthly_cost, 2)
        }
    
    def execute_allocation(self, recommendation):
        """
        Execute the resource allocation recommendation
        
        Args:
            recommendation: Allocation recommendation from calculate_required_resources
            
        Returns:
            dict: Execution result
        """
        try:
            action = recommendation['action']
            
            if action == 'maintain':
                return {
                    'success': True,
                    'message': 'No changes needed',
                    'action': action
                }
            
            elif action == 'scale_up':
                result = self.cloud_provider.scale_up(
                    target_instances=recommendation['recommended_instances'],
                    instance_type=recommendation['recommended_instance_type']
                )
                return result
            
            elif action == 'scale_down':
                result = self.cloud_provider.scale_down(
                    target_instances=recommendation['recommended_instances'],
                    instance_type=recommendation['recommended_instance_type']
                )
                return result
            
            else:
                return {
                    'success': False,
                    'message': f'Unknown action: {action}',
                    'action': action
                }
                
        except Exception as e:
            self.logger.error(f"Error executing allocation: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'action': recommendation.get('action', 'unknown')
            }
    
    def optimize_for_cost(self, predictions, current_allocation, budget_constraint):
        """
        Optimize allocation with cost constraints
        
        Args:
            predictions: Predicted workload
            current_allocation: Current resources
            budget_constraint: Maximum budget (monthly)
            
        Returns:
            dict: Cost-optimized recommendation
        """
        base_recommendation = self.calculate_required_resources(
            predictions, 
            current_allocation
        )
        
        if not base_recommendation:
            return None
        
        # Check if recommendation exceeds budget
        estimated_monthly = base_recommendation['estimated_cost']['monthly']
        
        if estimated_monthly > budget_constraint:
            # Find alternative that fits budget
            self.logger.info(f"Recommendation exceeds budget: ${estimated_monthly} > ${budget_constraint}")
            
            # Try to find optimal configuration within budget
            optimized = self._find_budget_optimal_config(
                predictions,
                current_allocation,
                budget_constraint
            )
            
            return optimized
        
        return base_recommendation
    
    def _find_budget_optimal_config(self, predictions, current_allocation, budget):
        """Find optimal configuration within budget constraint"""
        # Simplified: Try different combinations
        instance_types = ['t2.micro', 't2.small', 't2.medium', 't2.large']
        
        best_config = None
        best_score = -1
        
        for instance_type in instance_types:
            for instance_count in range(1, 6):
                cost = self._estimate_cost(instance_count, instance_type)
                
                if cost['monthly'] <= budget:
                    # Calculate performance score
                    score = self._calculate_performance_score(
                        instance_count,
                        instance_type,
                        predictions
                    )
                    
                    if score > best_score:
                        best_score = score
                        best_config = {
                            'instance_count': instance_count,
                            'instance_type': instance_type,
                            'estimated_cost': cost,
                            'performance_score': score
                        }
        
        if best_config:
            return {
                'timestamp': datetime.utcnow(),
                'action': 'optimize',
                'recommended_instances': best_config['instance_count'],
                'recommended_instance_type': best_config['instance_type'],
                'estimated_cost': best_config['estimated_cost'],
                'reason': f'Budget-optimized configuration (score: {best_score})',
                'predicted_cpu': predictions.get('cpu_usage', 0),
                'predicted_memory': predictions.get('memory_usage', 0)
            }
        
        return None
    
    def _calculate_performance_score(self, instance_count, instance_type, predictions):
        """Calculate performance score for a configuration"""
        # Simplified scoring based on instance capacity vs predicted load
        
        # Instance capacity (simplified)
        capacity = {
            't2.micro': 1,
            't2.small': 2,
            't2.medium': 4,
            't2.large': 8,
            't2.xlarge': 16
        }
        
        total_capacity = capacity.get(instance_type, 1) * instance_count
        predicted_load = predictions.get('cpu_usage', 50) / 10  # Normalize
        
        # Score: capacity should match load (not too much, not too little)
        if total_capacity >= predicted_load:
            score = 100 - abs(total_capacity - predicted_load) * 10
        else:
            score = 50 - (predicted_load - total_capacity) * 20  # Penalty for under-provisioning
        
        return max(0, score)
