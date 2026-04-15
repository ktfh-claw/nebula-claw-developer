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

- OpenNebula provides the virtualization layer.
- A restricted API exposes a narrow VM lifecycle surface for curated templates.
- OpenClaw runs separately and uses the published skill to call that API.

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
