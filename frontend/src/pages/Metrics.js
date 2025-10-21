import React, { useState, useEffect } from 'react';
import { RefreshCw, Download } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import toast from 'react-hot-toast';
import { getMetrics, getCurrentMetrics } from '../services/api';

const Metrics = () => {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentMetric, setCurrentMetric] = useState(null);

  const fetchMetrics = async () => {
    try {
      const response = await getMetrics({ limit: 100 });
      if (response.data.success) {
        setMetrics(response.data.metrics);
      }
    } catch (error) {
      toast.error('Failed to fetch metrics');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentMetric = async () => {
    try {
      const response = await getCurrentMetrics();
      if (response.data.success) {
        setCurrentMetric(response.data.metrics);
        toast.success('Metrics updated');
        fetchMetrics(); // Refresh list
      }
    } catch (error) {
      toast.error('Failed to fetch current metrics');
    }
  };

  useEffect(() => {
    fetchMetrics();
    fetchCurrentMetric();

    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchCurrentMetric, 60000);
    return () => clearInterval(interval);
  }, []);

  const chartData = {
    labels: metrics.slice(-30).map((_, i) => `T-${30-i}`),
    datasets: [
      {
        label: 'CPU Usage (%)',
        data: metrics.slice(-30).map(m => m.cpu_usage),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
      },
      {
        label: 'Memory Usage (%)',
        data: metrics.slice(-30).map(m => m.memory_usage),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
      },
      {
        label: 'Disk Usage (%)',
        data: metrics.slice(-30).map(m => m.disk_usage),
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        fill: true,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">System Metrics</h2>
        <div className="flex space-x-2">
          <button
            onClick={fetchCurrentMetric}
            className="btn btn-primary flex items-center space-x-2"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </button>
          <button className="btn btn-secondary flex items-center space-x-2">
            <Download className="h-4 w-4" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Current Metrics */}
      {currentMetric && (
        <div className="card">
          <h3 className="card-header">Current System Status</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600">CPU Usage</p>
              <p className="text-2xl font-bold text-blue-600">
                {currentMetric.cpu_usage?.toFixed(1)}%
              </p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600">Memory Usage</p>
              <p className="text-2xl font-bold text-green-600">
                {currentMetric.memory_usage?.toFixed(1)}%
              </p>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <p className="text-sm text-gray-600">Disk Usage</p>
              <p className="text-2xl font-bold text-yellow-600">
                {currentMetric.disk_usage?.toFixed(1)}%
              </p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600">Network Usage</p>
              <p className="text-2xl font-bold text-purple-600">
                {currentMetric.network_usage?.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="card">
        <h3 className="card-header">Historical Metrics</h3>
        <div style={{ height: '400px' }}>
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>

      {/* Metrics Table */}
      <div className="card">
        <h3 className="card-header">Recent Metrics</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CPU (%)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Memory (%)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Disk (%)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Network (%)
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {metrics.slice(0, 10).map((metric, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(metric.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.cpu_usage?.toFixed(1)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.memory_usage?.toFixed(1)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.disk_usage?.toFixed(1)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {metric.network_usage?.toFixed(1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Metrics;
