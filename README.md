# nebula-claw-developer

An example preintegrated combination of OpenNebula and OpenClaw.

In this setup, OpenClaw runs inside a VM and is able to manage a limited set of VMs on the same OpenNebula instance it runs on, using curated templates and guardrails suitable for development, testing, and integration environments for arbitrary software projects.

## Scope

This repository is intended to capture:

- installation guidance for provisioning an OpenNebula environment with `one-deploy`
- operational guidance and future automation hooks
- a restricted control plane API for safe communication with the OpenNebula deployment
- patterns for running OpenClaw inside a VM while letting it manage a constrained pool of sibling VMs

## Repository layout

- `installation/` — setup notes, inventory examples, and OpenNebula/OpenClaw installation guidance
- `operation/` — operational docs and future skills/automation
- `opennebula-restricted-control-plane/` — placeholder for a future REST API

## Intended architecture

- OpenNebula provides the virtualization layer
- OpenClaw runs inside a dedicated VM on that same OpenNebula installation
- OpenClaw can create/manage a curated subset of VMs for dev, test, and integration use cases
- a restricted API layer mediates higher-risk infrastructure actions

## Status

Early scaffold / placeholder repository.
