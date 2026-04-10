# API Reference

## Endpoints

- `GET /health`
- `GET /vms`
- `POST /vms`
- `DELETE /vms/<vm_id_or_name>`

Prefer readable names over numeric identifiers whenever possible.

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

## Current example environment

- restricted API user: `restrictedapi`
- curated template: `alpine320-test`
- example network: `vm`

## Curl examples

Health:

```bash
curl http://127.0.0.1:8080/health
```

List:

```bash
curl http://127.0.0.1:8080/vms
```

Create:

```bash
curl -X POST http://127.0.0.1:8080/vms \
  -H "Content-Type: application/json" \
  -d '{"template_name":"alpine320-test","name":"test-nebula-api-2026-04-10"}'
```

Delete:

```bash
curl -X DELETE http://127.0.0.1:8080/vms/test-nebula-api-2026-04-10
```

## Notes

- If the configured OpenNebula user is `oneadmin`, the API omits `--user`.
- If the configured OpenNebula user is not `oneadmin`, the API adds `--user` and `--password`.
- The current delete path maps to a hard terminate operation in OpenNebula.
