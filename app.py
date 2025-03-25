from flask import Flask, request, render_template, flash
import os
import random
import time
import string
from collections import defaultdict

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
TREATMENT_CONDITION = True
BASE_DELAY = 2
# Threshold to start rate limiting
ATTEMPT_THRESHOLD = random.choice([50, 60, 70, 80, 90])
ATTEMPTS_AFTER_SWITCH = 4
MAX_ATTEMPTS = 2*ATTEMPT_THRESHOLD
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

    if not TREATMENT_CONDITION:
        # No treatment
        # FIXME is this correct? Are we incrementing the list_switches counter correctly?
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
            return BASE_DELAY + (attempt_counter[ip_address] - ATTEMPT_THRESHOLD) * LINEAR_DELAY_INCREASE
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
            if attempt_counter[ip_address] >= MAX_ATTEMPTS:
                message = "Login successful! You've found the correct combination! Flag: CTF{br0t3_f0rc3_m4st3r}"
                message_class = 'success'
                attempt_counter[ip_address] = 0
            else:
                message = f"Login failed."
                message_class = 'danger'
                
            if attempt_counter[ip_address] > ATTEMPT_THRESHOLD and TREATMENT_CONDITION:
                alert = f"High number of attempts detected. Response delay: {delay:.1f}s"
        except Exception as e:
            message = f"An error occurred: {str(e)}"
            message_class = 'danger'

    # Prepare Qualtrics data if needed
    qualtrics_data = None
    if ip_address in session_data:
        qualtrics_data = {
            'condition': 1 if TREATMENT_CONDITION else 0,
            't': ATTEMPT_THRESHOLD,
            'total_attempts': session_data[ip_address]['total_attempts'],
            'list_switches': session_data[ip_address]['list_switches'],
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8087, debug=False)