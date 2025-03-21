# # Brute Force and SQL Injection Challenge

This application simulates a login system vulnerable to brute force attacks.

## Prerequisites

You will need to have Docker and Docker Compose installed in your computer to run this. This is separate from Python requirements. To install Docker, follow the instructions on Docker's website for your platform.

## Setup and Running the Application

1. Clone the repository: 

```git clone https://github.com/DDM-Lab/BruteForce_SQLi_Challenge```

- Then cd BruteForce_SQLi_Challenge
 
2. Build the Docker image:
```docker-compose build```


3. Start the application:
```docker-compose up```

4. Access the application:
Open a web browser and navigate to `http://localhost:8087`

## Solution

The problem is solved based on the number of attempts, not on actual credentials. Regardless of the list that the participant starts with, they will always be able to solve the problem based on `MAX_ATTEMPTS`. In the control treatment (if `TREATMENT_CONDITION = false`), the rate limit stays constant and switching lists has no impact. 

In the treatment condition, they will be rate limited linearly after `ATTEMPT_THRESHOLD`. After a while, they will be able to solve the problem. If they switch lists, the problem will be solved after `ATTEMPTS_AFTER_SWITCH`, this will happen very quickly to prevent participants from switching back and forth.

To solve the problem, then simply run ```brute_force_script.py``` and choose a list. You may need to install requirements.txt in your venv to run this.


