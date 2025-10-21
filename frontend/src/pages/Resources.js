import React, { useState, useEffect } from 'react';
import { Server, ArrowUp, ArrowDown, CheckCircle, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import { getResources, getRecommendations, allocateResources } from '../services/api';

const Resources = () => {
  const [resources, setResources] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [allocating, setAllocating] = useState(false);

  const fetchData = async () => {
    try {
      const [resourcesRes, recommendationRes] = await Promise.all([
        getResources(),
        getRecommendations()
      ]);

      if (resourcesRes.data.success) {
        setResources(resourcesRes.data.allocation);
      }

      if (recommendationRes.data.success) {
        setRecommendation(recommendationRes.data.recommendation);
      }
    } catch (error) {
      toast.error('Failed to fetch resource data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleAllocate = async () => {
    setAllocating(true);
    try {
      const response = await allocateResources({ recommendation });
      if (response.data.success) {
        toast.success('Resources allocated successfully');
        fetchData();
      } else {
        toast.error('Failed to allocate resources');
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to allocate resources');
    } finally {
      setAllocating(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const getActionIcon = (action) => {
    switch (action) {
      case 'scale_up':
        return <ArrowUp className="h-5 w-5 text-green-600" />;
      case 'scale_down':
        return <ArrowDown className="h-5 w-5 text-blue-600" />;
      case 'maintain':
        return <CheckCircle className="h-5 w-5 text-gray-600" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
    }
  };

  const getActionColor = (action) => {
    switch (action) {
      case 'scale_up':
        return 'bg-green-100 text-green-800';
      case 'scale_down':
        return 'bg-blue-100 text-blue-800';
      case 'maintain':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Resource Allocation</h2>
        <button
          onClick={fetchData}
          className="btn btn-secondary"
        >
          Refresh
        </button>
      </div>

      {/* Current Resources */}
      <div className="card">
        <h3 className="card-header">Current Allocation</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-6 bg-blue-50 rounded-lg">
            <Server className="h-12 w-12 text-blue-600 mx-auto mb-2" />
            <p className="text-sm text-gray-600 mb-1">Active Instances</p>
            <p className="text-4xl font-bold text-blue-600">
              {resources?.instance_count || 0}
            </p>
          </div>
          <div className="text-center p-6 bg-purple-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Instance Type</p>
            <p className="text-2xl font-bold text-purple-600">
              {resources?.instance_type || 'N/A'}
            </p>
          </div>
          <div className="text-center p-6 bg-green-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Total Instances</p>
            <p className="text-4xl font-bold text-green-600">
              {resources?.instances?.length || 0}
            </p>
          </div>
        </div>
      </div>

      {/* Recommendation */}
      {recommendation && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">AI Recommendation</h3>
            <span className={`badge ${getActionColor(recommendation.action)}`}>
              {recommendation.action?.replace('_', ' ').toUpperCase()}
            </span>
          </div>

          <div className="space-y-4">
            <div className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
              {getActionIcon(recommendation.action)}
              <div className="flex-1">
                <p className="font-medium text-gray-900 mb-1">Recommendation</p>
                <p className="text-sm text-gray-600">{recommendation.reason}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-white border border-gray-200 rounded-lg">
                <p className="text-xs text-gray-600 mb-1">Current Instances</p>
                <p className="text-2xl font-bold text-gray-900">
                  {recommendation.current_instances}
                </p>
              </div>
              <div className="p-4 bg-white border border-gray-200 rounded-lg">
                <p className="text-xs text-gray-600 mb-1">Recommended Instances</p>
                <p className="text-2xl font-bold text-blue-600">
                  {recommendation.recommended_instances}
                </p>
              </div>
              <div className="p-4 bg-white border border-gray-200 rounded-lg">
                <p className="text-xs text-gray-600 mb-1">Predicted CPU</p>
                <p className="text-2xl font-bold text-purple-600">
                  {recommendation.predicted_cpu?.toFixed(1)}%
                </p>
              </div>
              <div className="p-4 bg-white border border-gray-200 rounded-lg">
                <p className="text-xs text-gray-600 mb-1">Predicted Memory</p>
                <p className="text-2xl font-bold text-green-600">
                  {recommendation.predicted_memory?.toFixed(1)}%
                </p>
              </div>
            </div>

            {/* Cost Estimation */}
            {recommendation.estimated_cost && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">Cost Estimation</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-xs text-gray-600">Hourly</p>
                    <p className="text-lg font-bold text-gray-900">
                      ${recommendation.estimated_cost.hourly}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Daily</p>
                    <p className="text-lg font-bold text-gray-900">
                      ${recommendation.estimated_cost.daily}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Monthly</p>
                    <p className="text-lg font-bold text-gray-900">
                      ${recommendation.estimated_cost.monthly}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Action Button */}
            {recommendation.action !== 'maintain' && (
              <button
                onClick={handleAllocate}
                disabled={allocating}
                className="w-full btn btn-primary py-3 text-lg font-semibold"
              >
                {allocating ? 'Allocating...' : 'Apply Recommendation'}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Instance List */}
      {resources?.instances && resources.instances.length > 0 && (
        <div className="card">
          <h3 className="card-header">Instance Details</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Instance ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    State
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Launch Time
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {resources.instances.map((instance, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {instance.instance_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {instance.instance_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="badge badge-success">
                        {instance.state}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {instance.launch_time ? new Date(instance.launch_time).toLocaleString() : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Resources;
