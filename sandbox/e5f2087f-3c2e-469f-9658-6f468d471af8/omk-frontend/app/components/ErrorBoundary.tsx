'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in the child component tree
 * Prevents white screen crashes and provides user-friendly fallback UI
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so next render shows fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to error reporting service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });

    // TODO: Send to error tracking service (Sentry, LogRocket, etc.)
    // trackError(error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 flex items-center justify-center p-4">
          <div className="max-w-2xl w-full">
            <div className="bg-gradient-to-br from-red-900/20 to-gray-900/50 border border-red-500/30 rounded-2xl p-8 backdrop-blur-sm">
              {/* Icon */}
              <div className="flex justify-center mb-6">
                <div className="p-4 bg-red-500/20 rounded-full">
                  <AlertTriangle className="w-12 h-12 text-red-500" />
                </div>
              </div>

              {/* Title */}
              <h1 className="text-3xl font-bold text-white text-center mb-2">
                Something went wrong
              </h1>
              
              {/* Description */}
              <p className="text-gray-400 text-center mb-6">
                We encountered an unexpected error. Don't worry, our team has been notified.
              </p>

              {/* Error Details (in development) */}
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="mb-6 p-4 bg-black/50 border border-red-500/20 rounded-lg">
                  <h3 className="text-sm font-semibold text-red-400 mb-2">Error Details:</h3>
                  <pre className="text-xs text-red-300 overflow-x-auto">
                    {this.state.error.toString()}
                  </pre>
                  {this.state.errorInfo && (
                    <details className="mt-2">
                      <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-400">
                        Component Stack
                      </summary>
                      <pre className="text-xs text-gray-400 mt-2 overflow-x-auto">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </details>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={this.handleReset}
                  className="flex-1 px-6 py-3 bg-yellow-600 hover:bg-yellow-700 text-black font-semibold rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Try Again
                </button>
                
                <button
                  onClick={this.handleReload}
                  className="flex-1 px-6 py-3 bg-gray-800 hover:bg-gray-700 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 border border-gray-700"
                >
                  <RefreshCw className="w-4 h-4" />
                  Reload Page
                </button>
                
                <button
                  onClick={this.handleGoHome}
                  className="flex-1 px-6 py-3 bg-gray-800 hover:bg-gray-700 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 border border-gray-700"
                >
                  <Home className="w-4 h-4" />
                  Go Home
                </button>
              </div>

              {/* Help Text */}
              <p className="text-xs text-gray-500 text-center mt-6">
                If this problem persists, please contact support
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
