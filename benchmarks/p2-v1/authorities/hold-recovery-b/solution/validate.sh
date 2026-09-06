#!/bin/sh
python3 -m unittest discover -s checks -p 'spec_*.py' -v
