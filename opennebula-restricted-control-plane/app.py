#!/usr/bin/env python3
import csv
import io
import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config.json"
CONFIG_PATH = Path(os.environ.get("NEBULA_CLAW_DEVELOPER_RESTRICTED_API_CONFIG", DEFAULT_CONFIG_PATH))

app = Flask(__name__)


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


CONFIG = load_config()


class ApiError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@app.errorhandler(ApiError)
def handle_api_error(err: ApiError):
    return jsonify({"error": err.message}), err.status_code


@app.errorhandler(subprocess.CalledProcessError)
def handle_process_error(err: subprocess.CalledProcessError):
    stderr = (err.stderr or "").strip()
    stdout = (err.stdout or "").strip()
    return jsonify(
        {
            "error": "command_failed",
            "returncode": err.returncode,
            "stdout": stdout,
            "stderr": stderr,
        }
    ), 500


@app.errorhandler(Exception)
def handle_generic_error(err: Exception):
    return jsonify({"error": str(err)}), 500


def config_value(name: str, default: Any = None) -> Any:
    return CONFIG.get(name, default)


def build_shell_command(base_command: str, one_user: str, one_password: str | None = None) -> str:
    cmd = f"sudo -u oneadmin env HOME=/var/lib/one {base_command}"
    if one_user != "oneadmin":
        if not one_password:
            raise ApiError("password required when OpenNebula user is not oneadmin")
        cmd = f"{cmd} --user {shlex.quote(one_user)} --password {shlex.quote(one_password)}"
    return cmd


def run_shell(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        check=True,
    )


def resolve_one_credentials(payload: dict[str, Any] | None = None) -> tuple[str, str | None]:
    payload = payload or {}
    one_cfg = config_value("opennebula", {})
    one_user = payload.get("one_user") or one_cfg.get("user") or "oneadmin"
    one_password = payload.get("one_password") or one_cfg.get("password")
    return one_user, one_password


@app.get("/health")
def health():
    return jsonify({"status": "ok", "config": str(CONFIG_PATH)})


@app.get("/vms")
def list_vms():
    one_user, one_password = resolve_one_credentials()
    command = build_shell_command("/usr/bin/onevm list --csv", one_user, one_password)
    result = run_shell(command)

    output = result.stdout.strip()
    lines = [line for line in output.splitlines() if line.strip()]
    parsed: list[Any] = lines

    if lines:
        header = lines[0].lower()
        if "," in lines[0] and "id" in header and "name" in header:
            reader = csv.DictReader(io.StringIO(output), skipinitialspace=True)
            parsed = []
            for row in reader:
                parsed.append(
                    {
                        "id": row.get("ID"),
                        "user": row.get("USER"),
                        "name": row.get("NAME"),
                        "state": row.get("STAT"),
                        "cpu": row.get("CPU"),
                        "memory": row.get("MEM"),
                        "host": row.get("HOST"),
                        "time": row.get("TIME"),
                    }
                )

    return jsonify({"items": parsed, "command": command, "opennebula_user": one_user})


@app.post("/vms")
def create_vm():
    payload = request.get_json(silent=True) or {}
    template_name = payload.get("template_name") or payload.get("template_id")
    name = payload.get("name")

    if template_name is None:
        raise ApiError("missing json field: template_name")
    if not name:
        raise ApiError("missing json field: name")

    one_user, one_password = resolve_one_credentials(payload)
    base_command = f"/usr/bin/onetemplate instantiate {shlex.quote(str(template_name))} --name {shlex.quote(str(name))} "
    command = build_shell_command(base_command, one_user, one_password)
    result = run_shell(command)

    return jsonify(
        {
            "status": "created",
            "name": name,
            "template_name": template_name,
            "opennebula_user": one_user,
            "stdout": result.stdout.strip(),
            "command": command,
        }
    ), 201


@app.delete("/vms/<vm_id>")
def delete_vm(vm_id: str):
    payload = request.get_json(silent=True) or {}
    one_user, one_password = resolve_one_credentials(payload)
    vm_ref = payload.get("vm_name") or vm_id
    base_command = f"/usr/bin/onevm terminate {shlex.quote(str(vm_ref))} --hard"
    command = build_shell_command(base_command, one_user, one_password)
    result = run_shell(command)

    return jsonify(
        {
            "status": "deleted",
            "vm_id": vm_id,
            "vm_ref": vm_ref,
            "opennebula_user": one_user,
            "stdout": result.stdout.strip(),
            "command": command,
        }
    )


if __name__ == "__main__":
    host = os.environ.get("NEBULA_CLAW_DEVELOPER_RESTRICTED_API_HOST", "127.0.0.1")
    port = int(os.environ.get("NEBULA_CLAW_DEVELOPER_RESTRICTED_API_PORT", "8080"))
    app.run(host=host, port=port)
