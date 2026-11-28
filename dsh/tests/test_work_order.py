#!/usr/bin/env python3
"""Work-order contract test (spec §4.6).

Validates the shipped template as a *valid default work order* and asserts the
fields that keep the contract compatible with Team-off hosts:
index is Lead-only, team is optional/off, confirmed is human-only, and every
deliverable starts as draft.

Run standalone or as selfcheck section 7:
    python dsh/tests/test_work_order.py
"""

from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE = ROOT / "templates" / "agent-work-order.yaml"

failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        failures.append(f"{name}{(': ' + detail) if detail else ''}")


def main() -> int:
    data = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
    check("top-level mapping", isinstance(data, dict))
    if not isinstance(data, dict):
        print("FAIL:", "; ".join(failures))
        return 1

    check("schema_version", data.get("schema_version") == 1)
    check("role", data.get("role") in {"scout", "worker", "judge", "reconciler"})
    check("phase", data.get("phase") in {0, 1, 2, 2.5, 3})
    check("id", isinstance(data.get("id"), str) and data["id"].startswith("WO-"))

    scope = data.get("scope") or {}
    check("scope.kind", scope.get("kind") in {"module", "hypothesis", "file-set", "global-readonly"})
    check("scope.write_scopes", isinstance(scope.get("write_scopes"), list) and bool(scope["write_scopes"]))
    check("scope.module_revision", isinstance(scope.get("module_revision"), int))

    inputs = data.get("inputs") or {}
    check("inputs.contract_ref", isinstance(inputs.get("contract_ref"), str) and inputs["contract_ref"])

    deliverables = data.get("deliverables") or {}
    check("deliverables.index_update is False", deliverables.get("index_update") is False)
    artifacts = deliverables.get("artifacts") or []
    check("deliverables.artifacts non-empty", bool(artifacts))
    for item in artifacts:
        check("artifact.status", item.get("status") in {"draft", "candidate"})
        check("artifact.path", isinstance(item.get("path"), str) and item["path"])
        check("artifact.required_fields", isinstance(item.get("required_fields"), list))

    acceptance = data.get("acceptance") or {}
    check("acceptance.criteria list", isinstance(acceptance.get("criteria"), list))
    check("acceptance.requires_judge bool", isinstance(acceptance.get("requires_judge"), bool))

    stop = data.get("stop") or {}
    check("stop.retry_cap", stop.get("retry_cap") == 3)
    check("stop.evidence_saturation", stop.get("evidence_saturation") is True)

    authority = data.get("authority") or {}
    check("authority.confirmed_by human-only", authority.get("confirmed_by") == "human-only")

    producer = data.get("producer") or {}
    for field in ("dsh_name", "session_id", "preset"):
        check(f"producer.{field}", field in producer)
    name = producer.get("dsh_name") or ""
    check("producer.dsh_name role prefix", name.startswith(str(data.get("role")) + "-"), name)

    team = data.get("team") or {}
    check("team.enabled default False", team.get("enabled") is False)
    check("team.task_id default None", team.get("task_id") is None)
    check("team.blocked_by list", isinstance(team.get("blocked_by"), list))

    if failures:
        print(f"FAIL ({len(failures)}):")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("OK: work-order contract template is valid (Team-off compatible)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
