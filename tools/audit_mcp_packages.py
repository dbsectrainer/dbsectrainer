#!/usr/bin/env python3
"""Audit the six published MCP packages.

Two independent checks:

* ``--metadata`` (default) verifies npm maintainership and the official MCP
  registry listing. This is a discovery check, not a runtime check.
* ``--runtime`` launches each package exactly as the README used to advertise
  (``npx -y <package>``) and performs an MCP initialize + tools/list handshake.
* ``--workaround`` runs the same handshake with ``yargs`` supplied explicitly.
  It documents the current npm tarball defect without changing the packages.

The runtime probes need Node.js and network access. They are not part of
``make check`` because they exercise third-party packages.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "tools" / "mcp_packages.json"
RESULTS_DIR = ROOT / "docs" / "evidence" / "test-results"
USER_AGENT = "dbsectrainer-mcp-audit/1.0"
NPM_CACHE = "/tmp/dbsectrainer-npm-cache"
AUDIT_HOME = "/tmp/dbsectrainer-mcp-home"
AUDIT_CWD = "/tmp/dbsectrainer-mcp-audit"


def load_packages() -> list[dict]:
    return json.loads(CONFIG.read_text(encoding="utf-8"))["packages"]


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def metadata_audit(packages: list[dict]) -> tuple[list[dict], list[str]]:
    observations = []
    problems = []
    for package in packages:
        name = package["name"]
        observation = {"name": name, "repo": package["repo"]}
        try:
            npm = fetch_json(f"https://registry.npmjs.org/{urllib.parse.quote(name)}")
            latest = npm.get("dist-tags", {}).get("latest")
            maintainers = sorted({m.get("name") for m in npm.get("maintainers", [])})
            observation["npm"] = {
                "latest": latest,
                "maintainers": maintainers,
                "versions": len(npm.get("versions", {})),
            }
            if not latest:
                problems.append(f"{name}: no npm latest version")
            if "dbsectrainer" not in maintainers:
                problems.append(f"{name}: dbsectrainer is not an npm maintainer")
        except Exception as exc:  # noqa: BLE001
            observation["npm"] = {"error": str(exc)}
            problems.append(f"{name}: npm lookup failed: {exc}")

        try:
            registry = fetch_json(
                "https://registry.modelcontextprotocol.io/v0/servers?"
                f"search={urllib.parse.quote(name)}&limit=10"
            )
            servers = [entry.get("server", {}) for entry in registry.get("servers", [])]
            names = [server.get("name") for server in servers]
            registry_id = package["registry_id"]
            match = next((server for server in servers if server.get("name") == registry_id), None)
            observation["mcp_registry"] = {
                "names": names,
                "match": match is not None,
                "version": (match or {}).get("version"),
                "packages": [
                    p.get("identifier") for p in (match or {}).get("packages", [])
                ],
            }
            if match is None:
                problems.append(f"{name}: {registry_id} not found in the official MCP registry")
        except Exception as exc:  # noqa: BLE001
            observation["mcp_registry"] = {"error": str(exc)}
            problems.append(f"{name}: MCP registry lookup failed: {exc}")
        observations.append(observation)
    return observations, problems


def probe(package: dict, use_yargs: bool) -> dict:
    name = package["name"]
    os.makedirs(NPM_CACHE, exist_ok=True)
    os.makedirs(AUDIT_HOME, exist_ok=True)
    os.makedirs(AUDIT_CWD, exist_ok=True)
    env = os.environ.copy()
    env["npm_config_cache"] = NPM_CACHE
    env["NO_COLOR"] = "1"
    env["HOME"] = AUDIT_HOME
    env["npm_config_update_notifier"] = "false"

    command = ["npx", "-y", "--no-fund", "--no-audit"]
    if use_yargs:
        command += ["-p", name, "-p", "yargs", name]
    else:
        command += [name]
    command += package.get("runtime_args", [])

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=AUDIT_CWD,
        env=env,
        text=True,
        bufsize=1,
        start_new_session=True,
    )
    output: list[tuple[str, str]] = []

    def read(stream, tag):
        for line in iter(stream.readline, ""):
            output.append((tag, line.rstrip()))
            if len(output) > 600:
                break

    readers = [
        threading.Thread(target=read, args=(process.stdout, "stdout"), daemon=True),
        threading.Thread(target=read, args=(process.stderr, "stderr"), daemon=True),
    ]
    for thread in readers:
        thread.start()

    messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "profile-audit", "version": "1.0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ]
    for message in messages:
        try:
            process.stdin.write(json.dumps(message) + "\n")
            process.stdin.flush()
        except Exception:
            break
        time.sleep(1.3)
    time.sleep(5.5)

    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(os.getpgid(process.pid), sig)
        except Exception:
            pass
        time.sleep(0.4)
    try:
        process.wait(timeout=5)
    except Exception:
        pass

    responses = []
    for tag, line in output:
        if tag == "stdout":
            try:
                responses.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    server = None
    tools = None
    for response in responses:
        if response.get("id") == 1 and "result" in response:
            server = response["result"].get("serverInfo")
        if response.get("id") == 2 and "result" in response:
            tools = [tool.get("name") for tool in response["result"].get("tools", [])]
    stderr = "\n".join(line for tag, line in output if tag == "stderr")
    stderr_lines = stderr.splitlines()
    stderr_tail = "\n".join(stderr_lines[-12:])
    stderr_head = "\n".join(stderr_lines[:8])
    error_line = next(
        (line.strip() for line in stderr_lines if "Cannot find package" in line),
        "",
    )
    if not error_line:
        error_line = next(
            (
                line.strip()
                for line in stderr_lines
                if "ERR_MODULE_NOT_FOUND" in line or line.strip().startswith("Error:")
            ),
            "",
        )
    return {
        "name": name,
        "mode": "workaround-with-yargs" if use_yargs else "published-command",
        "command": " ".join(command),
        "exit_code": process.returncode,
        "initialized": server is not None,
        "server": server,
        "tool_count": len(tools) if tools is not None else None,
        "tools": tools,
        "ok": server is not None and bool(tools),
        "error_line": error_line,
        "stderr_head": stderr_head,
        "stderr_tail": stderr_tail,
    }


def write_result(mode: str, packages: list[dict], observations: list[dict], problems: list[str], probes: list[dict]) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output = RESULTS_DIR / f"mcp-{mode}.json"
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "package_count": len(packages),
        "metadata": observations,
        "metadata_problems": problems,
        "runtime": probes,
        "runtime_passed": sum(1 for probe_result in probes if probe_result["ok"]),
        "runtime_failed": sum(1 for probe_result in probes if not probe_result["ok"]),
        "ok": not problems and all(probe_result["ok"] for probe_result in probes) if probes else not problems,
    }
    output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", action="store_true", help="verify npm and MCP registry listings (default)")
    parser.add_argument("--runtime", action="store_true", help="probe the published npx command")
    parser.add_argument("--workaround", action="store_true", help="probe with yargs supplied explicitly")
    args = parser.parse_args()

    packages = load_packages()
    observations, problems = metadata_audit(packages)

    print("Package metadata")
    print("=" * 72)
    for observation in observations:
        npm = observation.get("npm", {})
        registry = observation.get("mcp_registry", {})
        print(
            f"{observation['name']}: npm {npm.get('latest', '?')} "
            f"maintainers={','.join(npm.get('maintainers', [])) or '?'}; "
            f"registry_match={registry.get('match')} version={registry.get('version')}"
        )
    if problems:
        print("\nMetadata problems:")
        for problem in problems:
            print(f" - {problem}")

    probes: list[dict] = []
    mode = "metadata"
    if args.runtime or args.workaround:
        mode = "runtime" if args.runtime else "workaround"
        print("\nRuntime probes")
        print("=" * 72)
        for package in packages:
            result = probe(package, use_yargs=args.workaround)
            probes.append(result)
            status = "PASS" if result["ok"] else "FAIL"
            print(
                f"[{status}] {result['name']}: exit={result['exit_code']} "
                f"initialized={result['initialized']} tools={result['tool_count']}"
            )
            if not result["ok"]:
                first_line = result.get("error_line") or result["stderr_tail"].splitlines()[0] if result["stderr_tail"] else ""
                if first_line:
                    print(f"        {first_line[:220]}")
        print(
            f"\n{sum(1 for probe_result in probes if probe_result['ok'])}/{len(probes)} "
            "packages completed the MCP handshake"
        )

    output = write_result(mode, packages, observations, problems, probes)
    print(f"\nJSON result: {output.relative_to(ROOT)}")
    return 0 if not problems and all(probe_result["ok"] for probe_result in probes) else 1


if __name__ == "__main__":
    sys.exit(main())
