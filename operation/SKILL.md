---
name: operation
description: Operate the restricted OpenNebula control plane for disposable development and testing VMs. Use when an OpenClaw agent needs to create, list, or terminate isolated VM environments on demand for software development, dependency installation, reproducible debugging, integration testing, or risky experiments that should not run on the main host.
---

# Operation

Use the restricted OpenNebula control plane API to provision short-lived VMs for isolated work.

## Goal

Create fully isolated virtual machines on demand so an agent can:

- test code changes safely
- install packages or services without polluting the main environment
- reproduce failures in a clean machine
- run risky or destructive experiments in a disposable sandbox
- validate behavior across a fresh system image

Treat these VMs as throwaway development and testing environments, not long-lived pets.

## Default workflow

1. Check the API health endpoint.
2. List currently visible VMs.
3. Reuse an existing suitable VM only if it clearly matches the task.
4. Otherwise create a fresh VM from an approved curated template.
5. Wait until the VM is reachable through the environment's normal access path.
6. Perform the development or testing task inside the VM.
7. Terminate the VM when the task is complete unless the user asks to keep it.

## API shape

Base endpoints:

- `GET /health`
- `GET /vms`
- `POST /vms`
- `DELETE /vms/<vm_id_or_name>`

Prefer readable names over numeric IDs whenever possible.

### Create request

Send JSON like:

```json
{
  "template_name": "alpine320-test",
  "name": "build-test-2026-04-10"
}
```

### Delete request

Prefer deleting by VM name:

```text
DELETE /vms/build-test-2026-04-10
```

## Naming guidance

Use clear, task-based VM names so later cleanup is obvious.

Recommended pattern:

- `<purpose>-<project>-<short-date>`

Examples:

- `test-nebula-api-2026-04-10`
- `build-myapp-2026-04-10`
- `repro-login-bug-2026-04-10`

Keep names short, descriptive, and unique enough to avoid collisions.

## Safety rules

Only use curated templates and networks that were intentionally shared with the restricted OpenNebula user.

Do not:

- use broad administrative OpenNebula privileges for routine VM work
- create long-lived infrastructure through this path
- assume arbitrary templates are safe to instantiate
- leave disposable VMs running after testing unless there is a clear reason

If the task needs persistence, say so explicitly and document why the VM should be kept.

## Suggested agent behavior

When using this skill:

- prefer a fresh VM for risky package installs, system-level changes, or integration tests
- prefer reusing a running VM only when setup cost matters and the environment is known to be compatible
- capture the VM name in notes or task output so it can be cleaned up later
- summarize what was tested in the isolated VM and whether the VM was destroyed afterward

## Current example environment

Current curated example resources in this project:

- template name: `alpine320-test`
- API-backed restricted user: `restrictedapi`

Read `installation/restricted-user-setup.md` when you need the concrete OpenNebula-side setup steps.

## Minimal usage examples

Health check:

```bash
curl http://127.0.0.1:8080/health
```

List VMs:

```bash
curl http://127.0.0.1:8080/vms
```

Create a VM:

```bash
curl -X POST http://127.0.0.1:8080/vms \
  -H "Content-Type: application/json" \
  -d '{"template_name":"alpine320-test","name":"test-nebula-api-2026-04-10"}'
```

Delete a VM:

```bash
curl -X DELETE http://127.0.0.1:8080/vms/test-nebula-api-2026-04-10
```

## When to read more

Read `../opennebula-restricted-control-plane/README.md` when you need endpoint details or credential behavior.

Read `../installation/restricted-user-setup.md` when you need to recreate the restricted OpenNebula user, curated template, or permission model.
