# Introduction

This problem demonstrates a brute-force attack on an online login form. You are given two lists of username and passwords in .txt files with the format "<username>:<password>".

The goal of this problem is to fill in the missing information in the provided script and install the required dependencies to be able to run.

In this walkthrough you have two files:
1. This file `walkthrough.md`
2. The solver `requirements.txt`

# Steps

1) We need to download the two credentials provided, `credentials1.txt` and `credentials2.txt`. If you are having trouble downloading, try right-clicking the URL and choosing "Download Linked File." If that doesn't work, try changing browsers or reviewing your current browser's settings.
2) We then need to place these into a directory that we can reference later. We will need their absolute path for our script.
3) We will now download the file `brute_force_script.py`. This file contains the code that we can use to try username and password combinations on the webserver.
    a) Note: this file will not only allow us to try username and password combinations, but also will print any messages we get from the server.
4) We then need to install some requirements. It is preferable if we create a `virtualenv` to do this. You can find information on how to do this (here)[https://docs.python.org/3/library/venv.html]
5) Then, once we have the virtual environment, we can install the requirements file provided with this document. You can do this with `pip install -r /path/to/requirements.txt`
    a) Note: the current `requirements.txt` file lists Python packages and versions that may not be available for your operating system. This means you need to find and install an alternative version. A way you can do this is `pip install <package_name>`.
6) To use this script, we will need to modify 3 things:
    a) First, find the absolute path for the credentials you downloaded. They should look like this "`/path/to/credentials1.txt`" (e.g., `/home/your_user/Downloads/bruteforce_files/credentials1.txt`)
    b) Currently, there are the following placeholders:
        ```
        # Replace with your own paths
        PATH_TO_CREDENTIAL_1 = "/path/to" + "credentials1.txt"
        PATH_TO_CREDENTIAL_2 = "/pat/to" + "credentials2.txt"
        ```
    c) Then, we need to replace the BASE_URL. Head to your browser and copy the URL that you are using to access the file.
        ```
        # Replace with your own base URL
        BASE_URL = 'http://127.0.0.1:8087'
        ```
6) We are now able to run the script. If you were able to follow the steps above. You should get the following:

```
> Initial credential list (1/2):
```

7) Here, you can choose which list you want to start with. For more information about the lists, refer to this website's landing page. After you choose a list, you will see:

```
Initial credential list (1/2): 1
Testing List 1:   0%|               | 0/100 [00:40<16:03, 10.04s/it]
```

This progress bar will indicate how far along (and how fast) you are in testing the current list. Keep an eye open for potential throttling!

    a) Note: If you use an incorrect credentials list, you will be flagged by the system and see something like:

        ```
        2025-04-07 15:28:02: Server: Account Locked!
        We detected that you're trying to use credentials that are not in our system.
        Please download the latest credential files and try again:

        Download Credentials List 1 (<url>/credentials1.txt)
        Download Credentials List 2 (<url>/credentials2.txt)
        ```

8) When you found a successful combination, you will get this message:

```
Valid credentials found!
Username: x6e2yjck
Password: 7G6VL6Kxvq
Let's try logging in?
```

You can then proceed to the web app and try logging in.

9) Finally, in this page, you will find the flag and a link to download a `qualtrics_data_bruteforce.txt` file. Please download this file and place it in the designated field in the survey. Also, grab the flag and make sure you place it in the survey.

Hope you enjoyed this problem!
    