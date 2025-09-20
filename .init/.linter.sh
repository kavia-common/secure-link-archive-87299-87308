#!/bin/bash
cd /home/kavia/workspace/code-generation/secure-link-archive-87299-87308/link_shortener_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

