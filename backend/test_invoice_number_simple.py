import sqlite3
import re

# Check what the next invoice number should be
conn = sqlite3.connect('canteen.db')
cursor = conn.cursor()

# Get the last invoice number
cursor.execute('SELECT invoice_number FROM invoices WHERE invoice_number LIKE "INV%" ORDER BY invoice_number DESC LIMIT 1')
result = cursor.fetchone()

if result:
    last_invoice = result[0]
    print(f'Last invoice: {last_invoice}')
    
    # Extract numeric part
    match = re.search(r'(\d+)', last_invoice)
    if match:
        last_num = int(match.group(1))
        next_num = last_num + 1
        next_invoice = f'INV{str(next_num).zfill(6)}'
        print(f'Next invoice should be: {next_invoice}')
    else:
        print('Could not extract numeric part')
else:
    print('No invoices found')

conn.close()
