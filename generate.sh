#!/bin/bash
# Simple script to generate nameplates

rm -rf ./output
source venv/bin/activate && python generate_nameplates.py
