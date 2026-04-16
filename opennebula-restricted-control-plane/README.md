# OpenNebula Restricted Control Plane

Basic Python REST API scaffold for a restricted OpenNebula control plane.

## Endpoints

- `GET /health` — simple health check plus configured visible template catalog
- `GET /templates` — list curated VM templates exposed to the API
- `GET /vms` — list current VMs visible to the configured OpenNebula user, including guest IP when OpenNebula reports it
- `POST /vms` — create a VM from an allowed curated template
- `DELETE /vms/<vm_id>` — terminate a VM by ID or name

## OpenNebula credentials

Credentials and curated templates are configurable in `config.json`:

```json
{
  "opennebula": {
    "user": "restrictedapi",
    "password": "change-me"
  },
  "templates": [
    {
      "name": "curated-ubuntu-24-04-for-nebula-claw-developer",
      "description": "Ubuntu 24.04 curated development VM for disposable OpenClaw and infrastructure experiments."
    }
  ]
}
```

Behavior:

- if the configured OpenNebula user is `oneadmin`, the API does **not** add `--user`
- if the configured OpenNebula user is anything else, the API adds both `--user <name>` and `--password <password>`
- per-request overrides are also supported with `one_user` and `one_password` fields in JSON bodies
- if `templates` is non-empty, `POST /vms` only allows template names from that configured allowlist
- for a restricted deployment, create a dedicated non-admin OpenNebula user and grant that user access only to curated templates, images, and networks

## Request examples

### List VMs

```bash
curl "http://127.0.0.1:8080/vms"
```

### List curated templates

```bash
curl "http://127.0.0.1:8080/templates"
```

### Create VM from a readable template name

```bash
curl -X POST "http://127.0.0.1:8080/vms" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "curated-ubuntu-24-04-for-nebula-claw-developer",
    "name": "test-vm"
  }'
```

### Create VM as another OpenNebula user

```bash
curl -X POST "http://127.0.0.1:8080/vms" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "curated-ubuntu-24-04-for-nebula-claw-developer",
    "name": "test-vm",
    "one_user": "alice",
    "one_password": "secret"
  }'
```

### Delete VM by numeric ID

```bash
curl -X DELETE "http://127.0.0.1:8080/vms/123"
```

### Delete VM by name

```bash
curl -X DELETE "http://127.0.0.1:8080/vms/restricted-api-via-rest"
```

This currently maps to a hard terminate action in OpenNebula.

## Running locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Environment variables:

- `NEBULA_CLAW_DEVELOPER_RESTRICTED_API_CONFIG` — optional path to an alternate config file
- `NEBULA_CLAW_DEVELOPER_RESTRICTED_API_HOST` — bind host, default `127.0.0.1`
- `NEBULA_CLAW_DEVELOPER_RESTRICTED_API_PORT` — bind port, default `8080`

## Running as a systemd service on Ubuntu

Example unit file:
- `nebula-claw-developer-api.service.example`

Suggested install flow:

```bash
sudo mkdir -p /opt/nebula-claw-developer
sudo cp -a opennebula-restricted-control-plane /opt/nebula-claw-developer/
cd /opt/nebula-claw-developer/opennebula-restricted-control-plane
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
sudo mkdir -p /etc/nebula-claw-developer
sudo cp config.json.template /etc/nebula-claw-developer/config.json
sudo cp nebula-claw-developer-api.service.example /etc/systemd/system/nebula-claw-developer-api.service
sudo systemctl daemon-reload
sudo systemctl enable --now nebula-claw-developer-api.service
sudo systemctl status nebula-claw-developer-api.service
```

## Sudo and password-prompt guidance

This API shell-outs through:
- `sudo -u oneadmin env HOME=/var/lib/one onevm ...`
- `sudo -u oneadmin env HOME=/var/lib/one onetemplate ...`
- related `one*` commands

If the service user is prompted for a password, the usual cause is missing sudoers policy, not systemd itself.

The service account must have passwordless sudo rights for the exact OpenNebula CLI commands it will execute, for example:

```bash
claw ALL=(oneadmin) NOPASSWD: /usr/bin/onevm, /usr/bin/onetemplate, /usr/bin/oneuser, /usr/bin/onehost, /usr/bin/onecluster, /usr/bin/onedatastore, /usr/bin/onevnet
Defaults:claw !requiretty
```

Validate with:

```bash
sudo visudo -c
sudo -l -U claw
```

If `sudo` still prompts under systemd, check:
- the service runs as the expected `User=`
- command paths in sudoers match the actual binaries exactly
- no distro policy or sudoers include overrides are reintroducing `requiretty`

## Notes

This is intentionally a first scaffold:

- it uses OpenNebula CLI commands through a local restricted execution path
- it is not authenticated yet
- passwords in request bodies are acceptable for local testing only, not final production design
- create and delete behavior should be narrowed further before production use
