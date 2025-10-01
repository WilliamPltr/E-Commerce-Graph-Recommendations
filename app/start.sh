#!/usr/bin/env bash
set -euo pipefail

cd /work/app
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload


