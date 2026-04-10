# OpenNebula Restricted Control Plane

Placeholder for a future REST API layer used to communicate safely with the OpenNebula deployment.

## Purpose

Provide a constrained interface between OpenClaw and OpenNebula so infrastructure actions can be narrowed to approved operations, curated templates, and auditable workflows.

## Intended responsibilities

- expose a minimal API surface for approved VM operations
- enforce policy and template restrictions
- validate requests before they reach OpenNebula
- provide audit-friendly logging and traceability
- reduce direct exposure of broader OpenNebula administrative capabilities

## Planned TODOs

- [ ] Define API boundaries and threat model
- [ ] Choose authentication and authorization approach
- [ ] Model curated template and action policies
- [ ] Add request/response schema definitions
- [ ] Prototype a minimal service skeleton
