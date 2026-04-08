import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Eye, CheckCircle, AlertCircle, AlertTriangle, XCircle, ArrowUp, ArrowDown, Minus } from 'lucide-react';

type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

interface FoodAnalytics {
  menu_item_id: number;
  name: string;
  category: string;
  predicted_quantity: number;
  confidence: number;
  risk_level: RiskLevel;
  trend: 'up' | 'down' | 'stable';
  historical_avg: number;
  change_percentage: number;
  preparation_recommendations: string[];
  hourly_forecast: Array<{
    hour: string;
    predicted_quantity: number;
    confidence: number;
  }>;
  contributing_factors: string[];
}

interface FoodAnalyticsTabProps {
  data: FoodAnalytics[];
  selectedItem: FoodAnalytics | null;
  onSelectItem: (item: FoodAnalytics | null) => void;
  showDetail: boolean;
  onShowDetail: (show: boolean) => void;
  isReadOnly: boolean;
}

const FoodAnalyticsTab: React.FC<FoodAnalyticsTabProps> = ({
  data,
  selectedItem,
  onSelectItem,
  showDetail,
  onShowDetail,
  isReadOnly
}) => {
  const getRiskColor = (riskLevel: RiskLevel) => {
    switch (riskLevel) {
      case 'low': return 'text-green-600 bg-green-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'critical': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getRiskIcon = (riskLevel: RiskLevel) => {
    switch (riskLevel) {
      case 'low': return <CheckCircle className="h-4 w-4" />;
      case 'medium': return <AlertCircle className="h-4 w-4" />;
      case 'high': return <AlertTriangle className="h-4 w-4" />;
      case 'critical': return <XCircle className="h-4 w-4" />;
      default: return <AlertCircle className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Food Preparation Analytics</CardTitle>
          <p className="text-sm text-gray-600">
            Item-level predictions and preparation recommendations
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {data.map((item, index) => (
              <div 
                key={item.menu_item_id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                onClick={() => {
                  onSelectItem(item);
                  onShowDetail(true);
                }}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h4 className="font-semibold">{item.name}</h4>
                    <Badge variant="outline">{item.category}</Badge>
                    <Badge className={getRiskColor(item.risk_level)}>
                      {getRiskIcon(item.risk_level)}
                      <span className="ml-1">{item.risk_level.toUpperCase()}</span>
                    </Badge>
                  </div>
                  <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Predicted:</span>
                      <span className="ml-2 font-semibold">{item.predicted_quantity}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Confidence:</span>
                      <span className="ml-2 font-semibold">{(item.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Trend:</span>
                      <span className={`ml-2 font-semibold flex items-center gap-1`}>
                        {item.trend === 'up' && <ArrowUp className="h-3 w-3 text-green-600" />}
                        {item.trend === 'down' && <ArrowDown className="h-3 w-3 text-red-600" />}
                        {item.trend === 'stable' && <Minus className="h-3 w-3 text-gray-600" />}
                        {item.change_percentage.toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Historical Avg:</span>
                      <span className="ml-2 font-semibold">{item.historical_avg}</span>
                    </div>
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  <Eye className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Food Detail Modal */}
      {showDetail && selectedItem && (
        <FoodDetailModal 
          item={selectedItem} 
          onClose={() => onShowDetail(false)}
          isReadOnly={isReadOnly}
        />
      )}
    </div>
  );
};

// Food Detail Modal Component
const FoodDetailModal: React.FC<{
  item: FoodAnalytics;
  onClose: () => void;
  isReadOnly: boolean;
}> = ({ item, onClose, isReadOnly }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">{item.name}</h2>
          <Button variant="ghost" onClick={onClose}>
            <XCircle className="h-5 w-5" />
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Historical vs Predicted */}
          <Card>
            <CardHeader>
              <CardTitle>Historical vs Predicted</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Historical Average:</span>
                  <span className="font-semibold">{item.historical_avg}</span>
                </div>
                <div className="flex justify-between">
                  <span>Predicted Quantity:</span>
                  <span className="font-semibold">{item.predicted_quantity}</span>
                </div>
                <div className="flex justify-between">
                  <span>Change:</span>
                  <span className={`font-semibold ${item.change_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {item.change_percentage >= 0 ? '+' : ''}{item.change_percentage.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Confidence:</span>
                  <span className="font-semibold">{(item.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Hourly Forecast */}
          <Card>
            <CardHeader>
              <CardTitle>Hourly Forecast</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {item.hourly_forecast.map((hour, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-sm">{hour.hour}</span>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{hour.predicted_quantity}</span>
                      <div className="w-16">
                        <Progress value={hour.confidence * 100} className="h-2" />
                      </div>
                      <span className="text-xs text-gray-500">{(hour.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Contributing Factors */}
          <Card>
            <CardHeader>
              <CardTitle>Contributing Factors</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {item.contributing_factors.map((factor, index) => (
                  <Badge key={index} variant="outline" className="mr-2 mb-2">
                    {factor}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Preparation Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle>Preparation Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {item.preparation_recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{recommendation}</span>
                  </div>
                ))}
              </div>
              {!isReadOnly && (
                <div className="mt-4 pt-4 border-t">
                  <Button className="w-full">
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Confirm Preparation Plan
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default FoodAnalyticsTab;
