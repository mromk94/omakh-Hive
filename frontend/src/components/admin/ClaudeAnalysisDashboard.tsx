/**
 * Claude System Analysis Dashboard
 * Displays Claude's architectural analysis and recommendations
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertCircle, CheckCircle, TrendingUp, Zap, Shield, Code } from 'lucide-react';

interface Recommendation {
  title: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  impact: string;
  status: 'pending' | 'in_progress' | 'completed';
  estimatedImprovement: string;
  files: string[];
}

interface AnalysisData {
  timestamp: string;
  overallScore: number;
  dataFlow: {
    score: number;
    bottlenecks: string[];
    strengths: string[];
  };
  security: {
    coverage: number;
    integrationPoints: number;
    recommendations: string[];
  };
  performance: {
    avgLatency: number;
    securityGateLatency: number;
    llmLatency: number;
  };
  recommendations: Recommendation[];
}

const ClaudeAnalysisDashboard: React.FC = () => {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalysisData();
  }, []);

  const fetchAnalysisData = async () => {
    try {
      const response = await fetch('/api/v1/admin/claude/analysis');
      const data = await response.json();
      setAnalysisData(data);
    } catch (error) {
      console.error('Failed to fetch analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const requestImplementation = async (recommendationTitle: string) => {
    try {
      const response = await fetch('/api/v1/admin/claude/implement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ recommendation: recommendationTitle })
      });
      const result = await response.json();
      alert(`Implementation request sent: ${result.message}`);
    } catch (error) {
      console.error('Failed to request implementation:', error);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'destructive';
      case 'high': return 'warning';
      case 'medium': return 'default';
      case 'low': return 'secondary';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'in_progress': return <Zap className="h-4 w-4 text-yellow-500 animate-pulse" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card className="w-96">
          <CardHeader>
            <CardTitle>No Analysis Data</CardTitle>
            <CardDescription>Run a system analysis to see results here.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={fetchAnalysisData}>Retry</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Claude System Analysis</h1>
          <p className="text-gray-500">Last updated: {new Date(analysisData.timestamp).toLocaleString()}</p>
        </div>
        <Button onClick={fetchAnalysisData}>Refresh Analysis</Button>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Overall Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{analysisData.overallScore}/10</div>
            <p className="text-xs text-gray-500 mt-1">System efficiency</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Security Coverage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{analysisData.security.coverage}%</div>
            <p className="text-xs text-gray-500 mt-1">{analysisData.security.integrationPoints} integration points</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Avg Latency
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{analysisData.performance.avgLatency}ms</div>
            <p className="text-xs text-gray-500 mt-1">Security: {analysisData.performance.securityGateLatency}ms</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{analysisData.recommendations.length}</div>
            <p className="text-xs text-gray-500 mt-1">
              {analysisData.recommendations.filter(r => r.priority === 'critical' || r.priority === 'high').length} high priority
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Data Flow Analysis</CardTitle>
              <CardDescription>Score: {analysisData.dataFlow.score}/10</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  Strengths
                </h4>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  {analysisData.dataFlow.strengths.map((strength, idx) => (
                    <li key={idx}>{strength}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-2 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-yellow-500" />
                  Bottlenecks
                </h4>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  {analysisData.dataFlow.bottlenecks.map((bottleneck, idx) => (
                    <li key={idx} className="text-yellow-600">{bottleneck}</li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Recommendations Tab */}
        <TabsContent value="recommendations" className="space-y-4">
          {analysisData.recommendations.map((rec, idx) => (
            <Card key={idx}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="space-y-1 flex-1">
                    <CardTitle className="flex items-center gap-2">
                      {getStatusIcon(rec.status)}
                      {rec.title}
                    </CardTitle>
                    <CardDescription>{rec.impact}</CardDescription>
                  </div>
                  <Badge variant={getPriorityColor(rec.priority) as any}>
                    {rec.priority.toUpperCase()}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-semibold">Expected Improvement:</span>
                    <p className="text-green-600">{rec.estimatedImprovement}</p>
                  </div>
                  <div>
                    <span className="font-semibold">Status:</span>
                    <p className="capitalize">{rec.status.replace('_', ' ')}</p>
                  </div>
                </div>
                <div>
                  <span className="font-semibold text-sm">Files to modify:</span>
                  <div className="mt-2 space-y-1">
                    {rec.files.map((file, i) => (
                      <div key={i} className="text-xs bg-gray-100 p-2 rounded font-mono flex items-center gap-2">
                        <Code className="h-3 w-3" />
                        {file}
                      </div>
                    ))}
                  </div>
                </div>
                {rec.status === 'pending' && (
                  <Button
                    onClick={() => requestImplementation(rec.title)}
                    className="w-full"
                  >
                    Request Claude Implementation
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Performance Metrics</CardTitle>
              <CardDescription>Current system latency breakdown</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Security Gate Latency</span>
                  <span className="font-semibold">{analysisData.performance.securityGateLatency}ms</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${(analysisData.performance.securityGateLatency / analysisData.performance.avgLatency) * 100}%` }}
                  ></div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">LLM Processing</span>
                  <span className="font-semibold">{analysisData.performance.llmLatency}ms</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${(analysisData.performance.llmLatency / analysisData.performance.avgLatency) * 100}%` }}
                  ></div>
                </div>
              </div>

              <div className="pt-4 border-t">
                <div className="flex justify-between">
                  <span className="font-semibold">Total Average</span>
                  <span className="font-bold text-lg">{analysisData.performance.avgLatency}ms</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Security Assessment</CardTitle>
              <CardDescription>Coverage: {analysisData.security.coverage}%</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Integration Points</h4>
                  <p className="text-2xl font-bold">{analysisData.security.integrationPoints}</p>
                  <p className="text-sm text-gray-500">All critical endpoints secured</p>
                </div>

                {analysisData.security.recommendations.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Security Recommendations</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      {analysisData.security.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ClaudeAnalysisDashboard;
