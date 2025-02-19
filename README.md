# uhtf

A micro hardware test framework (HTF).

## Install

### Repository

When using git, clone the repository and change your 
present working directory.

```shell
git clone http://github.com/mcpcpc/uhtf
cd uhtf/
```

Create and activate a virtual environment.

```shell
python -m venv venv
source venv/bin/activate
```

Install uhtf to the virtual environment.

```shell
pip install -e .
```

## Commands

### db-init

The backend database can be initialized or re-initialized 
with the following command.

```shell
quart --app uhtf init-db
```

## Deploy

## Docker Container

Pulling the latest container image from command line.

```shell
podman pull ghcr.io/mcpcpc/uhtf:latest
```

### Service

Replace `pi` with the appropriate user home directory.

```sh
podman generate systemd --new --files --name uhtf
mkdir -p /home/pi/.config/systemd/user
cp container-uhtf.service /home/pi/.config/systemd/user
systemctl --user daemon-reload
systemctl --user start container-uhtf.service
systemctl --user enable container-uhtf.service
loginctl enable-linger prod
```
