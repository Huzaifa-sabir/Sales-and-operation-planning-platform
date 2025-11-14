"""
Test the products API endpoint directly
"""
import requests
import json
import sys

def test_products_api():
    base_url = "http://localhost:8000/api/v1"
    
    # Test 1: Get products for Cheney Brothers
    print("\n" + "="*60)
    print("TEST 1: Get products for CHENEY-BROTHERS")
    print("="*60)
    
    try:
        response = requests.get(
            f"{base_url}/products",
            params={
                'customerId': 'CHENEY-BROTHERS',
                'page': 1,
                'limit': 1000,
                'isActive': 'true'
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"Total products returned: {len(products)}")
            print(f"Total in database: {data.get('total', 0)}")
            print(f"Has next page: {data.get('hasNext', False)}")
            
            print("\nProducts returned:")
            for i, p in enumerate(products[:15], 1):
                print(f"  {i}. {p.get('itemCode')}: {p.get('itemDescription', 'N/A')[:60]}")
            
            if len(products) > 15:
                print(f"  ... and {len(products) - 15} more")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to backend server at http://localhost:8000")
        print("Make sure the backend is running!")
        return
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Get all products (no customer filter)
    print("\n" + "="*60)
    print("TEST 2: Get all products (no customer filter)")
    print("="*60)
    
    try:
        response = requests.get(
            f"{base_url}/products",
            params={
                'page': 1,
                'limit': 10,
                'isActive': 'true'
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"Total products returned: {len(products)}")
            print("\nFirst 10 products:")
            for i, p in enumerate(products[:10], 1):
                print(f"  {i}. {p.get('itemCode')}: {p.get('itemDescription', 'N/A')[:60]}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    test_products_api()

