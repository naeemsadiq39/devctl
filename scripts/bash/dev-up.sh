#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
python "$ROOT/scripts/python/devctl_core.py" dev-up "$@"
