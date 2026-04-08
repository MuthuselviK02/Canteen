# Dynamic Order Time Management System

## Overview

This production-ready system provides comprehensive time tracking and dynamic wait time calculations for orders in the Smart Canteen application. It replaces static time estimates with real-time calculations based on order status, queue position, and actual timestamps.

## Features

### 🕐 **Current Timestamp Recording**
- Records exact order placement time
- Tracks status transition timestamps
- Maintains complete order lifecycle timeline

### ⚡ **Dynamic Wait Time Calculation**
- **Pending Orders**: Based on queue position and preparation time
- **Preparing Orders**: Real-time countdown based on start time
- **Ready Orders**: Minimal wait time (1 minute)
- **Completed Orders**: No wait time (0 minutes)

### 📊 **Status-Specific Time Tracking**
- `created_at`: When order was placed
- `started_preparation_at`: When preparation began
- `ready_at`: When order was ready for pickup
- `completed_at`: When order was completed

### 🔄 **Queue Management**
- Automatic queue position updates
- Dynamic wait time recalculation
- Fair queue ordering based on creation time

## Database Schema

### Orders Table
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    status VARCHAR DEFAULT 'Pending',
    queue_position INTEGER,
    predicted_wait_time INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_preparation_at DATETIME NULL,
    ready_at DATETIME NULL,
    completed_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## API Endpoints

### Core Order Endpoints
- `POST /api/orders/` - Create order with current timestamp
- `GET /api/orders/` - Get orders with dynamic wait times
- `GET /api/orders/{id}` - Get single order with time data

### Time Management Endpoints
- `PUT /api/orders/{id}/status?status={status}` - Update status with timestamp
- `GET /api/orders/{id}/time-summary` - Get comprehensive time summary
- `POST /api/orders/update-queue` - Update queue positions and times

## Time Calculation Logic

### Pending Orders
```
wait_time = base_preparation_time + (queue_position - 1) * queue_time_per_order
wait_time = max(0, wait_time - time_elapsed_since_creation)
```

### Preparing Orders
```
remaining_time = max(0, preparation_time - time_elapsed_since_start)
```

### Ready Orders
```
wait_time = 1  # Minimal time for pickup
```

### Completed Orders
```
wait_time = 0
```

## Production Configuration

### Environment Variables
```bash
ORDER_PREPARATION_TIME_MINUTES=10
ORDER_QUEUE_TIME_PER_ORDER=2
ORDER_READY_HOLD_TIME=5
ORDER_QUEUE_UPDATE_INTERVAL_SECONDS=60
```

### Queue Update Schedule
- **Recommended**: Every 60 seconds
- **High Traffic**: Every 30 seconds
- **Low Traffic**: Every 120 seconds

## Frontend Integration

### Time Display Components
```typescript
interface Order {
  id: string;
  userId: number;
  userName: string;
  items: OrderItem[];
  totalPrice: number;
  totalCalories: number;
  estimatedTime: number;  // Dynamic from backend
  status: OrderStatus;
  queuePosition: number;
  createdAt: Date;
  startedPreparationAt?: Date;
  readyAt?: Date;
  completedAt?: Date;
}
```

### Time Display Logic
```typescript
const getTimeDisplay = (order: Order) => {
  switch (order.status) {
    case 'pending':
      return {
        text: `${order.estimatedTime} min`,
        subtext: `Ordered at ${formatTime(order.createdAt)}`
      };
    case 'preparing':
      return {
        text: 'Preparing',
        subtext: `started ${formatTime(order.startedPreparationAt)}`
      };
    case 'ready':
      return {
        text: 'Ready for Pickup',
        subtext: `since ${formatTime(order.readyAt)}`
      };
    case 'completed':
      return {
        text: 'Completed',
        subtext: `at ${formatTime(order.completedAt)}`
      };
  }
};
```

## Production Deployment

### Database Migration
```bash
# Run the migration script
python migrations/add_order_timestamps.py
```

### Environment Setup
```bash
# Copy production environment
cp .env.production .env

# Update with production values
# Set proper database URL
# Configure security keys
# Set production CORS origins
```

### Monitoring
- **Queue Length**: Monitor pending order count
- **Average Wait Time**: Track customer satisfaction
- **Preparation Time**: Monitor kitchen efficiency
- **Completion Rate**: Track order fulfillment

## Performance Considerations

### Database Indexes
```sql
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_queue_position ON orders(queue_position);
```

### Caching Strategy
- Cache order status for 30 seconds
- Cache queue positions for 60 seconds
- Cache time calculations for 15 seconds

### Rate Limiting
- Queue updates: 10 requests per minute
- Status updates: 60 requests per minute
- Time summaries: 100 requests per minute

## Testing

### Unit Tests
```python
# Test time calculations
def test_dynamic_wait_time():
    order = Order(status='pending', queue_position=3, created_at=datetime.now() - timedelta(minutes=5))
    wait_time = OrderTimeService.calculate_dynamic_wait_time(order, db)
    assert wait_time > 0

# Test status updates
def test_status_update_with_timestamp():
    order = OrderTimeService.update_order_status_with_time(1, 'preparing', db)
    assert order.started_preparation_at is not None
```

### Integration Tests
```python
# Test complete order flow
def test_order_time_flow():
    # Create order
    # Update to preparing
    # Update to ready
    # Update to completed
    # Verify all timestamps
```

## Security Considerations

### Input Validation
- Validate status values
- Validate order ownership
- Sanitize time inputs

### Access Control
- Users can only update their own orders
- Admin required for queue updates
- Rate limiting on status updates

## Troubleshooting

### Common Issues

#### Wait Time Not Updating
1. Check queue update cron job
2. Verify database timestamps
3. Check time calculation logic

#### Status Timestamps Missing
1. Run database migration
2. Check update_order_status function
3. Verify timezone settings

#### Performance Issues
1. Add database indexes
2. Implement caching
3. Optimize queue updates

### Debug Commands
```bash
# Check database schema
sqlite3 canteen.db ".schema orders"

# Check order timestamps
sqlite3 canteen.db "SELECT id, status, created_at, started_preparation_at FROM orders LIMIT 5;"

# Test time calculation
python test_dynamic_time.py
```

## Future Enhancements

### Planned Features
- **Predictive Analytics**: ML-based wait time prediction
- **Real-time Notifications**: WebSocket updates
- **Kitchen Display**: Real-time order tracking
- **Analytics Dashboard**: Time performance metrics

### Scalability
- **Microservices**: Separate time service
- **Message Queue**: Async status updates
- **Load Balancing**: Multiple queue workers
- **Database Sharding**: Order data distribution

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review test results
3. Check application logs
4. Verify database schema
5. Test with provided test scripts

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-26  
**Production Ready**: ✅
