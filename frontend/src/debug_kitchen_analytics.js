// Add this to the Kitchen.tsx file for debugging the Show Analytics button

// Add this console log to the button click handler:
const handleToggleAnalytics = () => {
  const newState = !showAnalytics;
  console.log('🔍 Analytics button clicked:', {
    newState,
    currentState: showAnalytics,
    timestamp: new Date().toISOString()
  });
  setShowAnalytics(newState);
};

// Replace the existing button onClick with:
onClick={handleToggleAnalytics}

// Add this debug component inside the Kitchen component (before return):
const DebugInfo = () => (
  <div className="fixed bottom-4 right-4 bg-black text-white p-2 rounded text-xs z-50">
    <div>showAnalytics: {showAnalytics.toString()}</div>
    <div>orders: {orders.length}</div>
    <div>loading: {loading.toString()}</div>
    <div>currentTime: {currentTime.toLocaleTimeString()}</div>
  </div>
);

// Add this to the return statement, just before the closing </div>:
{process.env.NODE_ENV === 'development' && <DebugInfo />}
