#!/usr/bin/env python3
import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config.json"
CONFIG_PATH = Path(os.environ.get("RESTRICTED_API_CONFIG", DEFAULT_CONFIG_PATH))

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


def build_command(template: str, values: dict[str, Any]) -> str:
    cmd = template
    for key, value in values.items():
        cmd = cmd.replace("{" + key + "}", shlex.quote(str(value)))
    return cmd


def run_shell(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        check=True,
    )


def command_for(name: str) -> str:
    commands = CONFIG.get("commands", {})
    if name not in commands:
        raise ApiError(f"missing configured command for '{name}'", 500)
    return commands[name]


@app.get("/health")
def health():
    return jsonify({"status": "ok", "config": str(CONFIG_PATH)})


@app.get("/vms")
def list_vms():
    user = request.args.get("user")

    template = command_for("list_vms")
    command = build_command(template, {"user": user or ""})
    result = run_shell(command)

    output = result.stdout.strip()
    lines = [line for line in output.splitlines() if line.strip()]
    parsed = lines

    if lines:
        header = lines[0].lower()
        if "," in lines[0] and "id" in header and "name" in header:
            import csv
            import io

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

    return jsonify({"user": user, "items": parsed, "command": command})


@app.post("/vms")
def create_vm():
    payload = request.get_json(silent=True) or {}
    template_id = payload.get("template_id")
    name = payload.get("name")
    user = payload.get("user")

    if template_id is None:
        raise ApiError("missing json field: template_id")
    if not name:
        raise ApiError("missing json field: name")
    if not user:
        raise ApiError("missing json field: user")

    template = command_for("create_vm")
    command = build_command(
        template,
        {"template_id": template_id, "name": name, "user": user},
    )
    result = run_shell(command)

    return jsonify(
        {
            "status": "created",
            "user": user,
            "name": name,
            "template_id": template_id,
            "stdout": result.stdout.strip(),
            "command": command,
        }
    ), 201


@app.delete("/vms/<vm_id>")
def delete_vm(vm_id: str):
    payload = request.get_json(silent=True) or {}
    user = payload.get("user") or request.args.get("user")
    if not user:
        raise ApiError("missing user in query string or json body")

    template = command_for("delete_vm")
    command = build_command(template, {"vm_id": vm_id, "user": user})
    result = run_shell(command)

    return jsonify(
        {
            "status": "deleted",
            "vm_id": vm_id,
            "user": user,
            "stdout": result.stdout.strip(),
            "command": command,
        }
    )


if __name__ == "__main__":
    host = os.environ.get("RESTRICTED_API_HOST", "127.0.0.1")
    port = int(os.environ.get("RESTRICTED_API_PORT", "8080"))
    app.run(host=host, port=port)
