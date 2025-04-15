# Brute_Force_Challenge

- Namespace: picoctf/research
- ID: login-brute-force-script
- Type: custom
- Category: Web Exploitation
- Points: 1
- Templatable: yes
- MaxUsers: 1

## Description

You are given two lists of username:password pairs.
Your goal: Find the correct credentials to log in!

The server will slow you down if you try too many times or switch lists

## Details

Browse {{link_as('/', 'here')}}, and find the flag!
Good Luck!

## Hints

- Look at the hints on the Walkthrough

## Solution Overview

Use The provided bruteforce script.

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

Understand Brute Force attacks

## Tags

- web

## Attributes

- author: DDM Lab
- organization: picoCTF
- event: DDM LAB Research