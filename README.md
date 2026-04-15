# nebula-claw-developer

Reference repository for the Nebula Claw Developer skill and its supporting example architecture.

## Repository layout

- `nebula-claw-developer/` — the publishable OpenClaw skill intended for ClawHub
- `opennebula-restricted-control-plane/` — reference restricted API implementation used by the skill
- `installation/` — environment setup notes and installation guidance for the reference lab

## What is publishable

The `nebula-claw-developer/` folder is the skill package boundary.

It contains:

- `SKILL.md`
- `references/`
- `scripts/`

That folder is the unit to publish to ClawHub.

## What is not part of the skill package

The rest of the repository is supporting implementation and documentation for the example environment:

- `opennebula-restricted-control-plane/` is not part of the skill bundle
- `installation/` is not part of the skill bundle

These folders are useful for operators who want to stand up the same architecture, but they should not be bundled into the published skill.

## Intended architecture

- OpenNebula runs on a single bare metal host that serves as both frontend and hypervisor.
- A NATed private virtual network hosts the OpenClaw VM and the disposable workload VMs.
- The restricted API runs on the bare metal OpenNebula host.
- The restricted API performs VM actions through a separate non-admin OpenNebula user with access only to curated resources.
- The OpenClaw VM uses the published skill to call the restricted API, then connects to the created VMs for development, testing, and deployment work.

### Reference architecture diagram

```mermaid
flowchart TD
    subgraph BM[Single bare metal OpenNebula host]
        FE[OpenNebula frontend]
        HV[OpenNebula hypervisor]
        API[Restricted control plane API]
        RU[Restricted OpenNebula user]

        subgraph VI[Virtual infrastructure on the hypervisor]
            OC[OpenClaw VM\nNebula Claw Developer skill]
            DEV[Disposable dev VM]
            TEST[Disposable test VM]
            DEPLOY[Disposable deployment VM]
            NET[Private VM network]
        end

        FE --- HV
        API --> RU
        RU --> FE
        NET --- OC
        NET --- DEV
        NET --- TEST
        NET --- DEPLOY
    end

    OC -- HTTP API calls --> API
    API -- create, list, delete --> RU
    OC -- SSH or normal access path --> DEV
    OC -- SSH or normal access path --> TEST
    OC -- SSH or normal access path --> DEPLOY

    classDef infra fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a,stroke-width:1.5px;
    classDef vm fill:#dcfce7,stroke:#16a34a,color:#14532d,stroke-width:1.5px;
    classDef network fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-width:1.5px;

    class FE,HV,API,RU infra;
    class OC,DEV,TEST,DEPLOY vm;
    class NET network;
```

## Publish workflow

From the repository root, publish the skill folder with the ClawHub CLI:

```bash
clawhub login
clawhub whoami
clawhub skill publish ./nebula-claw-developer \
  --slug nebula-claw-developer \
  --name "Nebula Claw Developer" \
  --version 1.0.0 \
  --changelog "Initial public release" \
  --tags latest
```

## Local test workflow

To test locally in an OpenClaw workspace, copy or symlink `nebula-claw-developer/` into a workspace `skills/` directory, then start a new session or restart the gateway.

Example:

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -a ./nebula-claw-developer ~/.openclaw/workspace/skills/nebula-claw-developer
openclaw gateway restart
```
