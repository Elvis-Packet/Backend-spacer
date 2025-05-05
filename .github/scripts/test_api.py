import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000/api'

def test_spaces():
    print("\nTesting spaces endpoints...")
    
    # Get all spaces
    response = requests.get(f'{BASE_URL}/spaces')
    print(f"GET /spaces: {response.status_code}")
    if response.status_code == 200:
        print(f"Found {len(response.json())} spaces")
        print(json.dumps(response.json()[0], indent=2))

    # Get single space
    response = requests.get(f'{BASE_URL}/spaces/1')
    print(f"\nGET /spaces/1: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))

def test_users():
    print("\nTesting users endpoints...")
    
    # Get all users
    response = requests.get(f'{BASE_URL}/users')
    print(f"GET /users: {response.status_code}")
    if response.status_code == 200:
        print(f"Found {len(response.json())} users")
        print(json.dumps(response.json()[0], indent=2))

    # Get single user
    response = requests.get(f'{BASE_URL}/users/1')
    print(f"\nGET /users/1: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))

def test_bookings():
    print("\nTesting bookings endpoints...")
    
    # Get all bookings
    response = requests.get(f'{BASE_URL}/bookings')
    print(f"GET /bookings: {response.status_code}")
    if response.status_code == 200:
        print(f"Found {len(response.json())} bookings")
        print(json.dumps(response.json()[0], indent=2))

    # Get single booking
    response = requests.get(f'{BASE_URL}/bookings/1')
    print(f"\nGET /bookings/1: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))

    # Create new booking
    new_booking = {
        'space_id': 1,
        'client_id': 2,
        'start_time': (datetime.now() + timedelta(days=3)).isoformat(),
        'end_time': (datetime.now() + timedelta(days=3, hours=4)).isoformat(),
        'status': 'PENDING',
        'total_amount': 180
    }
    response = requests.post(f'{BASE_URL}/bookings', json=new_booking)
    print(f"\nPOST /bookings: {response.status_code}")
    if response.status_code == 201:
        print(json.dumps(response.json(), indent=2))

if __name__ == '__main__':
    print("Testing API endpoints...")
    test_spaces()
    test_users()
    test_bookings() 