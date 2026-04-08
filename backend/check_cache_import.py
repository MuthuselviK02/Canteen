# Check the actual function signature that's being imported
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

try:
    from app.routers.predictive_analytics import set_cached_data as pred_cache
    import inspect
    sig = inspect.signature(pred_cache)
    print(f'Predictive analytics set_cached_data signature: {sig}')
except Exception as e:
    print(f'Error importing from predictive_analytics: {e}')

# Check if there are multiple definitions
import app.routers.analytics as analytics_module
import app.routers.predictive_analytics as pred_module

print(f'Analytics module set_cached_data: {analytics_module.set_cached_data}')
print(f'Predictive module set_cached_data: {getattr(pred_module, "set_cached_data", "NOT FOUND")}')
