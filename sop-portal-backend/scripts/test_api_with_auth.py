"""
Test the products API endpoint with authentication
"""
import requests
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def test_products_api():
    base_url = "http://localhost:8000/api/v1"
    
    # Step 1: Login to get token
    print("\n" + "="*60)
    print("STEP 1: Login")
    print("="*60)
    
    login_data = {
        "username": "lpolo@garlandfood.net",
        "password": "Admin123!"
    }
    
    try:
        login_response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
        
        token = login_response.json().get('access_token')
        if not token:
            print("No token received from login")
            return
        
        print("✓ Login successful")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to backend server at http://localhost:8000")
        print("Make sure the backend is running!")
        return
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Get products for Cheney Brothers
    print("\n" + "="*60)
    print("STEP 2: Get products for CHENEY-BROTHERS")
    print("="*60)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(
            f"{base_url}/products",
            params={
                'customerId': 'CHENEY-BROTHERS',
                'page': 1,
                'limit': 1000,
                'isActive': 'true'
            },
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"✓ Total products returned: {len(products)}")
            print(f"✓ Total in database: {data.get('total', 0)}")
            print(f"✓ Has next page: {data.get('hasNext', False)}")
            
            print("\nProducts returned:")
            for i, p in enumerate(products, 1):
                print(f"  {i}. {p.get('itemCode')}: {p.get('itemDescription', 'N/A')[:60]}")
            
            # Verify it's the correct 10 products
            expected_codes = ['110010', '110023', '130037', '150006', '190001', '210011', '220004', '330030', '810009', '810010']
            actual_codes = [p.get('itemCode') for p in products]
            
            print(f"\n✓ Expected product codes: {expected_codes}")
            print(f"✓ Actual product codes: {sorted(actual_codes)}")
            
            if set(actual_codes) == set(expected_codes):
                print("\n✅ SUCCESS: All 10 correct products are returned!")
            else:
                missing = set(expected_codes) - set(actual_codes)
                extra = set(actual_codes) - set(expected_codes)
                if missing:
                    print(f"\n⚠️  Missing products: {missing}")
                if extra:
                    print(f"⚠️  Extra products: {extra}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_products_api()

