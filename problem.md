# Brute Force

- Namespace: picoctf/examples
- ID: brute-force
- Type: custom
- Category: General
- Points: 1
- Templatable: yes
- MaxUsers: 1

## Description
You are given two lists of username:password pairs.
Your goal: Find the correct credentials to log in!

The server will slow you down if you try too many times or switch lists.

## Details

Browse {{server("web")}}:{{port("web")}}, and find the flag!

Download the bruteforce script here: {{url_for("brute_force_script.py", "here")}}

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
## Attributes

- author: DDM Lab
- organization: picoCTF
- event: S-25 ddmlab reseach study
