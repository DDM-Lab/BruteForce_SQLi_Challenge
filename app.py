from flask import Flask, request, render_template, flash, send_file
import os
import random
import time
import string
import argparse
from collections import defaultdict


treatment_default = True

# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the Flask application with treatment settings")
    parser.add_argument(
        "--treatment",
        type=str,
        choices=["true", "false", "True", "False"],
        default=os.environ.get("TREATMENT", treatment_default),
        help="Set the treatment condition (True/False, default: True, can also be set with TREATMENT env variable)"
    )
    return parser.parse_args()

app = Flask(__name__)
app.secret_key = os.urandom(24)

args = parse_arguments()
# Configuration
if args.treatment is not None:
    TREATMENT = str(args.treatment).lower() == "true"
else:
    TREATMENT = treatment_default
BASE_DELAY = 0.5
# Threshold to start rate limiting
ATTEMPT_THRESHOLD = random.choice([30, 40, 50, 60, 70])
ATTEMPTS_AFTER_SWITCH = 4
MAX_ATTEMPTS = 100
LINEAR_DELAY_INCREASE = 0.2

# Tracking dictionaries
attempt_counter = defaultdict(int)
current_list_tracking = {}
last_credentials = defaultdict(dict)
# Add session_data dictionary to track list switches and other metrics
session_data = defaultdict(lambda: {'list_switches': 0, 'total_attempts': 0})

def generate_dummy_credentials(count=100):
    credentials = []
    for _ in range(count):
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        credentials.append(f"{username}:{password}")
    return credentials

# Generate stable credentials at startup
CREDENTIALS_LIST1 = generate_dummy_credentials()
CREDENTIALS_LIST2 = generate_dummy_credentials()

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

def determine_credential_source(username, password):
    creds1 = set(CREDENTIALS_LIST1)
    creds2 = set(CREDENTIALS_LIST2)
    
    attempt = f"{username}:{password}"
    if attempt in creds1:
        return "list1"
    elif attempt in creds2:
        return "list2"
    return "unknown"


def calculate_delay(ip_address, username, password):
    global attempt_counter, current_list_tracking, last_credentials, MAX_ATTEMPTS, session_data
    current_source = determine_credential_source(username, password)
    
    # Initialize tracking for new IP addresses
    if ip_address not in current_list_tracking:
        current_list_tracking[ip_address] = current_source
        attempt_counter[ip_address] = 1
        # Initialize session_data for new IP if not already done
        if 'list_switches' not in session_data[ip_address]:
            session_data[ip_address] = {'list_switches': 0, 'total_attempts': 1}
        else:
            session_data[ip_address]['total_attempts'] += 1
    else:
        attempt_counter[ip_address] += 1
        session_data[ip_address]['total_attempts'] += 1

    if not TREATMENT:
        last_credentials[ip_address] = {'username': username, 'password': password}
        return BASE_DELAY
        
    else:
        # Check if user switched lists
        if current_list_tracking[ip_address] != current_source and current_source != "unknown":
            # If participant switched list, increment the switch counter
            session_data[ip_address]['list_switches'] += 1
            # Reset tracking
            current_list_tracking[ip_address] = current_source
            attempt_counter[ip_address] = 0
            # If participant switched list, lower threshold
            MAX_ATTEMPTS = ATTEMPTS_AFTER_SWITCH
            # If participant switched list, reset delay
        
        last_credentials[ip_address] = {'username': username, 'password': password}
        
        if attempt_counter[ip_address] > ATTEMPT_THRESHOLD:
            # If we are above threshold, increase delay
            # This is a simple linear increase where the delay is +0.2 seconds per attempt
            return BASE_DELAY + (attempt_counter[ip_address] - ATTEMPT_THRESHOLD) ** LINEAR_DELAY_INCREASE
        else:
            return BASE_DELAY


@app.route('/', methods=['GET', 'POST'])
def home():
    message = ''
    message_class = ''
    alert = ''
    
    # Create a default worldbuilding context
    worldbuilding = {'first_visit': True}
    
    # Get client IP
    ip_address = get_client_ip()
    
    # If this is not the first visit, set first_visit to False
    if ip_address in session_data:
        worldbuilding['first_visit'] = False

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Mark as not first visit
        worldbuilding['first_visit'] = False
        
        try:
            delay = calculate_delay(ip_address, username, password)
            time.sleep(delay)
            
            # Simplified authentication
            if attempt_counter[ip_address] > MAX_ATTEMPTS:
                # Retrieve the last credentials submitted by the user
                creds = last_credentials.get(ip_address, {'username': 'unknown', 'password': 'unknown'})
                # Construct a message that includes the username, password, and the flag
                message = (f"Login successful! Flag: picoCTF{{br0t3__f0rc3__m4st3r}}")
                message_class = 'success'
                attempt_counter[ip_address] = 0

            else:
                message = f"Login failed."
                message_class = 'danger'
                
            if attempt_counter[ip_address] > ATTEMPT_THRESHOLD and TREATMENT:
                alert = f"High number of attempts detected. Throttling detected in this list."
        except Exception as e:
            message = f"An error occurred: {str(e)}"
            message_class = 'danger'

    qualtrics_data = {
        'condition': 1 if TREATMENT else 0,
        't': ATTEMPT_THRESHOLD,
        'total_attempts': session_data[ip_address]['total_attempts']-session_data[ip_address]['list_switches']-1,
        'list_switches': session_data[ip_address]['list_switches'],
        'flag': 'picoCTF{br0t3__f0rc3__m4st3r}'
    }

    return render_template('index.html', 
                         challenge_type='Brute Force', 
                         message=message, 
                         message_class=message_class, 
                         alert=alert,
                         worldbuilding=worldbuilding,
                         qualtrics_data=qualtrics_data)


@app.route('/credentials1.txt')
def credentials1():
    return '\n'.join(CREDENTIALS_LIST1), 200, {'Content-Type': 'text/plain'}

@app.route('/credentials2.txt')
def credentials2():
    return '\n'.join(CREDENTIALS_LIST2), 200, {'Content-Type': 'text/plain'}

@app.route('/brute_force_script.py')
def download_script():
    filepath = os.path.abspath('brute_force_script.py')
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8087, debug=False)