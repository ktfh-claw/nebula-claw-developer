# nebula-claw-developer

Example repository for building an OpenClaw skill that operates disposable OpenNebula virtual machines through a restricted control plane API.

## Repository layout

- `operation/` — the publishable OpenClaw skill intended for ClawHub
- `opennebula-restricted-control-plane/` — reference restricted API implementation used by the skill
- `installation/` — environment setup notes and installation guidance for the reference lab

## What is publishable

The `operation/` folder is the skill package boundary.

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

- OpenNebula provides the virtualization layer.
- A restricted API exposes a narrow VM lifecycle surface for curated templates.
- OpenClaw runs separately and uses the published skill to call that API.

## Publish workflow

From the repository root, publish the skill folder with the ClawHub CLI:

```bash
clawhub login
clawhub whoami
clawhub skill publish ./operation \
  --slug opennebula-operation \
  --name "OpenNebula Operation" \
  --version 1.0.0 \
  --changelog "Initial public release" \
  --tags latest
```

## Local test workflow

To test locally in an OpenClaw workspace, copy or symlink `operation/` into a workspace `skills/` directory, then start a new session or restart the gateway.

Example:

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -a ./operation ~/.openclaw/workspace/skills/opennebula-operation
openclaw gateway restart
```
