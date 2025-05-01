from flask import Flask, request, render_template, flash, send_file, redirect, url_for, session
import os
import random
import time
import string
import argparse
from collections import defaultdict
import logging
import json
import io

# Add at the start of your file, after the other imports
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open("/challenge/metadata.json", "r") as f:
    metadata_flag = json.load(f)
FLAG = metadata_flag['flag']

TREATMENT=True

app = Flask(__name__)
app.secret_key = os.urandom(24)

BASE_DELAY = 1
# Threshold to start rate limiting
ATTEMPT_THRESHOLD = random.choice([75, 80, 85, 90])
CONTROL_ATTEMPT_THRESHOLD = random.choice([10, 15, 20, 25])
ATTEMPTS_AFTER_SWITCH = 4
MAX_ATTEMPTS = (ATTEMPT_THRESHOLD + 30) if TREATMENT else (CONTROL_ATTEMPT_THRESHOLD + 30)
LINEAR_DELAY_INCREASE = 0.5

logger.info(f"TREATMENT: {TREATMENT}")
logger.info(f"ATTEMPT_THRESHOLD: {ATTEMPT_THRESHOLD}")
logger.info(f"CONTROL_ATTEMPT_THRESHOLD: {CONTROL_ATTEMPT_THRESHOLD}")
logger.info(f"MAX_ATTEMPTS: {MAX_ATTEMPTS}")

# Tracking dictionaries
attempt_counter = defaultdict(int)
current_list_tracking = {}
control_tracking = {}
last_credentials = defaultdict(dict)
# Modify session_data to track attempts per list
session_data = defaultdict(lambda: {
    'list_switches': 0,
    'total_attempts': 0,
    'list1_attempts': 0,
    'list2_attempts': 0,
    'unknown_attempts': 0
})

# Add this near the other global variables at the top
valid_credentials = {}  # Dictionary to store valid credentials per IP

def generate_dummy_credentials(count=200):
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
    #logger.info(f"Attempting to match: {attempt}")
    #logger.info(f"First few credentials in list1: {list(creds1)[:3]}")
    #logger.info(f"First few credentials in list2: {list(creds2)[:3]}")
    
    if attempt in creds1:
        #logger.info("Found in list1")
        return "list1"
    elif attempt in creds2:
        #logger.info("Found in list2")
        return "list2"
    #logger.info("Not found in either list")
    return "unknown"


def calculate_delay(ip_address, username, password):
    global attempt_counter, current_list_tracking, last_credentials, MAX_ATTEMPTS, session_data, control_tracking
    current_source = determine_credential_source(username, password)
    print("current_source: ", current_source)
    
    # Initialize tracking for new IP addresses
    if ip_address not in current_list_tracking:
        current_list_tracking[ip_address] = current_source
        control_tracking[ip_address] = current_source
        attempt_counter[ip_address] = 1
        # Initialize session_data for new IP if not already done
        if 'list_switches' not in session_data[ip_address]:
            session_data[ip_address] = {
                'list_switches': 0,
                'total_attempts': 1,
                'list1_attempts': 0,
                'list2_attempts': 0,
                'unknown_attempts': 0
            }
            # Increment the appropriate list counter
            if current_source == 'list1':
                session_data[ip_address]['list1_attempts'] = 1
            elif current_source == 'list2':
                session_data[ip_address]['list2_attempts'] = 1
            else:
                session_data[ip_address]['unknown_attempts'] = 1
        else:
            session_data[ip_address]['total_attempts'] += 1
            # Increment the appropriate list counter
            if current_source == 'list1':
                session_data[ip_address]['list1_attempts'] += 1
            elif current_source == 'list2':
                session_data[ip_address]['list2_attempts'] += 1
            else:
                session_data[ip_address]['unknown_attempts'] += 1
    else:
        attempt_counter[ip_address] += 1
        session_data[ip_address]['total_attempts'] += 1
        # Increment the appropriate list counter
        if current_source == 'list1':
            session_data[ip_address]['list1_attempts'] += 1
        elif current_source == 'list2':
            session_data[ip_address]['list2_attempts'] += 1
        else:
            session_data[ip_address]['unknown_attempts'] += 1
        
        # Check if user switched lists
        if current_list_tracking[ip_address] in ["list1", "list2"] and \
           current_source in ["list1", "list2"] and \
           current_list_tracking[ip_address] != current_source:
            # If participant switched list, increment the switch counter
            session_data[ip_address]['list_switches'] += 1
            # Reset tracking and lower threshold
            attempt_counter[ip_address] = 1
            MAX_ATTEMPTS = ATTEMPTS_AFTER_SWITCH

    # Update tracking before calculating delay
    current_list_tracking[ip_address] = current_source

    if not TREATMENT:
        last_credentials[ip_address] = {'username': username, 'password': password}
        # In the control group, we let 5 attempts pass before throttling so that participants see the effect of throttling
        # Whichever list they start with, that list will then be heavily throttled and the other list will not be throttled
        if attempt_counter[ip_address] < CONTROL_ATTEMPT_THRESHOLD:
            return BASE_DELAY
        else:
            if current_source == control_tracking[ip_address]:
                # change it here
                return BASE_DELAY + 4
            else:
                return BASE_DELAY 
        
    else:
        last_credentials[ip_address] = {'username': username, 'password': password}
        
        if attempt_counter[ip_address] > ATTEMPT_THRESHOLD:
            # change it here
            return BASE_DELAY + 4
        else:
            return BASE_DELAY


