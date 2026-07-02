#!/bin/bash
set -e

cd /app/API

python2 - <<'PY'
import os
import sys
import time

import Pyro4

host = os.environ["NAME_SERVER_HOST"]
gateway = os.environ["GATEWAY_NAME"]
port = 9090

for attempt in range(60):
    try:
        ns = Pyro4.locateNS(host=host, port=port)
        ns.lookup(gateway)
        print("Gateway %s is registered" % gateway)
        sys.exit(0)
    except Pyro4.errors.NamingError:
        if attempt == 59:
            print >> sys.stderr, "Timed out waiting for gateway %s on %s:%s" % (gateway, host, port)
            print >> sys.stderr, "Make sure gateways are running: docker compose up -d"
            sys.exit(1)
        time.sleep(2)
PY

exec python2 src/tools/DeviceSimulator.py \
  "${NAME_SERVER_HOST}" 9090 "${GATEWAY_NAME}" "${DEVICE_NAME}"
