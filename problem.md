# Web CSS

- Namespace: picoctf/research
- ID: brute-force
- Type: custom
- Category: Web Exploitation
- Points: 1
- Templatable: yes
- MaxUsers: 1

## Description

You are given two lists of username:password pairs.
Your goal: Find the correct credentials to log in!

The server will slow you down if you try too many times or switch lists.

## Details

Browse {{link_as('/', 'here')}}, and find the flag!

Download the bruteforce script here: {{url_for("brute_force_script.py", "here")}}

## Hints

- Look at the Walkthrough

## Solution Overview

Use the provided brute force script.

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

Understand the concept of Brute forcing

## Tags

- web

## Attributes

- author: DDM Lab
- organization: picoCTF
- event: DDM LAB Research