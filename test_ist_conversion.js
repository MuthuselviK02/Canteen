// Test IST time conversion with sample backend data
const { formatISTTime, formatISTDate } = require('./frontend/src/utils/istTime.ts');

console.log('🕐 === IST TIME CONVERSION TEST ===');
console.log();

// Simulate backend UTC timestamp (what the backend sends)
const backendTimestamp = '2026-01-29T03:24:50.562210Z';
console.log('Backend UTC timestamp:', backendTimestamp);

// Test the conversion
const istTime = formatISTTime(backendTimestamp);
const istDate = formatISTDate(backendTimestamp);

console.log('Converted IST Time:', istTime);
console.log('Converted IST Date:', istDate);

// Expected: Should show 08:54 AM (UTC + 5:30 = IST)
console.log();
console.log('Expected: 08:54 AM');
console.log('Actual:  ', istTime);
console.log('Match:   ', istTime === '08:54 AM' ? '✅' : '❌');
