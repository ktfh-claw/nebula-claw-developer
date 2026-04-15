# API Reference

## Purpose

The skill talks to a restricted OpenNebula control plane API that exposes a narrow VM lifecycle surface for disposable environments.

## Endpoints

- `GET /health`
- `GET /vms`
- `POST /vms`
- `DELETE /vms/<vm_id_or_name>`

Prefer readable VM and template names over numeric identifiers whenever possible.

## Create VM

Request body:

```json
{
  "template_name": "alpine320-test",
  "name": "test-nebula-api-2026-04-10"
}
```

Optional OpenNebula credential override for testing:

```json
{
  "template_name": "alpine320-test",
  "name": "test-nebula-api-2026-04-10",
  "one_user": "restrictedapi",
  "one_password": "change-me"
}
```

## Delete VM

Delete by name when possible:

```text
DELETE /vms/test-nebula-api-2026-04-10
```

## Expected environment inputs

The skill expects an API base URL to be available to the helper script, typically through the `API_BASE` environment variable.

Example:

```bash
API_BASE=http://10.1.1.130:8080 ./scripts/vm_api.sh health
```

Do not hardcode one deployment-specific endpoint into the published skill unless the installation explicitly targets one environment.

## Current example environment

- restricted API user: `restrictedapi`
- curated template: `alpine320-test`
- example network: `vm`

## Curl examples

Health:

```bash
curl "$API_BASE/health"
```

List:

```bash
curl "$API_BASE/vms"
```

Create:

```bash
curl -X POST "$API_BASE/vms" \
  -H "Content-Type: application/json" \
  -d '{"template_name":"alpine320-test","name":"test-nebula-api-2026-04-10"}'
```

Delete:

```bash
curl -X DELETE "$API_BASE/vms/test-nebula-api-2026-04-10"
```

## Notes

- If the configured OpenNebula user is `oneadmin`, the API omits `--user`.
- If the configured OpenNebula user is not `oneadmin`, the API adds `--user` and `--password`.
- The current delete path maps to a hard terminate action in OpenNebula.
