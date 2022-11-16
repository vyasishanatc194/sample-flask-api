#!/bin/bash 

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

PORTS="${FLASK_PORT:-5001}"

echo $DIR/.env
set -a # automatically export all variables
source $DIR/.env
set +a


gunicorn wsgi --timeout 900 -w 5 -b 0.0.0.0:$PORTS
