#!/bin/bash

# Start WireGuard
wg-quick up wg0

python3 export.py --config_env conf/.env