import logging
from datetime import datetime, timedelta
from config import Config


class CostOptimizer:
    """Cost optimization service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cost_weight = Config.COST_WEIGHT
        self.performance_weight = Config.PERFORMANCE_WEIGHT
    
    def calculate_optimization_score(self, allocation, metrics):
        """
        Calculate optimization score balancing cost and performance
        
        Args:
            allocation: Resource allocation details
            metrics: Performance metrics
            
        Returns:
            float: Optimization score (0-100)
        """
        try:
            # Cost score (lower cost = higher score)
            cost_score = self._calculate_cost_score(allocation)
            
            # Performance score (better performance = higher score)
            performance_score = self._calculate_performance_score(metrics)
            
            # Weighted combination
            total_score = (
                self.cost_weight * cost_score +
                self.performance_weight * performance_score
            )
            
            return round(total_score, 2)
            
        except Exception as e:
            self.logger.error(f"Error calculating optimization score: {str(e)}")
            return 0.0
    
    def _calculate_cost_score(self, allocation):
        """Calculate cost efficiency score"""
        # Simplified cost scoring
        # Lower cost per unit of compute = higher score
        
        instance_count = allocation.get('instance_count', 1)
        instance_type = allocation.get('instance_type', 't2.micro')
        
        # Base costs (simplified)
        base_costs = {
            't2.micro': 0.0116,
            't2.small': 0.023,
            't2.medium': 0.0464,
            't2.large': 0.0928,
            't2.xlarge': 0.1856
        }
        
        hourly_cost = base_costs.get(instance_type, 0.0116) * instance_count
        
        # Normalize to 0-100 scale (assuming max reasonable cost is $5/hour)
        max_cost = 5.0
        cost_score = max(0, 100 - (hourly_cost / max_cost) * 100)
        
        return cost_score
    
    def _calculate_performance_score(self, metrics):
        """Calculate performance score"""
        try:
            cpu_usage = metrics.get('cpu_usage', 0)
            memory_usage = metrics.get('memory_usage', 0)
            
            # Optimal range: 60-80% utilization
            optimal_min = 60
            optimal_max = 80
            
            # CPU score
            if optimal_min <= cpu_usage <= optimal_max:
                cpu_score = 100
            elif cpu_usage < optimal_min:
                cpu_score = 100 - (optimal_min - cpu_usage) * 2
            else:
                cpu_score = 100 - (cpu_usage - optimal_max) * 3
            
            # Memory score
            if optimal_min <= memory_usage <= optimal_max:
                memory_score = 100
            elif memory_usage < optimal_min:
                memory_score = 100 - (optimal_min - memory_usage) * 2
            else:
                memory_score = 100 - (memory_usage - optimal_max) * 3
            
            # Average score
            performance_score = (cpu_score + memory_score) / 2
            
            return max(0, min(100, performance_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating performance score: {str(e)}")
            return 50.0
    
    def analyze_cost_trends(self, cost_history):
        """
        Analyze cost trends over time
        
        Args:
            cost_history: List of cost records with timestamps
            
        Returns:
            dict: Cost trend analysis
        """
        try:
            if not cost_history:
                return {
                    'trend': 'stable',
                    'average_daily_cost': 0,
                    'total_cost': 0,
                    'projected_monthly_cost': 0
                }
            
            # Calculate daily costs
            daily_costs = {}
            for record in cost_history:
                date = record['timestamp'].date()
                cost = record.get('cost', 0)
                
                if date in daily_costs:
                    daily_costs[date] += cost
                else:
                    daily_costs[date] = cost
            
            # Calculate statistics
            costs = list(daily_costs.values())
            avg_daily_cost = sum(costs) / len(costs) if costs else 0
            total_cost = sum(costs)
            
            # Determine trend
            if len(costs) >= 7:
                recent_avg = sum(costs[-7:]) / 7
                older_avg = sum(costs[:-7]) / len(costs[:-7]) if len(costs) > 7 else recent_avg
                
                if recent_avg > older_avg * 1.1:
                    trend = 'increasing'
                elif recent_avg < older_avg * 0.9:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            # Project monthly cost
            projected_monthly_cost = avg_daily_cost * 30
            
            return {
                'trend': trend,
                'average_daily_cost': round(avg_daily_cost, 2),
                'total_cost': round(total_cost, 2),
                'projected_monthly_cost': round(projected_monthly_cost, 2),
                'days_analyzed': len(costs)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing cost trends: {str(e)}")
            return {
                'trend': 'error',
                'error': str(e)
            }
    
    def recommend_savings(self, current_allocation, metrics, predictions):
        """
        Recommend cost-saving opportunities
        
        Args:
            current_allocation: Current resource allocation
            metrics: Current performance metrics
            predictions: Predicted workload
            
        Returns:
            list: List of savings recommendations
        """
        recommendations = []
        
        try:
            # Check for over-provisioning
            cpu_usage = metrics.get('cpu_usage', 0)
            memory_usage = metrics.get('memory_usage', 0)
            
            if cpu_usage < 30 and memory_usage < 30:
                recommendations.append({
                    'type': 'downsize',
                    'priority': 'high',
                    'description': 'Resources are significantly under-utilized',
                    'potential_savings': '30-40%',
                    'action': 'Consider downsizing instance type or reducing instance count'
                })
            
            # Check for consistent low usage
            predicted_cpu = predictions.get('cpu_usage', 0)
            if cpu_usage < 40 and predicted_cpu < 40:
                recommendations.append({
                    'type': 'schedule',
                    'priority': 'medium',
                    'description': 'Consistent low usage detected',
                    'potential_savings': '20-30%',
                    'action': 'Consider implementing scheduled scaling or spot instances'
                })
            
            # Check for instance type optimization
            instance_type = current_allocation.get('instance_type', '')
            if 't2.' in instance_type:
                recommendations.append({
                    'type': 'instance_type',
                    'priority': 'low',
                    'description': 'T2 instances detected',
                    'potential_savings': '10-20%',
                    'action': 'Consider T3 instances for better price-performance ratio'
                })
            
            # Check for reserved instance opportunities
            if len(recommendations) == 0:
                recommendations.append({
                    'type': 'reserved',
                    'priority': 'low',
                    'description': 'Stable workload detected',
                    'potential_savings': '30-50%',
                    'action': 'Consider reserved instances for long-term cost savings'
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    def calculate_roi(self, baseline_cost, optimized_cost, implementation_cost=0):
        """
        Calculate ROI of optimization
        
        Args:
            baseline_cost: Cost before optimization (monthly)
            optimized_cost: Cost after optimization (monthly)
            implementation_cost: One-time implementation cost
            
        Returns:
            dict: ROI analysis
        """
        try:
            monthly_savings = baseline_cost - optimized_cost
            annual_savings = monthly_savings * 12
            
            if implementation_cost > 0:
                payback_period = implementation_cost / monthly_savings if monthly_savings > 0 else float('inf')
                roi_percentage = ((annual_savings - implementation_cost) / implementation_cost) * 100 if implementation_cost > 0 else 0
            else:
                payback_period = 0
                roi_percentage = 100
            
            return {
                'monthly_savings': round(monthly_savings, 2),
                'annual_savings': round(annual_savings, 2),
                'implementation_cost': implementation_cost,
                'payback_period_months': round(payback_period, 1),
                'roi_percentage': round(roi_percentage, 2),
                'savings_percentage': round((monthly_savings / baseline_cost) * 100, 2) if baseline_cost > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating ROI: {str(e)}")
            return {
                'error': str(e)
            }
    
    def generate_cost_report(self, start_date, end_date, cost_history, allocations):
        """
        Generate comprehensive cost report
        
        Args:
            start_date: Report start date
            end_date: Report end date
            cost_history: Historical cost data
            allocations: Historical allocation data
            
        Returns:
            dict: Comprehensive cost report
        """
        try:
            # Filter data by date range
            filtered_costs = [
                c for c in cost_history
                if start_date <= c['timestamp'] <= end_date
            ]
            
            # Calculate totals
            total_cost = sum(c.get('cost', 0) for c in filtered_costs)
            days = (end_date - start_date).days + 1
            avg_daily_cost = total_cost / days if days > 0 else 0
            
            # Cost breakdown by resource type
            cost_by_type = {}
            for record in filtered_costs:
                resource_type = record.get('resource_type', 'unknown')
                cost = record.get('cost', 0)
                
                if resource_type in cost_by_type:
                    cost_by_type[resource_type] += cost
                else:
                    cost_by_type[resource_type] = cost
            
            # Allocation changes
            allocation_changes = len([
                a for a in allocations
                if start_date <= a['timestamp'] <= end_date
            ])
            
            report = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'costs': {
                    'total': round(total_cost, 2),
                    'average_daily': round(avg_daily_cost, 2),
                    'projected_monthly': round(avg_daily_cost * 30, 2),
                    'by_resource_type': {k: round(v, 2) for k, v in cost_by_type.items()}
                },
                'allocations': {
                    'total_changes': allocation_changes,
                    'average_per_day': round(allocation_changes / days, 2) if days > 0 else 0
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating cost report: {str(e)}")
            return {
                'error': str(e)
            }
