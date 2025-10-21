import React from 'react';
import { Bell, User, LogOut, Zap } from 'lucide-react';

const Header = ({ onLogout }) => {
  return (
    <header className="glass border-b border-purple-100 sticky top-0 z-40">
      <div className="flex items-center justify-between px-8 py-5">
        <div className="animate-fade-in">
          <div className="flex items-center space-x-3 mb-1">
            <h1 className="text-3xl font-extrabold gradient-text">
              Cloud Resource Optimizer
            </h1>
            <div className="px-3 py-1 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full">
              <span className="text-xs font-bold text-white flex items-center gap-1">
                <Zap className="h-3 w-3" />
                AI
              </span>
            </div>
          </div>
          <p className="text-sm text-gray-600 font-medium">
            Intelligent Resource Allocation & Cost Optimization
          </p>
        </div>

        <div className="flex items-center space-x-4 animate-slide-in-right">
          {/* Notifications */}
          <button className="relative p-3 text-gray-600 hover:bg-purple-50 rounded-xl transition-all duration-300 hover:scale-110 group">
            <Bell className="h-5 w-5 group-hover:text-purple-600 transition-colors" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-gradient-to-r from-red-500 to-pink-500 rounded-full animate-pulse shadow-lg"></span>
          </button>

          {/* User Profile */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-3 px-4 py-2.5 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200 shadow-sm hover:shadow-md transition-all duration-300">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full blur-md opacity-50"></div>
                <div className="relative bg-gradient-to-br from-purple-600 to-pink-600 p-2 rounded-full">
                  <User className="h-4 w-4 text-white" />
                </div>
              </div>
              <div className="text-left">
                <p className="text-sm font-bold text-gray-800">Admin</p>
                <p className="text-xs text-gray-500">Administrator</p>
              </div>
            </div>

            {/* Logout Button */}
            <button
              onClick={onLogout}
              className="p-3 text-gray-600 hover:bg-red-50 hover:text-red-600 rounded-xl transition-all duration-300 hover:scale-110 group"
              title="Logout"
            >
              <LogOut className="h-5 w-5 group-hover:rotate-12 transition-transform" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
