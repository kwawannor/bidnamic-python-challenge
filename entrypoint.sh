#!/bin/bash

case "$1" in
endpoint)
  gunicorn --workers=1 --reload wsgi:app -b 0.0.0.0:8000
  ;;

test)
  pytest tests/
  ;;

loader)
  python load.py
  ;;

*)
  echo $"Usage: $0 {endpoint|test|loader}"
  exit 1
esac