import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Brain, 
  Activity, 
  TrendingUp, 
  Calendar, 
  CheckCircle, 
  AlertTriangle,
  Info
} from 'lucide-react';

interface ModelHealth {
  data_freshness: string;
  confidence_trend: Array<{
    date: string;
    confidence: number;
  }>;
  forecast_coverage: number;
  error_metrics: {
    mae: number;
    rmse: number;
    mape: number;
  };
  last_training_date: string;
  model_version: string;
}

interface ModelHealthTabProps {
  data: ModelHealth;
}

const ModelHealthTab: React.FC<ModelHealthTabProps> = ({ data }) => {
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
    if (confidence >= 0.5) return 'text-orange-600';
    return 'text-red-600';
  };

  const getCoverageColor = (coverage: number) => {
    if (coverage >= 90) return 'text-green-600';
    if (coverage >= 75) return 'text-yellow-600';
    if (coverage >= 60) return 'text-orange-600';
    return 'text-red-600';
  };

  const getErrorColor = (error: number, type: 'mae' | 'rmse' | 'mape') => {
    // Different thresholds for different error metrics
    const thresholds = {
      mae: { good: 5, warning: 10 },
      rmse: { good: 8, warning: 15 },
      mape: { good: 10, warning: 20 }
    };
    
    const threshold = thresholds[type];
    if (error <= threshold.good) return 'text-green-600';
    if (error <= threshold.warning) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Model Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Model Version</p>
                <p className="text-2xl font-bold">{data.model_version}</p>
                <p className="text-xs text-gray-500">Current version</p>
              </div>
              <Brain className="h-6 w-6 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Data Freshness</p>
                <p className="text-lg font-bold">{data.data_freshness}</p>
                <p className="text-xs text-gray-500">Last data update</p>
              </div>
              <Calendar className="h-6 w-6 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Last Training</p>
                <p className="text-lg font-bold">{data.last_training_date}</p>
                <p className="text-xs text-gray-500">Model retraining</p>
              </div>
              <Activity className="h-6 w-6 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Confidence Trends */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Confidence Trends
          </CardTitle>
          <p className="text-sm text-gray-600">
            Model confidence over time - higher values indicate better predictions
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {data.confidence_trend.map((point, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <span className="font-medium">{point.date}</span>
                    <Badge className={getConfidenceColor(point.confidence)}>
                      {point.confidence >= 0.9 ? 'Excellent' : 
                       point.confidence >= 0.7 ? 'Good' :
                       point.confidence >= 0.5 ? 'Fair' : 'Poor'}
                    </Badge>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-24">
                    <Progress value={point.confidence * 100} className="h-2" />
                  </div>
                  <span className={`font-semibold ${getConfidenceColor(point.confidence)}`}>
                    {(point.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Forecast Coverage */}
      <Card>
        <CardHeader>
          <CardTitle>Forecast Coverage</CardTitle>
          <p className="text-sm text-gray-600">
            Percentage of items successfully forecasted vs total catalog
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-lg font-medium">Coverage Rate</span>
              <span className={`text-2xl font-bold ${getCoverageColor(data.forecast_coverage)}`}>
                {data.forecast_coverage.toFixed(1)}%
              </span>
            </div>
            <Progress value={data.forecast_coverage} className="h-4" />
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Info className="h-4 w-4" />
              <span>
                {data.forecast_coverage >= 90 ? 'Excellent coverage - most items are being predicted accurately.' :
                 data.forecast_coverage >= 75 ? 'Good coverage - majority of items have reliable predictions.' :
                 data.forecast_coverage >= 60 ? 'Fair coverage - some items may need manual attention.' :
                 'Poor coverage - consider retraining with more data.'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Error Metrics (Historical Performance)</CardTitle>
          <p className="text-sm text-gray-600">
            Model accuracy measured against historical data - lower values are better
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-medium">Mean Absolute Error (MAE)</span>
                <span className={`font-bold ${getErrorColor(data.error_metrics.mae, 'mae')}`}>
                  {data.error_metrics.mae.toFixed(2)}
                </span>
              </div>
              <Progress value={Math.min((data.error_metrics.mae / 10) * 100, 100)} className="h-2" />
              <p className="text-xs text-gray-600">
                Average absolute difference between predicted and actual values
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-medium">Root Mean Square Error (RMSE)</span>
                <span className={`font-bold ${getErrorColor(data.error_metrics.rmse, 'rmse')}`}>
                  {data.error_metrics.rmse.toFixed(2)}
                </span>
              </div>
              <Progress value={Math.min((data.error_metrics.rmse / 15) * 100, 100)} className="h-2" />
              <p className="text-xs text-gray-600">
                Square root of average squared differences - penalizes larger errors
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-medium">Mean Absolute Percentage Error (MAPE)</span>
                <span className={`font-bold ${getErrorColor(data.error_metrics.mape, 'mape')}`}>
                  {data.error_metrics.mape.toFixed(1)}%
                </span>
              </div>
              <Progress value={Math.min((data.error_metrics.mape / 20) * 100, 100)} className="h-2" />
              <p className="text-xs text-gray-600">
                Average percentage error - relative accuracy measure
              </p>
            </div>
          </div>

          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start gap-2">
              <Info className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <p className="font-medium text-blue-800">Understanding Error Metrics</p>
                <p className="text-sm text-blue-700 mt-1">
                  These metrics are calculated using historical data where predictions were made 
                  and actual outcomes are known. They help assess model reliability and identify 
                  areas for improvement.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Model Health Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Overall Model Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium text-green-600">Strengths</h4>
              <div className="space-y-2">
                {data.forecast_coverage >= 75 && (
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Good forecast coverage ({data.forecast_coverage.toFixed(1)}%)</span>
                  </div>
                )}
                {data.confidence_trend[data.confidence_trend.length - 1]?.confidence >= 0.7 && (
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>High current confidence ({(data.confidence_trend[data.confidence_trend.length - 1]?.confidence * 100).toFixed(1)}%)</span>
                  </div>
                )}
                {data.error_metrics.mape <= 15 && (
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Acceptable error rates (MAPE: {data.error_metrics.mape.toFixed(1)}%)</span>
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="font-medium text-orange-600">Areas for Improvement</h4>
              <div className="space-y-2">
                {data.forecast_coverage < 75 && (
                  <div className="flex items-center gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-orange-600" />
                    <span>Low forecast coverage - consider retraining</span>
                  </div>
                )}
                {data.error_metrics.mape > 20 && (
                  <div className="flex items-center gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-orange-600" />
                    <span>High error rates - model needs improvement</span>
                  </div>
                )}
                {data.confidence_trend.length > 1 && 
                 data.confidence_trend[data.confidence_trend.length - 1]?.confidence < 
                 data.confidence_trend[data.confidence_trend.length - 2]?.confidence && (
                  <div className="flex items-center gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-orange-600" />
                    <span>Declining confidence trend detected</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ModelHealthTab;
