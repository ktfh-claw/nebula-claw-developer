# Installation

This folder holds setup notes for a reference OpenNebula + OpenClaw environment.

## Goals

- deploy OpenNebula with `one-deploy`
- document environment-specific inventory and bootstrap steps
- create a VM for OpenClaw
- install and configure OpenClaw inside that VM

## Suggested flow

1. Prepare the target host(s) and networking.
2. Adapt `inventory-example.yml` into a real inventory file for the environment.
3. Use `one-deploy` to install OpenNebula.
4. Verify frontend and node functionality.
5. Create a VM that will host OpenClaw.
6. Install OpenClaw in that VM following the official docs.
7. Limit OpenClaw's permissions so it can only manage curated VM templates / workflows.

## OpenNebula setup notes

- Start from the official `one-deploy` documentation and examples.
- Keep the inventory under version control only after removing or externalizing secrets.
- Validate bridge/NAT/networking assumptions for the target environment.
- Confirm datastore mode (`ds.mode`) and virtual network details before deployment.

## TODOs

- [ ] Write concrete `one-deploy` steps for this environment
- [ ] Document NAT configuration requirements and examples
- [x] Document post-install OpenNebula user / group / ACL configuration
- [x] Define the curated VM templates OpenClaw is allowed to manage
- [ ] Add a hardening checklist for the OpenClaw VM
- [ ] Add backup / snapshot recommendations

## Restricted control plane setup

See `restricted-user-setup.md` for a concrete example of:

- creating a non-admin OpenNebula user for the API
- importing a curated Alpine image from the marketplace
- sharing the curated template, image, and network with a non-admin group
- configuring the API to use readable names instead of mostly numeric IDs

## Creating the OpenClaw VM

Suggested placeholder process:

1. Create a VM template in OpenNebula for the OpenClaw controller VM.
2. Provision the VM with a supported Linux distribution.
3. Assign networking that allows:
   - outbound internet access for package installs and integrations
   - access to the OpenNebula control endpoint or restricted API layer
   - any private network access required for managed development VMs
4. Bootstrap SSH access and baseline security.

## Installing OpenClaw in the VM

Follow the official OpenClaw documentation for installation and gateway setup:

- Local docs on the host where OpenClaw is installed
- Mirror: https://docs.openclaw.ai
- Source: https://github.com/openclaw/openclaw

Suggested follow-up documentation to add later:

- exact VM sizing guidance
- systemd/gateway setup notes
- secret handling pattern for service-managed environments
- node pairing / remote access model
