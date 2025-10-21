import React, { useState, useEffect } from 'react';
import { Cpu, MemoryStick, Network, DollarSign, TrendingUp, AlertCircle } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import toast from 'react-hot-toast';
import MetricCard from '../components/MetricCard';
import { getDashboardStats, getHistory } from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(null);

  const fetchData = async () => {
    try {
      const [statsRes, historyRes] = await Promise.all([
        getDashboardStats(),
        getHistory(7)
      ]);

      if (statsRes.data.success) {
        setStats(statsRes.data.stats);
      }

      if (historyRes.data.success) {
        setHistory(historyRes.data);
      }
    } catch (error) {
      toast.error('Failed to fetch dashboard data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    setRefreshInterval(interval);

    return () => {
      if (refreshInterval) clearInterval(refreshInterval);
    };
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const currentMetrics = stats?.current_metrics || {};
  const costTrends = stats?.cost_trends || {};

  // Prepare chart data
  const chartData = {
    labels: history?.metrics?.slice(-20).map((m, i) => `T-${20-i}`) || [],
    datasets: [
      {
        label: 'CPU Usage (%)',
        data: history?.metrics?.slice(-20).map(m => m.cpu_usage) || [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Memory Usage (%)',
        data: history?.metrics?.slice(-20).map(m => m.memory_usage) || [],
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Resource Usage Trends'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Dashboard Overview</h2>
        <button
          onClick={fetchData}
          className="btn btn-primary"
        >
          Refresh
        </button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="CPU Usage"
          value={currentMetrics.cpu_usage || 0}
          unit="%"
          trend={2.5}
          icon={Cpu}
          color="blue"
        />
        <MetricCard
          title="Memory Usage"
          value={currentMetrics.memory_usage || 0}
          unit="%"
          trend={-1.2}
          icon={MemoryStick}
          color="green"
        />
        <MetricCard
          title="Network Usage"
          value={currentMetrics.network_usage || 0}
          unit="%"
          trend={0.8}
          icon={Network}
          color="purple"
        />
        <MetricCard
          title="Monthly Cost"
          value={costTrends.projected_monthly_cost || 0}
          unit="$"
          trend={-5.3}
          icon={DollarSign}
          color="yellow"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="card-header">Resource Usage Trends</h3>
          <div style={{ height: '300px' }}>
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>

        <div className="card">
          <h3 className="card-header">System Information</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Active Instances</span>
              <span className="font-semibold text-gray-900">
                {stats?.current_allocation?.instance_count || 0}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Instance Type</span>
              <span className="font-semibold text-gray-900">
                {stats?.current_allocation?.instance_type || 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Optimization Score</span>
              <span className="font-semibold text-green-600">
                {stats?.optimization_score || 0}/100
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-gray-600">Cost Trend</span>
              <span className={`badge ${
                costTrends.trend === 'decreasing' ? 'badge-success' :
                costTrends.trend === 'increasing' ? 'badge-danger' :
                'badge-info'
              }`}>
                {costTrends.trend || 'stable'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-gray-600">Avg Daily Cost</span>
              <span className="font-semibold text-gray-900">
                ${costTrends.average_daily_cost?.toFixed(2) || '0.00'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="card-header">Recent Allocations</h3>
        <div className="space-y-3">
          {stats?.recent_allocations_count > 0 ? (
            <div className="text-center py-4">
              <TrendingUp className="h-12 w-12 text-blue-500 mx-auto mb-2" />
              <p className="text-gray-600">
                {stats.recent_allocations_count} resource allocation(s) in the last 24 hours
              </p>
            </div>
          ) : (
            <div className="text-center py-4">
              <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600">No recent allocations</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
