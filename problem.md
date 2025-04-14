# Brute Force

- Namespace: picoctf/research
- ID: brute-force-login
- Type: custom
- Category: Web
- Points: 1
- Templatable: no
- Max Users: 1

## Description
You are given two lists of username:password pairs.
Your goal: Find the correct credentials to log in!

The server will slow you down if you try too many times or switch lists.


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
