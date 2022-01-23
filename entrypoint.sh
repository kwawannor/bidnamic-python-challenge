#!/bin/bash

case "$1" in
endpoint)
  gunicorn --workers=1 --reload wsgi:app
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