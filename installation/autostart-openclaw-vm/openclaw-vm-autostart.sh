#!/usr/bin/env bash
set -euo pipefail

# OpenClaw VM ID in OpenNebula
VM_ID="<<OPENCLAW_VM_ID>>"
MAX_WAIT_SECONDS=600
POLL_SECONDS=10

deadline=$((SECONDS + MAX_WAIT_SECONDS))

echo "Waiting for OpenNebula VM $VM_ID state to settle..."

while (( SECONDS < deadline )); do
    state="$(onevm show "$VM_ID" -x | xmllint --xpath 'string(/VM/STATE)' - 2>/dev/null || true)"
    lcm_state="$(onevm show "$VM_ID" -x | xmllint --xpath 'string(/VM/LCM_STATE)' - 2>/dev/null || true)"

    echo "VM $VM_ID STATE=$state LCM_STATE=$lcm_state"

    # OpenNebula STATE=3 usually means ACTIVE/running.
    # STATE=8 usually means POWEROFF.
    if [[ "$state" == "8" ]]; then
        echo "VM $VM_ID is POWEROFF; resuming..."
        onevm resume "$VM_ID"
        exit 0
    fi

    # If it is genuinely still active after the wait window, do nothing.
    sleep "$POLL_SECONDS"
done

echo "Timeout reached; checking final state..."

onevm list
final_state="$(onevm show "$VM_ID" -x | xmllint --xpath 'string(/VM/STATE)' - 2>/dev/null || true)"

if [[ "$final_state" == "8" ]]; then
    echo "VM $VM_ID is POWEROFF after timeout; resuming..."
    onevm resume "$VM_ID"
else
    echo "VM $VM_ID is not POWEROFF; leaving unchanged."
fi
