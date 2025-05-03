# Dark vault

- Namespace: picoctf/research
- ID: login-brute-force-script-treatment
- Type: custom
- Category: Web Exploitation
- Points: 1
- Templatable: no
- MaxUsers: 1

## Description

You will be able to access two lists of username:password pairs (credentials1.txt and credentials2.txt).
Load the credentials into `brute_force_script.py` and try to break the login form.
Keep an eye open on request rate limits... they might be onto you.

**NOTE: Do not close the Qualtrics survey.**


## Details

Browse {{link_as('/', 'here')}}, and find the flag!

**NOTE: Do not forget to download the Qualtrics data (`brute_force_challenge.txt`) along with the flag!**


## Hints

- You can use the walkthrough provided in the Qualtrics survey.

## Solution Overview

Use the provided brute force script. The solution is based on the number of attempts.

## Challenge Options

```yaml
cpus: 0.5
memory: 128m
pidslimit: 20
ulimits:
  - nofile=128:128
diskquota: 64m
init: true
```

## Learning Objective

Observe a brute force attack in action.

## Tags

- web

## Attributes

- author: DDM Lab
- organization: picoCTF
- event: picoCTF Experimental Problems 1
