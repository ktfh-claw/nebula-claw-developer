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
- Curated image: `ubuntu-24-curated`
- Curated VM template: `ubuntu-24-curated`
- Curated virtual network: `vm`

## 1. Create a dedicated non-admin OpenNebula user

```bash
sudo -u oneadmin oneuser create restrictedapi StrongTempPass123!
```

Verify:

```bash
sudo -u oneadmin oneuser list
```

## 2. Import a small curated image from the public marketplace

List marketplace apps and pick a readable Ubuntu image name:

```bash
sudo -u oneadmin onemarketapp list
```

Example import:

```bash
sudo -u oneadmin onemarketapp export "Ubuntu 24.04" ubuntu-24-curated --datastore default
```

This creates:

- an image named `ubuntu-24-curated`
- a VM template named `ubuntu-24-curated`

Verify:

```bash
sudo -u oneadmin oneimage list

sudo -u oneadmin onetemplate list
```

## 3. Put curated resources in a shared non-admin group

The example user is created in the `users` group. Move the curated resources into that group and allow group use.

Template:

```bash
sudo -u oneadmin onetemplate chgrp ubuntu-24-curated users

sudo -u oneadmin onetemplate chmod ubuntu-24-curated 640
```

Image:

```bash
sudo -u oneadmin oneimage chgrp ubuntu-24-curated users

sudo -u oneadmin oneimage chmod ubuntu-24-curated 640
```

Network:

```bash
sudo -u oneadmin onevnet chgrp vm users

sudo -u oneadmin onevnet chmod vm 640
```

## 4. Test direct OpenNebula access as the restricted user

List VMs:

```bash
sudo -u oneadmin onevm list --csv \
  --user restrictedapi \
  --password StrongTempPass123!
```

Create a VM from the curated template:

```bash
sudo -u oneadmin onetemplate instantiate ubuntu-24-curated \
  --name restricted-api-test \
  --user restrictedapi \
  --password StrongTempPass123!
```

Delete the VM:

```bash
sudo -u oneadmin onevm terminate restricted-api-test \
  --hard \
  --user restrictedapi \
  --password StrongTempPass123!
```

## 5. Customize the VM and the template for your need

### 5.1 Curate the VM template

Starting from the imported VM template from the marketplace, customize for the needs of your environment. You can find an example in `curated-vm-template-example.txt`.

### 5.2 Curate the VM disk/image

Access a test VM deployment as `root` from your OpenClaw VM (or anywhere else...), and run these setup steps:

```bash
adduser claw
# specify any password, and any user details in the responses
usermod -aG sudo claw
chsh -s /bin/bash claw
```

Test the new user, and then add some `sudo` policies:

```bash
sudo visudo
```

Add at the end of the file:
```bash
Defaults:claw !requiretty

claw ALL=(ALL) NOPASSWD: ALL
Cmnd_Alias CLAW_APT = /usr/bin/apt-get update, /usr/bin/apt-get install -y *
Cmnd_Alias CLAW_LINK = /usr/bin/ln, /usr/bin/install, /usr/bin/mkdir

claw ALL=(root) NOPASSWD: CLAW_APT, CLAW_LINK
```

And then `sudo visudo -c` should pass.

### 5.3 Save the disk 

After you are happy with the state of the OS, save its disk/image. E.g. from OpenNebula UI: Find the running VM, go to Storage tab, select the OS disk, Save-As. Then finally update the VM template to point to the cloned disk, i.e. replace the `<<CURATED OS IMAGE ID>>` in the above referenced example.

## 6. Configure the restricted control plane API

Copy the `opennebula-restricted-control-plane/config.json.template` to `opennebula-restricted-control-plane/config.json` and update the user/password of the OpenNebula user:

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

Place add the following sudoers rule file to `/etc/sudoers.d/nebula-claw-developer-api` after replacing "claw" with your user that will be executing the API:

```bash
$ sudo cat /etc/sudoers.d/nebula-claw-developer-api
claw ALL=(oneadmin) NOPASSWD: /usr/bin/onevm, /usr/bin/onetemplate, /usr/bin/oneuser, /usr/bin/onehost, /usr/bin/onecluster, /usr/bin/onedatastore, /usr/bin/onevnet
Defaults:claw !requiretty

$ sudo chmod 0440 /etc/sudoers.d/nebula-claw-developer-api
$ sudo visudo -c
```

## 7. Test the API

List VMs:

```bash
curl http://127.0.0.1:8080/vms
```

Create a VM:

```bash
curl -X POST http://127.0.0.1:8080/vms \
  -H "Content-Type: application/json" \
  -d '{"template_name":"ubuntu-24-curated","name":"restricted-api-test"}'
```

Delete the VM:

```bash
curl -X DELETE http://127.0.0.1:8080/vms/restricted-api-test
```

## 8. Connect the published skill to the API

The publishable skill lives in the repository `nebula-claw-developer/` folder.

When installing that skill into OpenClaw, point it at the restricted API with `API_BASE`, for example:

```bash
API_BASE=http://10.1.1.130:8080 ./nebula-claw-developer/scripts/vm_api.sh health
```

For a ClawHub release, keep deployment-specific endpoints outside the published skill and provide them at install or runtime.
```

Delete a VM:

```bash
curl -X DELETE http://127.0.0.1:8080/vms/restricted-api-via-rest
```

## Notes

- In the current implementation, VM deletion should ideally support names as first-class identifiers, not only numeric IDs.
- For production use, move the OpenNebula password out of `config.json` into environment variables or a secret store.
- The next hardening step should be an allowlist of template names that the API is allowed to instantiate.
