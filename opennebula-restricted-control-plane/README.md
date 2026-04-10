# OpenNebula Restricted Control Plane

Basic Python REST API scaffold for a restricted OpenNebula control plane.

## Endpoints

- `GET /health` — simple health check
- `GET /vms` — list current VMs visible through the configured OpenNebula command
- `POST /vms` — create a VM from a template for a specific user
- `DELETE /vms/<vm_id>?user=<name>` — delete a VM by ID

## Request examples

### List VMs

```bash
curl "http://127.0.0.1:8080/vms"
```

### Create VM

```bash
curl -X POST "http://127.0.0.1:8080/vms" \
  -H "Content-Type: application/json" \
  -d '{
    "user": "oneadmin",
    "template_id": 0,
    "name": "test-vm"
  }'
```

### Delete VM

```bash
curl -X DELETE "http://127.0.0.1:8080/vms/123?user=oneadmin"
```

## Configuration

Commands are configured in `config.json`.

Each endpoint maps to a shell command template. Placeholders are replaced safely before execution.

Current placeholders:

- `{template_id}`
- `{name}`
- `{user}`
- `{vm_id}`

The default configuration uses OpenNebula CLI commands executed through the local `oneadmin` account:

- list VMs with `onevm list`
- create VMs with `onetemplate instantiate`
- delete VMs with `onevm delete`

## Running locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Environment variables:

- `RESTRICTED_API_CONFIG` — optional path to an alternate config file
- `RESTRICTED_API_HOST` — bind host, default `127.0.0.1`
- `RESTRICTED_API_PORT` — bind port, default `8080`

## Notes

This is intentionally a first scaffold:

- it uses shell commands instead of a stronger internal adapter layer
- it is not authenticated yet
- it relies on local sudo rules / host policy for privilege boundaries
- create and delete behavior should be narrowed further before production use
