# # Brute Force and SQL Injection Challenge

This application simulates a login system vulnerable to brute force attacks and SQL injection. 

## Prerequisites

- Docker
- Docker Compose

## Setup and Running the Application

1. Clone the repository: 

```git clone https://github.com/saketh7502/Avail2_Brute_SQLi.git```

- Then cd Avail2_Brute_SQLi
 
2. Build the Docker image:
```docker-compose build```


3. Start the application:
```docker-compose up```

4. Access the application:
Open a web browser and navigate to `http://localhost:8087`

## Usage

- The application presents a login form vulnerable to brute force attacks.
- There's also a "Forgot Password" feature vulnerable to SQL injection.
- Use the provided list of usernames and passwords to attempt brute force login.
- Experiment with SQL injection techniques on the "Forgot Password" page.


