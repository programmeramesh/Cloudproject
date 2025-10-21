import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const MetricCard = ({ title, value, unit, trend, icon: Icon, color = 'blue' }) => {
  const getTrendIcon = () => {
    if (trend > 0) return <TrendingUp className="h-4 w-4" />;
    if (trend < 0) return <TrendingDown className="h-4 w-4" />;
    return <Minus className="h-4 w-4" />;
  };

  const colorGradients = {
    blue: 'from-blue-500 to-cyan-500',
    green: 'from-green-500 to-emerald-500',
    yellow: 'from-yellow-500 to-orange-500',
    red: 'from-red-500 to-pink-500',
    purple: 'from-purple-500 to-pink-500',
  };

  const bgColors = {
    blue: 'bg-blue-50',
    green: 'bg-green-50',
    yellow: 'bg-yellow-50',
    red: 'bg-red-50',
    purple: 'bg-purple-50',
  };

  return (
    <div className="metric-card animate-scale-in group cursor-pointer">
      <div className="relative z-10 flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">
            {title}
          </p>
          <div className="flex items-baseline space-x-2">
            <p className="text-4xl font-extrabold gradient-text">
              {typeof value === 'number' ? value.toFixed(1) : value}
            </p>
            {unit && (
              <span className="text-lg font-semibold text-gray-400">
                {unit}
              </span>
            )}
          </div>
          {trend !== undefined && (
            <div className={`flex items-center mt-3 px-3 py-1.5 rounded-lg inline-flex ${
              trend > 0 
                ? 'bg-green-100 text-green-700' 
                : trend < 0 
                ? 'bg-red-100 text-red-700' 
                : 'bg-gray-100 text-gray-700'
            }`}>
              {getTrendIcon()}
              <span className="ml-1.5 text-sm font-bold">
                {trend > 0 ? '+' : ''}{Math.abs(trend).toFixed(1)}%
              </span>
              <span className="ml-1 text-xs font-medium opacity-75">
                vs last hour
              </span>
            </div>
          )}
        </div>
        
        {Icon && (
          <div className="relative">
            {/* Glow effect */}
            <div className={`absolute inset-0 bg-gradient-to-br ${colorGradients[color]} rounded-2xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity duration-300`}></div>
            
            {/* Icon container */}
            <div className={`relative p-5 rounded-2xl bg-gradient-to-br ${colorGradients[color]} shadow-lg transform group-hover:scale-110 group-hover:rotate-6 transition-all duration-300`}>
              <Icon className="h-8 w-8 text-white" />
            </div>
          </div>
        )}
      </div>

      {/* Progress bar */}
      <div className="relative z-10 mt-4">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${Math.min(typeof value === 'number' ? value : 0, 100)}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default MetricCard;
