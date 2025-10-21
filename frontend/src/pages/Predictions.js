import React, { useState, useEffect } from 'react';
import { TrendingUp, Play, Zap } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import toast from 'react-hot-toast';
import { getPredictions, generatePredictions, trainModel } from '../services/api';

const Predictions = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [training, setTraining] = useState(false);
  const [steps, setSteps] = useState(12);

  const fetchPredictions = async () => {
    try {
      const response = await getPredictions(50);
      if (response.data.success) {
        setPredictions(response.data.predictions);
      }
    } catch (error) {
      toast.error('Failed to fetch predictions');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePredictions = async () => {
    setGenerating(true);
    try {
      const response = await generatePredictions(steps);
      if (response.data.success) {
        toast.success('Predictions generated successfully');
        fetchPredictions();
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to generate predictions');
    } finally {
      setGenerating(false);
    }
  };

  const handleTrainModel = async () => {
    setTraining(true);
    try {
      const response = await trainModel({ epochs: 50, batch_size: 32 });
      if (response.data.success) {
        toast.success('Model trained successfully');
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to train model');
    } finally {
      setTraining(false);
    }
  };

  useEffect(() => {
    fetchPredictions();
  }, []);

  const latestPrediction = predictions[0];
  const predictionData = latestPrediction?.predictions || [];

  const chartData = {
    labels: predictionData.map((_, i) => `+${i + 1}h`),
    datasets: [
      {
        label: 'Predicted CPU Usage (%)',
        data: predictionData,
        borderColor: 'rgb(139, 92, 246)',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
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
        text: 'Workload Prediction (Next 12 Hours)'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'CPU Usage (%)'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Time (Hours)'
        }
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
        <h2 className="text-2xl font-bold text-gray-800">Workload Predictions</h2>
        <div className="flex space-x-2">
          <button
            onClick={handleTrainModel}
            disabled={training}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Zap className="h-4 w-4" />
            <span>{training ? 'Training...' : 'Train Model'}</span>
          </button>
          <button
            onClick={handleGeneratePredictions}
            disabled={generating}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Play className="h-4 w-4" />
            <span>{generating ? 'Generating...' : 'Generate Predictions'}</span>
          </button>
        </div>
      </div>

      {/* Prediction Settings */}
      <div className="card">
        <h3 className="card-header">Prediction Settings</h3>
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">
            Prediction Steps (Hours):
          </label>
          <input
            type="number"
            value={steps}
            onChange={(e) => setSteps(parseInt(e.target.value))}
            min="1"
            max="24"
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <span className="text-sm text-gray-600">
            Predict workload for the next {steps} hours
          </span>
        </div>
      </div>

      {/* Prediction Chart */}
      {predictionData.length > 0 ? (
        <div className="card">
          <h3 className="card-header">AI Prediction Results</h3>
          <div style={{ height: '400px' }}>
            <Line data={chartData} options={chartOptions} />
          </div>
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Model:</strong> LSTM Neural Network | 
              <strong className="ml-2">Generated:</strong> {new Date(latestPrediction?.timestamp).toLocaleString()}
            </p>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="text-center py-12">
            <TrendingUp className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-700 mb-2">
              No Predictions Available
            </h3>
            <p className="text-gray-600 mb-4">
              Generate predictions to see AI-powered workload forecasts
            </p>
            <button
              onClick={handleGeneratePredictions}
              disabled={generating}
              className="btn btn-primary"
            >
              Generate Predictions
            </button>
          </div>
        </div>
      )}

      {/* Prediction Statistics */}
      {predictionData.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card">
            <h4 className="text-sm font-medium text-gray-600 mb-2">Average Predicted Load</h4>
            <p className="text-3xl font-bold text-blue-600">
              {(predictionData.reduce((a, b) => a + b, 0) / predictionData.length).toFixed(1)}%
            </p>
          </div>
          <div className="card">
            <h4 className="text-sm font-medium text-gray-600 mb-2">Peak Predicted Load</h4>
            <p className="text-3xl font-bold text-red-600">
              {Math.max(...predictionData).toFixed(1)}%
            </p>
          </div>
          <div className="card">
            <h4 className="text-sm font-medium text-gray-600 mb-2">Minimum Predicted Load</h4>
            <p className="text-3xl font-bold text-green-600">
              {Math.min(...predictionData).toFixed(1)}%
            </p>
          </div>
        </div>
      )}

      {/* Model Information */}
      <div className="card">
        <h3 className="card-header">Model Information</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-600">Model Type</span>
            <span className="font-semibold text-gray-900">LSTM Neural Network</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-600">Sequence Length</span>
            <span className="font-semibold text-gray-900">24 hours</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-gray-600">Training Epochs</span>
            <span className="font-semibold text-gray-900">50</span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-gray-600">Prediction Accuracy</span>
            <span className="font-semibold text-green-600">&gt; 85%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Predictions;
