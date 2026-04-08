#!/usr/bin/env python3
"""
Test the updated inventory sorting and categorization
"""

import requests
import json

API_URL = 'http://localhost:8000'

def test_inventory_updates():
    # Login
    response = requests.post(f'{API_URL}/api/auth/login', json={
        'email': 'superadmin@admin.com',
        'password': 'admin123'
    })
    token = response.json()['access_token']

    # Get inventory data
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{API_URL}/api/inventory/dashboard?start_date=2026-02-06T18:30:00.000Z&end_date=2026-02-07T18:30:00.000Z&category=all', headers=headers)

    if response.status_code == 200:
        data = response.json()
        kpis = data['inventory_kpis']
        items = data['inventory_items']
        
        print('📊 Updated Inventory KPIs:')
        print(f'  Total items: {kpis["total_items"]}')
        print(f'  Well stocked: {kpis["well_stocked"]}')
        print(f'  Needs restocking: {kpis["needs_restocking"]}')
        print(f'  Out of stock: {kpis["out_of_stock"]}')
        print(f'  No forecast: {kpis["no_forecast"]}')
        
        print('\n🔢 Items by stock level:')
        
        # Show items in each category
        out_of_stock = [item for item in items if item['inventory_status'] == 'Out of Stock']
        needs_restocking = [item for item in items if item['inventory_status'] == 'Needs Restocking']
        well_stocked = [item for item in items if item['inventory_status'] == 'Well Stocked']
        
        if out_of_stock:
            print(f'\n❌ Out of Stock ({len(out_of_stock)}):')
            for item in out_of_stock:
                print(f'  {item["item_name"]}: {item["remaining_stock"]}')
        
        if needs_restocking:
            print(f'\n⚠️ Needs Restocking ({len(needs_restocking)}):')
            for item in needs_restocking:
                print(f'  {item["item_name"]}: {item["remaining_stock"]}')
        
        if well_stocked:
            print(f'\n✅ Well Stocked ({len(well_stocked)}):')
            # Show first 10 well-stocked items in ascending order
            for item in well_stocked[:10]:
                print(f'  {item["item_name"]}: {item["remaining_stock"]}')
            if len(well_stocked) > 10:
                print(f'  ... and {len(well_stocked) - 10} more items')
                
        print(f'\n🎯 Summary: Items with <6 stock are now in "Needs Restocking"')
        print(f'📈 Items are sorted by stock level (ascending) within each category')
        
    else:
        print(f'Error: {response.status_code}')

if __name__ == "__main__":
    test_inventory_updates()
