#!/bin/bash
# uvicorn main:app --reload
uvicorn main:app --reload --log-level debug --access-log
