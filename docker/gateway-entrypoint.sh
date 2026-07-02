#!/bin/bash
set -e

cd /data
/usr/local/bin/stordy &
STORDY_PID=$!

for i in $(seq 1 30); do
  if python2 -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('127.0.0.1', 50052)); s.close()" 2>/dev/null; then
    break
  fi
  if ! kill -0 "$STORDY_PID" 2>/dev/null; then
    echo "Stordy failed to start" >&2
    exit 1
  fi
  if [ "$i" -eq 30 ]; then
    echo "Timed out waiting for Stordy on port 50052" >&2
    exit 1
  fi
  sleep 1
done

cd /app/API
exec python2 runner.py \
  -n "${NAME_SERVER_HOST}" -p 9090 \
  -G "${GATEWAY_NAME}" -C "${GATEWAY_CONTEXT:-0001}" -S "${POOL_SIZE:-1}"