@app.route('/', methods=['GET', 'POST'])
def home():
    message = ''
    message_class = ''
    alert = ''

    # Get client IP
    ip_address = get_client_ip()

    qualtrics_data = {
        'condition': 1 if TREATMENT else 0,
        't': ATTEMPT_THRESHOLD if TREATMENT else CONTROL_ATTEMPT_THRESHOLD,
        'total_attempts': session_data[ip_address]['total_attempts'],
        'list_switches': session_data[ip_address]['list_switches'],
        'list1_attempts': session_data[ip_address]['list1_attempts'],
        'list2_attempts': session_data[ip_address]['list2_attempts'],
        'unknown_attempts': session_data[ip_address]['unknown_attempts'],
        'flag': f'{FLAG}'
    }

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            # First check if we already have valid credentials for this IP
            if ip_address in valid_credentials:
                # Only allow the known valid credentials
                if (valid_credentials[ip_address]['username'] == username and 
                    valid_credentials[ip_address]['password'] == password):
                    session['authenticated'] = True
                    return redirect(url_for('success')) # problematic
                else:
                    message = f"Login failed. Use the credentials you discovered. {valid_credentials[ip_address]}"
                    message_class = 'danger'
                    time.sleep(3)
                    return render_template('index.html',
                                        challenge_type='Brute Force',
                                        message=message,
                                        message_class=message_class,
                                        qualtrics_data=qualtrics_data,
                                        alert=alert)
            
            # Check if credentials are in any list before proceeding
            source = determine_credential_source(username, password)
            if source == "unknown":
                time.sleep(10)
                return redirect(url_for('locked_out'))
            
            # If credentials are valid, proceed with normal brute force logic
            delay = calculate_delay(ip_address, username, password)
            time.sleep(delay)
            
            # CORE BRUTEFORCE LOGIC BLOCK
            if attempt_counter[ip_address] > MAX_ATTEMPTS:
                # Store the successful credentials
                valid_credentials[ip_address] = {
                    'username': last_credentials[ip_address]['username'],
                    'password': last_credentials[ip_address]['password'],
                    'flag': f'{FLAG}'
                }
                # Instead of redirecting, show success message with credentials
                message = f"Login successful!"
                message_class = 'success'

            else:
                message = f"Login failed."
                message_class = 'danger'
                
            if attempt_counter[ip_address] > ATTEMPT_THRESHOLD and TREATMENT:
                alert = f"Suspicious activity detected. We are getting throttled."
            elif attempt_counter[ip_address] > CONTROL_ATTEMPT_THRESHOLD and not TREATMENT:
                alert = f"Suspicious activity detected. We are getting throttled."
        except Exception as e:
            message = f"An error occurred."
            message_class = 'danger'


    return render_template('index.html', 
                         challenge_type='Brute Force', 
                         message=message, 
                         message_class=message_class, 
                         alert=alert,
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

# Add new route for success page
@app.route('/success')
def success():
    ip_address = get_client_ip()
    
    # Check both valid credentials and session authentication
    if ip_address not in valid_credentials or not session.get('authenticated'):
        return redirect(url_for('home'))
    
    # Clear the authentication flag after successful access
    session.pop('authenticated', None)
    
    qualtrics_data = {
        'condition': 1 if TREATMENT else 0,
        't': ATTEMPT_THRESHOLD if TREATMENT else CONTROL_ATTEMPT_THRESHOLD,
        'total_attempts': session_data[ip_address]['total_attempts'],
        'list_switches': session_data[ip_address]['list_switches'],
        'list1_attempts': session_data[ip_address]['list1_attempts'],
        'list2_attempts': session_data[ip_address]['list2_attempts'],
        'unknown_attempts': session_data[ip_address]['unknown_attempts'],
        'flag': f'{FLAG}'
    }
    
    return render_template('success.html',
                         username=valid_credentials[ip_address]['username'],
                         password=valid_credentials[ip_address]['password'],
                         flag=FLAG,
                         qualtrics_data=qualtrics_data)

@app.route('/locked_out')
def locked_out():
    return render_template('locked_out.html', 
                         credentials1_url=url_for('credentials1'),
                         credentials2_url=url_for('credentials2'))

@app.route('/download_qualtrics')
def download_qualtrics():
    ip_address = get_client_ip()
    
    # Check both valid credentials and session for authorization
    if ip_address not in valid_credentials:
        return redirect(url_for('home'))
    
    qualtrics_data = {
        'condition': 1 if TREATMENT else 0,
        't': ATTEMPT_THRESHOLD if TREATMENT else CONTROL_ATTEMPT_THRESHOLD,
        'total_attempts': session_data[ip_address]['total_attempts'],
        'list_switches': session_data[ip_address]['list_switches'],
        'list1_attempts': session_data[ip_address]['list1_attempts'],
        'list2_attempts': session_data[ip_address]['list2_attempts'],
        'unknown_attempts': session_data[ip_address]['unknown_attempts'],
        'flag': f'{FLAG}'
    }
    
    # Convert the data to a JSON string
    json_data = json.dumps(qualtrics_data, indent=2)
    
    # Create a BytesIO object to hold the data
    mem = io.BytesIO()
    mem.write(json_data.encode('utf-8'))
    mem.seek(0)
    
    # Return the data as a downloadable file
    return send_file(
        mem,
        as_attachment=True,
        download_name='brute_force_challenge.txt',
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
