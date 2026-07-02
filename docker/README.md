# SpeedChain + Stordy Docker

Two gateways (each with its own Stordy storage volume), a Pyro4 name server, and an interactive device simulator.

## Prerequisites

- Docker and Docker Compose
- Git submodule `stordy/` initialized at repo root:

```bash
git submodule update --init --recursive
```

## Start infrastructure (detached)

```bash
docker compose up -d --build
```

This starts:

- `name-server` on port **9090**
- `gateway-a` (`gwa`) with storage in `./volumes/gwa`
- `gateway-b` (`gwb`) with storage in `./volumes/gwb`

Check logs:

```bash
docker compose logs -f gateway-a gateway-b
```

Look for `Stordy initialize!!` and gateway startup messages.

## Interactive device (foreground)

Run in a separate terminal (blocks until you exit the device menu):

```bash
docker compose --profile interactive run --rm device
```

Connect to a different gateway or rename the device:

```bash
docker compose --profile interactive run --rm \
  -e GATEWAY_NAME=gwb -e DEVICE_NAME=dev-b device
```

Suggested first test inside the device menu:

1. Option **12** — enter `None` (no consensus algorithm)
2. Option **3** — authenticate (creates device block, obtains AES key)
3. Option **4** — enter `1` (send one simulated transaction)
4. Option **5** — list blocks (optional)

## Tear down

```bash
docker compose down
```

Blockchain data persists under `./volumes/gwa` and `./volumes/gwb`.

## Apple Silicon

Gateway and device images are built for `linux/amd64` for Python 2.7 / grpcio compatibility. Docker Desktop will emulate if needed.

The first gateway build can take several minutes while `grpcio` compiles from source.

## Debian Buster (Python 2.7 base image)

The official `python:2.7-slim` image uses EOL Debian Buster. The Dockerfiles point apt at `archive.debian.org` so package installs keep working.

## Troubleshooting

**`unknown name: gwa` when starting the device**

The gateways were not running or had crashed. Check:

```bash
docker compose ps
docker compose logs gateway-a gateway-b
```

Both gateways must show `Up`. If they exited, rebuild and restart:

```bash
docker compose up -d --build
```

**Gateway crashes mentioning GLIBC**

Stordy is built as a statically linked musl binary so it runs inside the older Python 2.7 image.

**`No module named google.protobuf`**

Rebuild gateways after pulling the latest `docker/requirements-gateway.txt` (includes `protobuf`).
