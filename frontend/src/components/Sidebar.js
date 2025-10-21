import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Activity, TrendingUp, Server, Sparkles } from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard', gradient: 'from-blue-500 to-cyan-500' },
    { path: '/metrics', icon: Activity, label: 'Metrics', gradient: 'from-green-500 to-emerald-500' },
    { path: '/predictions', icon: TrendingUp, label: 'Predictions', gradient: 'from-purple-500 to-pink-500' },
    { path: '/resources', icon: Server, label: 'Resources', gradient: 'from-orange-500 to-red-500' },
  ];

  return (
    <div className="sidebar-gradient text-white w-72 space-y-8 py-8 px-4 flex flex-col shadow-2xl relative overflow-hidden">
      {/* Decorative gradient overlay */}
      <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
        <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500 rounded-full filter blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500 rounded-full filter blur-3xl"></div>
      </div>

      {/* Logo */}
      <div className="relative flex items-center space-x-3 px-4 animate-fade-in">
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl blur-lg opacity-75 animate-pulse"></div>
          <div className="relative bg-gradient-to-br from-purple-600 to-pink-600 p-3 rounded-xl shadow-xl">
            <Sparkles className="h-7 w-7 text-white" />
          </div>
        </div>
        <div>
          <h1 className="text-2xl font-extrabold bg-gradient-to-r from-purple-300 to-pink-300 bg-clip-text text-transparent">
            CloudOpt
          </h1>
          <p className="text-xs text-gray-400 font-medium">AI-Powered</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2 relative">
        {menuItems.map((item, index) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`group relative flex items-center space-x-3 py-3.5 px-4 rounded-xl transition-all duration-300 animate-slide-in-left ${
                isActive
                  ? 'bg-white/10 backdrop-blur-lg shadow-lg scale-105'
                  : 'hover:bg-white/5 hover:scale-102'
              }`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {/* Active indicator */}
              {isActive && (
                <div className={`absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-12 bg-gradient-to-b ${item.gradient} rounded-r-full shadow-lg`}></div>
              )}
              
              {/* Icon with gradient background */}
              <div className={`relative p-2 rounded-lg transition-all duration-300 ${
                isActive 
                  ? `bg-gradient-to-br ${item.gradient}` 
                  : 'bg-white/5 group-hover:bg-white/10'
              }`}>
                <Icon className={`h-5 w-5 transition-all duration-300 ${
                  isActive ? 'text-white' : 'text-gray-300 group-hover:text-white'
                }`} />
              </div>
              
              {/* Label */}
              <span className={`font-semibold transition-all duration-300 ${
                isActive ? 'text-white' : 'text-gray-300 group-hover:text-white'
              }`}>
                {item.label}
              </span>

              {/* Hover effect */}
              {!isActive && (
                <div className={`absolute inset-0 bg-gradient-to-r ${item.gradient} opacity-0 group-hover:opacity-10 rounded-xl transition-opacity duration-300`}></div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="relative px-4 py-4 bg-white/5 backdrop-blur-lg rounded-xl border border-white/10">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
          <span className="text-sm font-semibold text-gray-300">System Active</span>
        </div>
        <div className="text-xs text-gray-400 space-y-1">
          <p className="font-medium">Version 1.0.0</p>
          <p className="text-gray-500">© 2024 CloudOpt AI</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
