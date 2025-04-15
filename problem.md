# Brute Force

- Namespace: picoctf/examples
- ID: brute-force1
- Type: custom
- Category: General
- Points: 1
- Templatable: yes
- MaxUsers: 1

## Description

Identify and connect to 4 open ports on the target system.
Each successful connection will reveal part of the encrypted flag.

## Details

Access the challenge through this link:

## Hints

- You use the walkthrough

## Solution Overview

The provided text is PNG, which has been converted to base64 format

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

Identify various kinds of encoding.

## Tags

- python

## Attributes

- author: DDM Lab
- organization: picoCTF
- event: DDM LAB Research