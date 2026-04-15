# Restricted User Setup Reference

## Purpose

Use a dedicated non-admin OpenNebula user for restricted control plane actions, while still executing the local CLI on the node through the local service account.

## Example values

- OpenNebula user: `restrictedapi`
- Curated image: `alpine320-test`
- Curated template: `alpine320-test`
- Curated network: `vm`

## Create the restricted user

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  oneuser create restrictedapi StrongTempPass123!
```

## Import a curated Alpine image from the marketplace

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  onemarketapp export "Alpine Linux 3.20" alpine320-test --datastore default
```

## Share curated resources with the non-admin group

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

## Direct command tests as restricted user

List:

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  onevm list --csv --user restrictedapi --password StrongTempPass123!
```

Create:

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  onetemplate instantiate alpine320-test \
  --name restricted-api-test \
  --hold \
  --user restrictedapi \
  --password StrongTempPass123!
```

Delete:

```bash
sudo -u oneadmin env HOME=/var/lib/one \
  onevm terminate restricted-api-test \
  --hard \
  --user restrictedapi \
  --password StrongTempPass123!
```

## API config example

```json
{
  "opennebula": {
    "user": "restrictedapi",
    "password": "change-me"
  }
}
```

## Follow-up hardening

- Move the password out of JSON config.
- Add API authentication.
- Allowlist template names.
- Add TTL-based cleanup for disposable VMs.
- Restrict bind address and network exposure according to the deployment.
