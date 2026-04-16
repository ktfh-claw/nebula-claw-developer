# OpenNebula Restricted Control Plane

Basic Python REST API scaffold for a restricted OpenNebula control plane.

## Endpoints

- `GET /health` — simple health check
- `GET /vms` — list current VMs visible to the configured OpenNebula user
- `POST /vms` — create a VM from a template
- `DELETE /vms/<vm_id>` — terminate a VM by ID or name

## OpenNebula credentials

Credentials are configurable in `config.json`:

```json
{
  "opennebula": {
    "user": "restrictedapi",
    "password": "change-me"
  }
}
```

Behavior:

- if the configured OpenNebula user is `oneadmin`, the API does **not** add `--user`
- if the configured OpenNebula user is anything else, the API adds both `--user <name>` and `--password <password>`
- per-request overrides are also supported with `one_user` and `one_password` fields in JSON bodies
- for a restricted deployment, create a dedicated non-admin OpenNebula user and grant that user access only to curated templates, images, and networks

## Request examples

### List VMs

```bash
curl "http://127.0.0.1:8080/vms"
```

### Create VM from a readable template name

```bash
curl -X POST "http://127.0.0.1:8080/vms" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "alpine320-test",
    "name": "test-vm"
  }'
```

### Create VM as another OpenNebula user

```bash
curl -X POST "http://127.0.0.1:8080/vms" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "alpine320-test",
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

- `NEBULA_CLAW_DEVELOPER_API_CONFIG` — optional path to an alternate config file
- `NEBULA_CLAW_DEVELOPER_RESTRICTED_API_HOST` — bind host, default `127.0.0.1`
- `NEBULA_CLAW_DEVELOPER_RESTRICTED_API_PORT` — bind port, default `8080`

## Notes

This is intentionally a first scaffold:

- it uses OpenNebula CLI commands through a local restricted execution path
- it is not authenticated yet
- passwords in request bodies are acceptable for local testing only, not final production design
- create and delete behavior should be narrowed further before production use
