#!/usr/bin/env python3
"""Validate repository-bug-audit evidence JSON and its paired Markdown report."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references" / "bug-audit-evidence.schema.json"
EXPECTED_WEIGHTS = {
    "correctness": 30,
    "security": 25,
    "performance_operability": 15,
    "testing": 10,
    "architecture": 10,
    "readability": 5,
    "dead_code": 5,
}
CATEGORY_DIMENSION = {
    "correctness": "correctness",
    "security": "security",
    "testing": "testing",
    "architecture": "architecture",
    "readability": "readability",
    "dead-code": "dead_code",
    "performance": "performance_operability",
    "operability": "performance_operability",
}
TYPE_RANK = {"defect": 0, "risk": 1, "quality-debt": 2}
SEVERITY_RANK = {"🔴 High": 3, "🟡 Medium": 2, "🟢 Low": 1}
RUNTIME_FINDING_TYPES = {"defect", "risk"}


def _type_matches(value: Any, expected: str) -> bool:
    """Match a Python value using JSON Schema type semantics."""
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def _resolve_ref(root_schema: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise ValueError(f"unsupported schema reference: {reference}")
    node: Any = root_schema
    for part in reference[2:].split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


# ponytail: 自製 JSON Schema 子集求值器，換取零第三方依賴（skill 的可移植承諾）。
# 僅覆蓋 schema 實際使用的關鍵字（type/enum/const/required/properties/additionalProperties/
# minItems/maxItems/items/minLength/pattern/minimum/maximum/$ref）。若
# bug-audit-evidence.schema.json 引入新關鍵字（如 oneOf/anyOf/dependencies），
# 需在此同步擴充，並在 tests 補對應用例。
def validate_schema(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any] | None = None,
    path: str = "$",
) -> list[str]:
    """Validate the JSON Schema subset required by this skill."""
    root_schema = root_schema or schema
    if "$ref" in schema:
        return validate_schema(value, _resolve_ref(root_schema, schema["$ref"]), root_schema, path)

    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_type_matches(value, candidate) for candidate in expected_types):
            return [f"{path}: expected type {expected_type!r}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} is not in the allowed enum")

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}: unexpected property {key!r}")
        for key, child in properties.items():
            if key in value:
                errors.extend(validate_schema(value[key], child, root_schema, f"{path}.{key}"))

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: expected at least {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: expected no more than {schema['maxItems']} items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                errors.extend(validate_schema(item, item_schema, root_schema, f"{path}[{index}]"))

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string is shorter than {schema['minLength']}")
        pattern = schema.get("pattern")
        if pattern and re.fullmatch(pattern, value) is None:
            errors.append(f"{path}: value does not match pattern {pattern!r}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: value is below minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: value is above maximum {schema['maximum']}")
    return errors


def select_artifact_paths(directory: Path, mode: str, now: datetime | None = None) -> tuple[Path, Path]:
    """Select paired artifact paths without overwriting existing files."""
    base = "repository-bug-audit-rapid-report" if mode == "rapid" else "repository-bug-audit-report"
    report = directory / f"{base}.md"
    evidence = directory / f"{base}.evidence.json"
    if not report.exists() and not evidence.exists():
        return report, evidence
    timestamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    return directory / f"{base}-{timestamp}.md", directory / f"{base}-{timestamp}.evidence.json"


def _round_half_up(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _is_confirmed(finding: dict[str, Any]) -> bool:
    return finding["status"] in {"confirmed", "cross-confirmed"} and finding["confidence"] >= 7


def _is_runtime_finding(finding: dict[str, Any]) -> bool:
    return finding["finding_type"] in RUNTIME_FINDING_TYPES


def _finding_sort_key(finding: dict[str, Any]) -> tuple[int, int, int, str]:
    return (
        TYPE_RANK[finding["finding_type"]],
        -SEVERITY_RANK[finding["severity"]],
        -finding["confidence"],
        finding["finding_id"],
    )


def _rating_for_score(score: int) -> str:
    if score >= 90:
        return "Strong engineering quality"
    if score >= 75:
        return "Generally good"
    if score >= 60:
        return "Material technical debt"
    if score >= 40:
        return "Elevated engineering risk"
    return "Major engineering risk"


def _safe_inventory_path(raw_path: str) -> bool:
    normalized = raw_path.replace("\\", "/")
    return not (
        PureWindowsPath(raw_path).is_absolute()
        or PurePosixPath(normalized).is_absolute()
        or ".." in PurePosixPath(normalized).parts
    )


def _resolve_repo_path(repo_root: Path, raw_path: str) -> Path:
    """Resolve a repository-relative evidence path, accepting either slash style."""
    return repo_root / PurePosixPath(raw_path.replace("\\", "/"))


def _location_candidates(raw_location: str) -> list[str]:
    """Return the file paths a finding location may name, or nothing when it names none.

    Locations are normally `path` or `path:line`, but `path:symbol` and `path:line-line`
    also appear. Trying the string both with and without its trailing `:segment` keeps the
    check lenient: a free-form location simply yields no candidate and is not checked.
    """
    candidate = raw_location.strip()
    if not candidate or any(character.isspace() for character in candidate):
        return []
    candidates = [candidate]
    if ":" in candidate:
        candidates.append(candidate.rsplit(":", 1)[0])
    return [item for item in candidates if item and ("/" in item or "\\" in item or "." in item)]


def _validate_paths_exist(data: dict[str, Any], repo_root: Path) -> list[str]:
    """Check that recorded paths name files that actually exist in the audited tree.

    The validator proves structure, not truth, but a path that no file backs is one
    fabrication it can catch outright. When the tree is not co-located with the report —
    a sandbox that only received the artifacts — nothing resolves and there is no basis
    for the check, so it reports that once instead of failing every path.
    """
    if not repo_root.is_dir():
        return []
    inventory = data["inventory"]
    missing_inventory = [
        (index, item)
        for index, item in enumerate(inventory)
        if not _resolve_repo_path(repo_root, item["path"]).exists()
    ]
    if inventory and len(missing_inventory) == len(inventory):
        return [
            f"artifact: no inventory path resolves under {repo_root}; either the paths are "
            "unbacked or the audited tree is elsewhere, in which case pass --repo-root"
        ]

    errors = [
        f"$.inventory[{index}].path: {item['path']!r} does not exist in the audited tree"
        for index, item in missing_inventory
    ]
    for index, finding in enumerate(data["findings"]):
        candidates = _location_candidates(finding["location"])
        if candidates and not any(_resolve_repo_path(repo_root, item).exists() for item in candidates):
            errors.append(
                f"$.findings[{index}].location: {finding['location']!r} does not exist in the audited tree"
            )
    return errors


def validate_evidence(
    data: dict[str, Any],
    evidence_path: Path,
    report_path: Path,
    repo_root: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    mode = data["audit_mode"]

    try:
        datetime.fromisoformat(data["generated_at"].replace("Z", "+00:00"))
    except ValueError:
        errors.append("$.generated_at: expected an ISO 8601 date-time")

    expected_base = "repository-bug-audit-rapid-report" if mode == "rapid" else "repository-bug-audit-report"
    report_pattern = rf"^{re.escape(expected_base)}(?:-\d{{8}}-\d{{6}})?\.md$"
    if re.fullmatch(report_pattern, report_path.name) is None:
        errors.append(f"artifact: report filename does not match {mode} naming policy")
    expected_evidence_name = f"{report_path.stem}.evidence.json"
    if evidence_path.name != expected_evidence_name:
        errors.append("artifact: evidence filename must use the report basename plus .evidence.json")
    if Path(data["artifacts"]["report"]).name != report_path.name:
        errors.append("$.artifacts.report: does not match the validated report filename")
    if Path(data["artifacts"]["evidence"]).name != evidence_path.name:
        errors.append("$.artifacts.evidence: does not match the validated evidence filename")
    if report_path.parent.name != ".docs":
        errors.append("artifact: report must live in the repository .docs directory")
    if evidence_path.parent.name != ".docs":
        errors.append("artifact: evidence must live in the repository .docs directory")

    inventory = data["inventory"]
    normalized_paths: set[str] = set()
    counts = {status: 0 for status in ("read", "mapped", "excluded", "unreadable")}
    # In Comprehensive mode a mapped item is a file the audit owed a read and did not deliver,
    # so it has to say why; in Rapid mode mapping is the declared review boundary.
    reason_required = {"excluded", "unreadable"} | ({"mapped"} if mode == "comprehensive" else set())
    for index, item in enumerate(inventory):
        normalized = item["path"].replace("\\", "/").casefold()
        if normalized in normalized_paths:
            errors.append(f"$.inventory[{index}].path: duplicate normalized path")
        normalized_paths.add(normalized)
        if not _safe_inventory_path(item["path"]):
            errors.append(f"$.inventory[{index}].path: inventory paths must be repository-relative")
        counts[item["status"]] += 1
        if item["status"] in reason_required and not item.get("reason"):
            errors.append(f"$.inventory[{index}].reason: required for {item['status']} items")

    errors.extend(_validate_paths_exist(data, repo_root or report_path.resolve().parent.parent))

    coverage = data["coverage"]
    calculated_in_scope = counts["read"] + counts["mapped"] + counts["unreadable"]
    calculated_percentage = round((counts["read"] / calculated_in_scope) * 100, 2) if calculated_in_scope else 0.0
    expected_counts = {
        "discovered_files": len(inventory),
        "in_scope_files": calculated_in_scope,
        "read_files": counts["read"],
        "mapped_files": counts["mapped"],
        "unreadable_files": counts["unreadable"],
        "excluded_files": counts["excluded"],
    }
    for key, expected in expected_counts.items():
        if coverage[key] != expected:
            errors.append(f"$.coverage.{key}: expected {expected} from inventory, got {coverage[key]}")
    if abs(float(coverage["percentage"]) - calculated_percentage) > 0.01:
        errors.append(f"$.coverage.percentage: expected {calculated_percentage:.2f} from inventory")

    ids: set[str] = set()
    fingerprints: set[str] = set()
    findings = data["findings"]
    for index, finding in enumerate(findings):
        prefix = f"$.findings[{index}]"
        finding_id = finding["finding_id"]
        fingerprint = finding["fingerprint"]
        if finding_id in ids:
            errors.append(f"{prefix}.finding_id: duplicate ID")
        ids.add(finding_id)
        if fingerprint in fingerprints:
            errors.append(f"{prefix}.fingerprint: duplicate root-cause fingerprint")
        fingerprints.add(fingerprint)

        confidence = finding["confidence"]
        if confidence <= 2:
            errors.append(f"{prefix}.confidence: confidence 1–2 candidates must be discarded")
        if confidence <= 6 and finding["status"] != "needs-verification":
            errors.append(f"{prefix}.status: confidence below 7 requires needs-verification")
        if finding["severity"] == "🔴 High" and confidence < 7 and finding["status"] != "needs-verification":
            errors.append(f"{prefix}.status: unconfirmed potential High must need verification")

        finding_type = finding["finding_type"]
        if finding_type == "defect":
            if not finding.get("expected_behavior", "").strip():
                errors.append(f"{prefix}.expected_behavior: defect requires a non-empty expected behavior")
            if not finding.get("actual_behavior", "").strip():
                errors.append(f"{prefix}.actual_behavior: defect requires a non-empty actual behavior")
            if finding["evidence_kind"] not in {"observed", "reproduced"}:
                errors.append(f"{prefix}.evidence_kind: defect requires observed or reproduced evidence")
            if confidence < 7:
                errors.append(f"{prefix}.confidence: defect requires confidence of at least 7")
            if finding["status"] not in {"confirmed", "cross-confirmed"}:
                errors.append(f"{prefix}.status: defect must be confirmed or cross-confirmed")
        elif finding_type == "risk" and not finding["preconditions"].strip():
            errors.append(f"{prefix}.preconditions: risk requires non-empty preconditions")
        elif finding_type == "quality-debt" and mode == "rapid":
            errors.append(f"{prefix}.finding_type: quality-debt is forbidden in Rapid mode")

        unique_agents = {agent.casefold() for agent in finding["source_agents"]}
        if finding["status"] == "cross-confirmed" and len(unique_agents) < 2:
            errors.append(f"{prefix}.source_agents: cross-confirmed requires two independent agents")

    finding_id_set = {finding["finding_id"] for finding in findings}
    confirmed = [finding for finding in findings if _is_confirmed(finding)]
    confirmed_runtime = [finding for finding in confirmed if _is_runtime_finding(finding)]
    confirmed_high = [finding for finding in confirmed_runtime if finding["severity"] == "🔴 High"]
    confirmed_medium = [finding for finding in confirmed_runtime if finding["severity"] == "🟡 Medium"]
    public_material_runtime = [
        finding
        for finding in findings
        if _is_runtime_finding(finding)
        and finding["confidence"] >= 5
        and finding["severity"] in {"🔴 High", "🟡 Medium"}
    ]
    risk = data["assessment"]["risk"]
    confidence = data["assessment"]["confidence"]
    all_flows_traced = all(flow["status"] == "traced" for flow in data["core_flows"])

    if confirmed_high and risk != "High":
        errors.append("$.assessment.risk: a confirmed High defect/risk requires High risk")
    if confirmed_medium and risk == "Low":
        errors.append("$.assessment.risk: a confirmed Medium defect/risk forbids Low risk")
    if public_material_runtime and risk == "Low":
        errors.append("$.assessment.risk: a public High/Medium defect/risk forbids Low risk")
    if risk == "High" and not confirmed_high and len(confirmed_medium) < 2:
        errors.append("$.assessment.risk: High requires a confirmed High or at least two confirmed Medium defect/risk findings")
    if risk == "Low" and not all_flows_traced:
        errors.append("$.assessment.risk: Low requires every recorded core/high-risk flow to be traced")

    if mode == "rapid":
        for forbidden in ("dimensions", "total_score", "rating"):
            if forbidden in data:
                errors.append(f"$.{forbidden}: forbidden in Rapid mode")
        if confidence == "High":
            errors.append("$.assessment.confidence: Rapid confidence cannot be High")
        if data["execution"]["provisional"] and confidence != "Low":
            errors.append("$.assessment.confidence: a provisional Rapid audit must have Low confidence")
        if confidence == "Medium" and not all_flows_traced:
            errors.append("$.assessment.confidence: Medium Rapid confidence requires traced selected flows")
    else:
        if counts["mapped"] and not data["execution"]["provisional"]:
            errors.append(
                "$.inventory: a non-provisional Comprehensive audit cannot leave in-scope items mapped"
            )
        if "dimensions" not in data or "total_score" not in data or "rating" not in data:
            errors.append("$: Comprehensive mode requires dimensions, total_score, and rating")
        else:
            errors.extend(_validate_dimensions(data, finding_id_set, confirmed))
        if confidence == "High":
            any_passed = any(check["status"] == "passed" for check in data["verification_checks"])
            if coverage["percentage"] != 100 or not all_flows_traced or data["execution"]["provisional"] or not any_passed:
                errors.append("$.assessment.confidence: High requires 100% coverage, traced flows, non-provisional status, and a passed verification")
        if confidence == "Medium" and (coverage["percentage"] < 90 or not all_flows_traced):
            errors.append("$.assessment.confidence: Medium requires at least 90% coverage and traced flows")
    return errors


def _validate_dimensions(
    data: dict[str, Any],
    finding_ids: set[str],
    confirmed_findings: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    dimensions = data["dimensions"]
    by_id = {dimension["id"]: dimension for dimension in dimensions}
    if len(by_id) != len(dimensions):
        errors.append("$.dimensions: duplicate dimension IDs")
    if set(by_id) != set(EXPECTED_WEIGHTS):
        errors.append("$.dimensions: all seven canonical dimensions are required")
        return errors

    for dimension_id, expected_weight in EXPECTED_WEIGHTS.items():
        dimension = by_id[dimension_id]
        if dimension["weight"] != expected_weight:
            errors.append(f"$.dimensions.{dimension_id}.weight: expected {expected_weight}")
        unknown_ids = set(dimension["finding_ids"]) - finding_ids
        if unknown_ids:
            errors.append(f"$.dimensions.{dimension_id}.finding_ids: unknown IDs {sorted(unknown_ids)}")
        if dimension["level"] is None:
            if dimension["score"] is not None or not dimension.get("na_reason"):
                errors.append(f"$.dimensions.{dimension_id}: N/A requires null score and na_reason")
        else:
            expected_score = expected_weight * dimension["level"] / 5
            if dimension["score"] is None or abs(float(dimension["score"]) - expected_score) > 0.001:
                errors.append(f"$.dimensions.{dimension_id}.score: expected {expected_score:g}")
            if "na_reason" in dimension:
                errors.append(f"$.dimensions.{dimension_id}.na_reason: allowed only for N/A")

    for dimension_id, dimension in by_id.items():
        if dimension["level"] is None:
            continue
        highs = [
            finding
            for finding in confirmed_findings
            if finding["severity"] == "🔴 High" and CATEGORY_DIMENSION[finding["category"]] == dimension_id
        ]
        mediums = [
            finding
            for finding in confirmed_findings
            if finding["severity"] == "🟡 Medium" and CATEGORY_DIMENSION[finding["category"]] == dimension_id
        ]
        if len(highs) >= 2 and dimension["level"] > 1:
            errors.append(f"$.dimensions.{dimension_id}.level: multiple confirmed High findings cap level at 1")
        elif highs and dimension["level"] > 2:
            errors.append(f"$.dimensions.{dimension_id}.level: a confirmed High finding caps level at 2")
        if mediums and dimension["level"] > 3:
            errors.append(f"$.dimensions.{dimension_id}.level: a confirmed Medium finding caps level at 3")

    for finding in data["findings"]:
        if finding["confidence"] < 5:
            continue
        expected_dimension = CATEGORY_DIMENSION[finding["category"]]
        assigned_dimensions = [
            dimension_id
            for dimension_id, dimension in by_id.items()
            if finding["finding_id"] in dimension["finding_ids"]
        ]
        if assigned_dimensions != [expected_dimension]:
            errors.append(f"$.dimensions: finding {finding['finding_id']} must be assigned only to {expected_dimension}")

    applicable = [dimension for dimension in dimensions if dimension["level"] is not None]
    applicable_weight = sum(dimension["weight"] for dimension in applicable)
    if applicable_weight == 0:
        errors.append("$.dimensions: at least one dimension must be applicable")
        return errors
    weighted_score = sum(Decimal(str(dimension["score"])) for dimension in applicable)
    expected_total = _round_half_up(Decimal(100) * weighted_score / Decimal(applicable_weight))
    if data["total_score"] != expected_total:
        errors.append(f"$.total_score: expected {expected_total}, got {data['total_score']}")
    expected_rating = _rating_for_score(expected_total)
    if data["rating"] != expected_rating:
        errors.append(f"$.rating: expected {expected_rating!r}")
    return errors


def _local_link_target(raw_target: str, report_path: Path) -> Path | None:
    target = raw_target.strip().strip("<>")
    if not target or target.startswith(("#", "http://", "https://", "mailto:")):
        return None
    target = target.split("#", 1)[0]
    candidate = Path(target)
    if not candidate.is_absolute():
        candidate = report_path.parent / candidate
    if candidate.exists():
        return candidate
    line_match = re.match(r"^(.*):\d+$", str(candidate))
    return Path(line_match.group(1)) if line_match else candidate


def validate_report(text: str, data: dict[str, Any], report_path: Path) -> list[str]:
    errors: list[str] = []
    mode = data["audit_mode"]
    expected_title = "# Repository Bug Audit — Rapid" if mode == "rapid" else "# Repository Bug Audit"
    if not text.startswith(expected_title):
        errors.append(f"report: expected title {expected_title!r}")

    expected_sections = (
        [
            "1. Executive Summary",
            "2. Review Coverage and Bug Surfaces",
            "3. Prioritized Findings",
            "4. Limitations",
        ]
        if mode == "rapid"
        else [
            "1. Executive Summary",
            "2. Risk-Weighted Quality Scores",
            "3. Prioritized Findings",
            "4. Limitations",
        ]
    )
    actual_sections = re.findall(r"^## (.+)$", text, flags=re.MULTILINE)
    if actual_sections != expected_sections:
        errors.append(f"report: expected exactly four sections {expected_sections!r}")

    provisional_marker = "**Provisional report**"
    if data["execution"]["provisional"] != (provisional_marker in text):
        errors.append("report: provisional marker must match execution.provisional")
    if mode == "rapid" and "| Total score |" in text:
        errors.append("report: Rapid report must not include Total score")
    if mode == "comprehensive" and "| Total score |" not in text:
        errors.append("report: Comprehensive executive summary must include Total score")

    public_findings = sorted(
        [finding for finding in data["findings"] if finding["confidence"] >= 5],
        key=_finding_sort_key,
    )
    internal_findings = [finding for finding in data["findings"] if finding["confidence"] <= 4]
    findings_section_match = re.search(
        r"^## 3\. Prioritized Findings\s*$([\s\S]*?)(?=^## 4\. Limitations\s*$)",
        text,
        flags=re.MULTILINE,
    )
    findings_section = findings_section_match.group(1) if findings_section_match else ""
    table_pairs = re.findall(
        r"^\|\s*([A-Z][A-Z0-9_-]*-[0-9]{3})\s*\|\s*(defect|risk|quality-debt)\s*\|",
        findings_section,
        flags=re.MULTILINE,
    )
    detail_ids = set(re.findall(r"^### ([A-Z][A-Z0-9_-]*-[0-9]{3}):", text, flags=re.MULTILINE))
    expected_pairs = [(finding["finding_id"], finding["finding_type"]) for finding in public_findings]
    empty_message = "No reportable findings were identified within the reviewed scope."

    if public_findings:
        canonical_header = "| ID | Type | Severity / confidence | Location | Problem and impact | Recommendation |"
        if canonical_header not in findings_section:
            errors.append("report: public findings require the canonical findings table")
        if table_pairs != expected_pairs:
            errors.append("report: findings table rows must exactly match public evidence findings in canonical order")
        if empty_message in findings_section:
            errors.append("report: non-empty findings must not use the empty-findings message")
    elif empty_message not in findings_section:
        errors.append("report: empty public findings require the canonical empty-findings message")

    expected_public_ids = {finding["finding_id"] for finding in public_findings}
    for finding in public_findings:
        finding_id = finding["finding_id"]
        needs_detail = SEVERITY_RANK[finding["severity"]] >= SEVERITY_RANK["🟡 Medium"]
        if needs_detail and finding_id not in detail_ids:
            errors.append(f"report: High/Medium finding {finding_id} requires a detail heading")
        if needs_detail and finding_id in detail_ids:
            block_match = re.search(
                rf"^### {re.escape(finding_id)}:.*?$([\s\S]*?)(?=^### [A-Z][A-Z0-9_-]*-[0-9]{{3}}:|^## 4\.|\Z)",
                text,
                flags=re.MULTILINE,
            )
            block = block_match.group(1) if block_match else ""
            for label in ("Location", "Evidence", "Impact", "Recommendation", "Verification"):
                if f"**{label}:**" not in block:
                    errors.append(f"report: detail block {finding_id} is missing {label}")
        if not needs_detail and finding_id in detail_ids:
            errors.append(f"report: Low finding {finding_id} must not have a detail block")
    for finding in internal_findings:
        if finding["finding_id"] in text:
            errors.append(f"report: internal low-confidence candidate {finding['finding_id']} must not be public")
    for detail_id in detail_ids - expected_public_ids:
        errors.append(f"report: detail heading {detail_id} has no public evidence finding")

    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        candidate = _local_link_target(match.group(1), report_path)
        if candidate is not None and not candidate.exists():
            errors.append(f"report: broken local link {match.group(1)!r}")
    return errors


def run_validation(evidence_path: Path, report_path: Path, repo_root: Path | None = None) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    data = json.loads(evidence_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    schema_errors = validate_schema(data, schema)
    if schema_errors:
        return schema_errors
    return validate_evidence(data, evidence_path, report_path, repo_root) + validate_report(
        report, data, report_path
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a repository-bug-audit artifact pair.")
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Root of the audited tree; defaults to the report's parent directory (the .docs parent).",
    )
    args = parser.parse_args(argv)
    try:
        errors = run_validation(args.evidence, args.report, args.repo_root)
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"Unable to validate bug-audit artifacts: {exc}", file=sys.stderr)
        return 2
    if errors:
        print(f"Bug-audit validation failed with {len(errors)} violation(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Bug-audit artifacts are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
