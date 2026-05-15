#!/usr/bin/env bash
set -euo pipefail

MAX_WAIT_SECONDS=600
POLL_SECONDS=10

# OpenNebula STATE values:
# STATE=3 => ACTIVE / appears running
# STATE=8 => POWEROFF

echo "Finding VMs that currently appear to be running..."

mapfile -t VM_IDS < <(
    onevm list -x | xmllint --xpath '//VM[STATE=3]/ID/text()' - 2>/dev/null | xargs -n1 echo
)

if (( ${#VM_IDS[@]} == 0 )); then
    echo "No VMs appear to be running. Nothing to do."
    exit 0
fi

echo "Found running VM(s): ${VM_IDS[*]}"

echo "Issuing poweroff for each running VM..."

for vm_id in "${VM_IDS[@]}"; do
    echo "Powering off VM $vm_id..."
    onevm poweroff "$vm_id" || {
        echo "WARNING: failed to poweroff VM $vm_id; continuing."
    }
done

echo "Waiting for VM(s) to reach POWEROFF state..."

deadline=$((SECONDS + MAX_WAIT_SECONDS))

while (( SECONDS < deadline )); do
    pending=()

    for vm_id in "${VM_IDS[@]}"; do
        state="$(
            onevm show "$vm_id" -x \
                | xmllint --xpath 'string(/VM/STATE)' - 2>/dev/null \
                || true
        )"

        lcm_state="$(
            onevm show "$vm_id" -x \
                | xmllint --xpath 'string(/VM/LCM_STATE)' - 2>/dev/null \
                || true
        )"

        echo "VM $vm_id STATE=$state LCM_STATE=$lcm_state"

        if [[ "$state" != "8" ]]; then
            pending+=("$vm_id")
        fi
    done

    if (( ${#pending[@]} == 0 )); then
        echo "All target VM(s) reached POWEROFF."
        break
    fi

    echo "Still waiting for VM(s): ${pending[*]}"
    sleep "$POLL_SECONDS"
done

echo "Final state check before resume..."

resume_ids=()

for vm_id in "${VM_IDS[@]}"; do
    state="$(
        onevm show "$vm_id" -x \
            | xmllint --xpath 'string(/VM/STATE)' - 2>/dev/null \
            || true
    )"

    lcm_state="$(
        onevm show "$vm_id" -x \
            | xmllint --xpath 'string(/VM/LCM_STATE)' - 2>/dev/null \
            || true
    )"

    echo "VM $vm_id final STATE=$state LCM_STATE=$lcm_state"

    if [[ "$state" == "8" ]]; then
        resume_ids+=("$vm_id")
    else
        echo "WARNING: VM $vm_id did not reach POWEROFF; not resuming it."
    fi
done

if (( ${#resume_ids[@]} == 0 )); then
    echo "No VM reached POWEROFF. Nothing to resume."
    exit 1
fi

echo "Resuming VM(s): ${resume_ids[*]}"

for vm_id in "${resume_ids[@]}"; do
    echo "Resuming VM $vm_id..."
    onevm resume "$vm_id" || {
        echo "WARNING: failed to resume VM $vm_id."
    }
done

echo "Done."