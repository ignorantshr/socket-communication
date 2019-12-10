#!/usr/bin/env bash

python_lib="/usr/lib/python2.7/site-packages"

install -p -dm 0755 ${python_lib}/communication/protocol/
install -p -m 0644 protocol/*.py ${python_lib}/communication/protocol/
install -p -m 0644 __init__.py ${python_lib}/communication/__init__.py
rm -f ${python_lib}/communication/*.pyc
rm -f ${python_lib}/communication/protocol/*.pyc
