# Restricted OpenNebula User Setup

This document shows how to prepare a non-admin OpenNebula user for the restricted control plane API.

The goal is:

- keep `oneadmin` as the local execution identity on the node
- use a dedicated OpenNebula user for API-visible operations
- allow that user to manage only curated resources
- prefer human-readable names instead of numeric IDs whenever possible

## Example curated resources

This example uses the following names:

- OpenNebula user: `restrictedapi`
- Curated image: `alpine320-test`
- Curated VM template: `alpine320-test`
- Curated virtual network: `vm`

## 1. Create a dedicated non-admin OpenNebula user

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  oneuser create restrictedapi StrongTempPass123!
```

Verify:

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  oneuser list
```

## 2. Import a small curated image from the public marketplace

List marketplace apps and pick a readable Alpine image name:

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  onemarketapp list
```

Example import:

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  onemarketapp export "Alpine Linux 3.20" alpine320-test --datastore default
```

This creates:

- an image named `alpine320-test`
- a VM template named `alpine320-test`

Verify:

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  oneimage list

sudo -u oneadmin env HOME=/var/lib/one \
  onetemplate list
```

## 3. Put curated resources in a shared non-admin group

The example user is created in the `users` group. Move the curated resources into that group and allow group use.

Template:

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  onetemplate chgrp alpine320-test users

sudo -u oneadmin env HOME=/var/lib/one \
  onetemplate chmod alpine320-test 640
```

Image:

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  oneimage chgrp alpine320-test users

sudo -u oneadmin env HOME=/var/lib/one \
  oneimage chmod alpine320-test 640
```

Network:

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  onevnet chgrp vm users

sudo -u oneadmin env HOME=/var/lib/one \
  onevnet chmod vm 640
```

## 4. Test direct OpenNebula access as the restricted user

List VMs:

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  onevm list --csv \
  --user restrictedapi \
  --password StrongTempPass123!
```

Create a VM from the curated template:

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  onetemplate instantiate alpine320-test \
  --name restricted-api-test \
  --hold \
  --user restrictedapi \
  --password StrongTempPass123!
```

Delete the VM:

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  onevm terminate restricted-api-test \
  --hard \
  --user restrictedapi \
  --password StrongTempPass123!
```

## 5. Configure the restricted control plane API

Example `opennebula-restricted-control-plane/config.json`:

```json
{
  "opennebula": {
    "user": "restrictedapi",
    "password": "StrongTempPass123!"
  }
}
```

Behavior in the current prototype:

- if `user` is `oneadmin`, the API omits `--user`
- otherwise, the API adds `--user` and `--password`

## 6. Test the API

List VMs:

```bash
curl http://127.0.0.1:8080/vms
```

Create a VM:

```bash
curl -X POST http://127.0.0.1:8080/vms \
  -H "Content-Type: application/json" \
  -d '{"template_id":"alpine320-test","name":"restricted-api-via-rest"}'
```

Delete a VM:

```bash
curl -X DELETE http://127.0.0.1:8080/vms/restricted-api-via-rest
```

## Notes

- In the current implementation, VM deletion should ideally support names as first-class identifiers, not only numeric IDs.
- For production use, move the OpenNebula password out of `config.json` into environment variables or a secret store.
- The next hardening step should be an allowlist of template names that the API is allowed to instantiate.
