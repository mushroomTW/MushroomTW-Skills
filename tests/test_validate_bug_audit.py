from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path, PurePosixPath


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_bug_audit.py"
SPEC = importlib.util.spec_from_file_location("validate_bug_audit", MODULE_PATH)
assert SPEC and SPEC.loader
validate_bug_audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_bug_audit)


def rapid_evidence() -> dict:
    return {
        "schema_version": "3.0",
        "audit_mode": "rapid",
        "generated_at": "2026-08-05T12:00:00+08:00",
        "project": {"name": "Example Project", "root": ".", "profile": "library-sdk"},
        "artifacts": {
            "report": "repository-bug-audit-rapid-report.md",
            "evidence": "repository-bug-audit-rapid-report.evidence.json",
        },
        "execution": {"review_mode": "standard", "provisional": False},
        "assessment": {
            "risk": "Low",
            "risk_rationale": "No public High or Medium runtime finding was identified.",
            "confidence": "Medium",
            "confidence_rationale": "The mapped repository and selected flow support the limited conclusion.",
        },
        "coverage": {
            "discovered_files": 2,
            "in_scope_files": 2,
            "read_files": 1,
            "mapped_files": 1,
            "unreadable_files": 0,
            "excluded_files": 0,
            "percentage": 50.0,
            "critical_in_scope_files": 1,
            "critical_read_files": 1,
            "critical_percentage": 100.0,
            "boundary": "Read the public entry point; mapped the low-risk helper.",
        },
        "inventory": [
            {"path": "src\\main.py", "status": "read", "risk_tier": "core"},
            {"path": "src/helper.py", "status": "mapped", "risk_tier": "low"},
        ],
        "core_flows": [
            {
                "name": "Public API",
                "risk_tier": "core",
                "entry_point": "src/main.py:main",
                "status": "traced",
                "evidence": ["Read the entry point and its direct helper call."],
            }
        ],
        "verification_checks": [
            {
                "name": "unit tests",
                "status": "not_run",
                "scope": "repository",
                "evidence": "No configured test command was found.",
            }
        ],
        "findings": [],
        "limitations": ["Lower-risk helper implementation was mapped but not read."],
    }


def comprehensive_evidence() -> dict:
    data = rapid_evidence()
    data.update(
        {
            "audit_mode": "comprehensive",
            "artifacts": {
                "report": "repository-bug-audit-report.md",
                "evidence": "repository-bug-audit-report.evidence.json",
            },
            "assessment": {
                "risk": "Low",
                "risk_rationale": "No public High or Medium runtime finding remains.",
                "confidence": "High",
                "confidence_rationale": "All files and flows were reviewed and tests passed.",
            },
            "coverage": {
                "discovered_files": 2,
                "in_scope_files": 2,
                "read_files": 2,
                "mapped_files": 0,
                "unreadable_files": 0,
                "excluded_files": 0,
                "percentage": 100.0,
                "critical_in_scope_files": 1,
                "critical_read_files": 1,
                "critical_percentage": 100.0,
                "boundary": "All first-party files were read.",
            },
            "inventory": [
                {"path": "src/main.py", "status": "read", "risk_tier": "core"},
                {"path": "src/tool.py", "status": "read", "risk_tier": "standard"},
            ],
            "verification_checks": [
                {
                    "name": "unit tests",
                    "status": "passed",
                    "scope": "repository",
                    "evidence": "The configured suite exited successfully.",
                }
            ],
            "dimensions": [
                {
                    "id": dimension_id,
                    "weight": weight,
                    "level": 4,
                    "score": weight * 4 / 5,
                    "rationale": "Generally sound within the reviewed scope.",
                    "finding_ids": [],
                }
                for dimension_id, weight in validate_bug_audit.EXPECTED_WEIGHTS.items()
            ],
            "total_score": 80,
            "rating": "Generally good",
            "limitations": [],
        }
    )
    return data


def narrowed_comprehensive_evidence() -> dict:
    """A Comprehensive audit that exceeded its read budget, narrowed scope, and disclosed it.

    The unread file lives in the inventory as a `mapped` item with a reason, so coverage
    falls out of the inventory automatically and `limitations` carries the consequence in
    prose rather than a file list.
    """
    data = comprehensive_evidence()
    data["execution"]["provisional"] = True
    data["assessment"]["confidence"] = "Low"
    data["assessment"]["confidence_rationale"] = "One in-scope file was left unread within the budget."
    data["inventory"].append(
        {
            "path": "src/legacy.py",
            "status": "mapped",
            "risk_tier": "low",
            "reason": "Left unread after scope was narrowed to core paths within the execution budget.",
        }
    )
    data["coverage"].update(
        {
            "discovered_files": 3,
            "in_scope_files": 3,
            "read_files": 2,
            "mapped_files": 1,
            "percentage": 66.67,
            "boundary": "Core paths were read; one low-risk file was left mapped.",
        }
    )
    data["limitations"] = ["One low-risk in-scope file was left unread; the inventory records which."]
    return data


def defect_finding(severity: str = "Medium") -> dict:
    return {
        "finding_id": "BUG-001",
        "fingerprint": "correctness|incorrect-result|main",
        "finding_type": "defect",
        "severity": severity,
        "confidence": 8,
        "category": "correctness",
        "location": "src/main.py:1",
        "summary": "The public function returns an incorrect result.",
        "evidence_kind": "observed",
        "evidence": ["The visible return value conflicts with the public contract."],
        "expected_behavior": "Return the documented value.",
        "actual_behavior": "Return a different value.",
        "preconditions": "Call the public function.",
        "affected_surface": "Public API",
        "impact": "Callers receive an incorrect value.",
        "recommendation": "Correct the return path.",
        "verification": "Run the existing regression test.",
        "test_idea": "Assert the documented return value.",
        "source_agents": ["standard-review"],
        "status": "confirmed",
    }


def risk_finding(severity: str = "Medium") -> dict:
    return {
        "finding_id": "RISK-001",
        "fingerprint": "security|missing-boundary-check|load",
        "finding_type": "risk",
        "severity": severity,
        "confidence": 7,
        "category": "security",
        "location": "src/main.py:8",
        "summary": "An external value reaches a sensitive operation without a visible check.",
        "evidence_kind": "observed",
        "evidence": ["The traced path contains no boundary validation."],
        "preconditions": "An untrusted caller controls the external value.",
        "affected_surface": "Public API",
        "impact": "A caller may reach an unsafe operation.",
        "recommendation": "Validate the value at the trust boundary.",
        "verification": "Run the repository security test after adding the boundary control.",
        "source_agents": ["standard-review"],
        "status": "confirmed",
    }


def quality_debt_finding(severity: str = "Medium") -> dict:
    return {
        "finding_id": "DEBT-001",
        "fingerprint": "architecture|shared-global-state|cache",
        "finding_type": "quality-debt",
        "severity": severity,
        "confidence": 8,
        "category": "architecture",
        "location": "src/tool.py:1",
        "summary": "Shared mutable state couples otherwise independent callers.",
        "evidence_kind": "observed",
        "evidence": ["Multiple public paths mutate the same module-level object."],
        "preconditions": "",
        "affected_surface": "Internal architecture",
        "impact": "Changes are harder to isolate and verify.",
        "recommendation": "Move ownership behind an explicit instance boundary.",
        "verification": "Run the existing architecture checks and unit tests.",
        "source_agents": ["standard-review"],
        "status": "confirmed",
    }


def _finding_sort_key(finding: dict) -> tuple[int, int, int, str]:
    type_rank = {"defect": 0, "risk": 1, "quality-debt": 2}
    severity_rank = {"High": 3, "Medium": 2, "Low": 1}
    return (
        type_rank[finding["finding_type"]],
        -severity_rank[finding["severity"]],
        -finding["confidence"],
        finding["finding_id"],
    )


def findings_section(findings: list[dict]) -> str:
    public = sorted((item for item in findings if item["confidence"] >= 5), key=_finding_sort_key)
    if not public:
        return "No reportable findings were identified within the reviewed scope."
    lines = [
        "| ID | Type | Severity / confidence | Location | Problem and impact | Recommendation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in public:
        lines.append(
            f"| {item['finding_id']} | {item['finding_type']} | "
            f"{validate_bug_audit.SEVERITY_LABELS[item['severity']]} / {item['confidence']} | "
            f"{item['location']} | "
            f"{item['summary']} {item['impact']} | {item['recommendation']} |"
        )
    for item in public:
        if item["severity"] == "Low":
            continue
        lines.extend(
            [
                "",
                f"### {item['finding_id']}: {item['summary']}",
                "",
                f"**Location:** {item['location']}",
                "",
                "**Evidence:**",
                "",
                f"- {item['evidence'][0]}",
                "",
                f"**Impact:** {item['impact']}",
                "",
                f"**Recommendation:** {item['recommendation']}",
                "",
                f"**Verification:** {item['verification']}",
            ]
        )
    return "\n".join(lines)


def rapid_report(data: dict | None = None) -> str:
    data = data or rapid_evidence()
    return f"""# Repository Bug Audit — Rapid

## 1. Executive Summary

| Metric | Result |
| --- | --- |
| Risk signal | {data['assessment']['risk']} |
| Assessment confidence | {data['assessment']['confidence']} |
| Review coverage | 1 / 2, 50% |
| Core-path coverage | 1 / 1, 100% |
| Verification summary | Tests not run |

This Rapid audit does not assign a quality score.

## 2. Review Coverage and Bug Surfaces

The public entry point was reviewed and the helper was mapped.

## 3. Prioritized Findings

{findings_section(data['findings'])}

## 4. Limitations

- The lower-risk helper was not read.
"""


def comprehensive_report(data: dict | None = None) -> str:
    data = data or comprehensive_evidence()
    return f"""# Repository Bug Audit

## 1. Executive Summary

| Metric | Result |
| --- | --- |
| Total score | {data['total_score']} — {data['rating']} |
| Overall risk | {data['assessment']['risk']} |
| Assessment confidence | {data['assessment']['confidence']} |
| File coverage | 2 / 2, 100% |
| Core-path coverage | 1 / 1, 100% |
| Verification summary | Unit tests passed |

The project is generally sound within the reviewed scope.

## 2. Risk-Weighted Quality Scores

| Dimension | Weight | Level | Score | Primary rationale |
| --- | ---: | ---: | ---: | --- |
| Correctness | 30 | 4 | 24 | Generally sound. |

## 3. Prioritized Findings

{findings_section(data['findings'])}

## 4. Limitations

None.
"""


class BugAuditValidatorTests(unittest.TestCase):
    def validate_pair(
        self,
        data: dict,
        report: str,
        materialize: bool = True,
        missing: tuple[str, ...] = (),
    ) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / ".docs"
            docs.mkdir()
            if materialize:
                self.materialize_inventory(root, data, missing)
            report_path = docs / data["artifacts"]["report"]
            evidence_path = docs / data["artifacts"]["evidence"]
            report_path.write_text(report, encoding="utf-8")
            evidence_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return validate_bug_audit.run_validation(evidence_path, report_path)

    @staticmethod
    def materialize_inventory(root: Path, data: dict, missing: tuple[str, ...] = ()) -> None:
        """Create the audited tree the evidence claims, so path checks have something to resolve.

        Unsafe paths are skipped on purpose: a test that feeds an absolute or parent path is
        asserting that the validator rejects it, not asking for a file outside the temp root.
        Paths named in `missing` are left uncreated so a test can model a fabricated path.
        """
        for item in data["inventory"]:
            if item["path"] in missing or not validate_bug_audit._safe_inventory_path(item["path"]):
                continue
            target = root / PurePosixPath(item["path"].replace("\\", "/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.touch()

    def test_valid_rapid_and_comprehensive_v2_pairs(self) -> None:
        self.assertEqual([], self.validate_pair(rapid_evidence(), rapid_report()))
        self.assertEqual([], self.validate_pair(comprehensive_evidence(), comprehensive_report()))

    def test_v1_schema_is_rejected(self) -> None:
        data = rapid_evidence()
        data["schema_version"] = "1.0"
        errors = self.validate_pair(data, rapid_report(data))
        self.assertTrue(any("expected constant '3.0'" in error for error in errors))

    def test_rapid_forbids_scores_and_high_confidence(self) -> None:
        data = rapid_evidence()
        data["assessment"]["confidence"] = "High"
        data["total_score"] = 75
        data["rating"] = "Generally good"
        data["dimensions"] = []
        errors = self.validate_pair(data, rapid_report(data))
        self.assertTrue(any("forbidden in Rapid mode" in error for error in errors))
        self.assertTrue(any("Rapid confidence cannot be High" in error for error in errors))

    def test_defect_requires_contract_direct_evidence_and_confirmation(self) -> None:
        data = rapid_evidence()
        finding = defect_finding()
        finding.update({"confidence": 6, "evidence_kind": "inferred", "status": "needs-verification"})
        del finding["expected_behavior"]
        del finding["actual_behavior"]
        data["findings"] = [finding]
        errors = self.validate_pair(data, rapid_report())
        self.assertTrue(any("expected_behavior" in error for error in errors))
        self.assertTrue(any("actual_behavior" in error for error in errors))
        self.assertTrue(any("observed or reproduced" in error for error in errors))
        self.assertTrue(any("confidence of at least 7" in error for error in errors))
        self.assertTrue(any("must be confirmed" in error for error in errors))

    def test_risk_requires_non_empty_preconditions(self) -> None:
        data = rapid_evidence()
        finding = risk_finding("Low")
        finding["preconditions"] = ""
        data["findings"] = [finding]
        errors = self.validate_pair(data, rapid_report(data))
        self.assertTrue(any("risk requires non-empty preconditions" in error for error in errors))

    def test_rapid_forbids_quality_debt(self) -> None:
        data = rapid_evidence()
        data["findings"] = [quality_debt_finding("Low")]
        errors = self.validate_pair(data, rapid_report(data))
        self.assertTrue(any("quality-debt is forbidden in Rapid mode" in error for error in errors))

    def test_comprehensive_accepts_scored_quality_debt(self) -> None:
        data = comprehensive_evidence()
        finding = quality_debt_finding()
        data["findings"] = [finding]
        architecture = next(item for item in data["dimensions"] if item["id"] == "architecture")
        architecture.update({"level": 3, "score": 6, "finding_ids": [finding["finding_id"]]})
        data["total_score"] = 78
        errors = self.validate_pair(data, comprehensive_report(data))
        self.assertEqual([], errors)

    def test_findings_table_requires_canonical_type_order(self) -> None:
        data = comprehensive_evidence()
        findings = [quality_debt_finding("Low"), risk_finding("Low"), defect_finding("Low")]
        data["findings"] = findings
        for finding in findings:
            dimension_id = validate_bug_audit.CATEGORY_DIMENSION[finding["category"]]
            dimension = next(item for item in data["dimensions"] if item["id"] == dimension_id)
            dimension["finding_ids"].append(finding["finding_id"])
        valid_report = comprehensive_report(data)
        self.assertEqual([], self.validate_pair(data, valid_report))

        lines = valid_report.splitlines()
        row_indexes = [index for index, line in enumerate(lines) if line.startswith(("| BUG-", "| RISK-", "| DEBT-"))]
        lines[row_indexes[0]], lines[row_indexes[1]] = lines[row_indexes[1]], lines[row_indexes[0]]
        errors = self.validate_pair(data, "\n".join(lines))
        self.assertTrue(any("canonical order" in error for error in errors))

    def test_confirmed_medium_runtime_finding_forbids_low_and_caps_dimension(self) -> None:
        data = comprehensive_evidence()
        finding = defect_finding()
        data["findings"] = [finding]
        data["dimensions"][0]["finding_ids"] = [finding["finding_id"]]
        errors = self.validate_pair(data, comprehensive_report(data))
        self.assertTrue(any("forbids Low risk" in error for error in errors))
        self.assertTrue(any("caps level at 3" in error for error in errors))

    def test_comprehensive_recalculates_coverage_weight_and_total(self) -> None:
        data = comprehensive_evidence()
        data["coverage"]["read_files"] = 1
        data["dimensions"][0]["weight"] = 29
        data["total_score"] = 82
        errors = self.validate_pair(data, comprehensive_report(data))
        self.assertTrue(any("coverage.read_files" in error for error in errors))
        self.assertTrue(any("weight: expected 30" in error for error in errors))
        self.assertTrue(any("total_score" in error for error in errors))

    def test_comprehensive_validates_na_renormalization(self) -> None:
        data = comprehensive_evidence()
        dead_code = next(item for item in data["dimensions"] if item["id"] == "dead_code")
        dead_code.update({"level": None, "score": None, "na_reason": "The fixture has no dead-code surface."})
        data["total_score"] = 79
        errors = self.validate_pair(data, comprehensive_report(data))
        self.assertTrue(any("total_score: expected 80" in error for error in errors))
        data["total_score"] = 80
        del dead_code["na_reason"]
        errors = self.validate_pair(data, comprehensive_report(data))
        self.assertTrue(any("N/A requires null score and na_reason" in error for error in errors))

    def test_duplicate_fingerprint_and_missing_verification_fail(self) -> None:
        data = rapid_evidence()
        first = defect_finding("Low")
        second = copy.deepcopy(first)
        second["finding_id"] = "BUG-002"
        del second["verification"]
        data["findings"] = [first, second]
        errors = self.validate_pair(data, rapid_report())
        self.assertTrue(any("missing required property 'verification'" in error for error in errors))
        second["verification"] = "Run the existing regression test."
        errors = self.validate_pair(data, rapid_report(data))
        self.assertTrue(any("duplicate root-cause fingerprint" in error for error in errors))

    def test_medium_requires_detail_and_exact_sections(self) -> None:
        data = rapid_evidence()
        finding = defect_finding()
        data["findings"] = [finding]
        data["assessment"]["risk"] = "Medium"
        report = rapid_report().replace(
            "No reportable findings were identified within the reviewed scope.",
            "| ID | Type | Severity / confidence | Location | Problem and impact | Recommendation |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| BUG-001 | defect | 🟡 Medium / 8 | src/main.py:1 | Wrong result. | Correct it. |",
        ).replace("## 2. Review Coverage and Bug Surfaces", "## 2. Reviewed Areas")
        errors = self.validate_pair(data, report)
        self.assertTrue(any("requires a detail heading" in error for error in errors))
        self.assertTrue(any("expected exactly four sections" in error for error in errors))

    def test_compliance_property_is_rejected(self) -> None:
        data = comprehensive_evidence()
        data["compliance"] = []
        errors = self.validate_pair(data, comprehensive_report(data))
        self.assertTrue(any("unexpected property 'compliance'" in error for error in errors))

    def test_windows_relative_path_utf8_and_empty_findings_are_valid(self) -> None:
        self.assertEqual([], self.validate_pair(rapid_evidence(), rapid_report()))

    def test_artifacts_outside_docs_are_rejected(self) -> None:
        data = rapid_evidence()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report_path = root / data["artifacts"]["report"]
            evidence_path = root / data["artifacts"]["evidence"]
            report_path.write_text(rapid_report(data), encoding="utf-8")
            evidence_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            errors = validate_bug_audit.run_validation(evidence_path, report_path)
        self.assertTrue(
            any("must live in the repository .docs directory" in error for error in errors)
        )

    def test_absolute_or_parent_inventory_path_fails(self) -> None:
        for path in ("C:\\repo\\secret.py", "../outside.py"):
            with self.subTest(path=path):
                data = rapid_evidence()
                data["inventory"][0]["path"] = path
                errors = self.validate_pair(data, rapid_report(data))
                self.assertTrue(any("repository-relative" in error for error in errors))

    def test_artifact_collision_uses_shared_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "repository-bug-audit-report.md").write_text("existing", encoding="utf-8")
            report, evidence = validate_bug_audit.select_artifact_paths(
                root, "comprehensive", datetime(2026, 8, 5, 12, 34, 56)
            )
            self.assertEqual("repository-bug-audit-report-20260805-123456.md", report.name)
            self.assertEqual("repository-bug-audit-report-20260805-123456.evidence.json", evidence.name)

    def test_unbacked_inventory_path_is_rejected(self) -> None:
        data = comprehensive_evidence()
        data["inventory"][1]["path"] = "src/ghost.py"
        errors = self.validate_pair(data, comprehensive_report(data), missing=("src/ghost.py",))
        self.assertTrue(
            any("'src/ghost.py' does not exist in the audited tree" in error for error in errors)
        )

    def test_unbacked_finding_location_is_rejected(self) -> None:
        data = comprehensive_evidence()
        finding = defect_finding("Low")
        finding["location"] = "src/ghost.py:12"
        data["findings"] = [finding]
        data["dimensions"][0]["finding_ids"] = ["BUG-001"]
        errors = self.validate_pair(data, comprehensive_report(data))
        self.assertTrue(
            any("'src/ghost.py:12' does not exist in the audited tree" in error for error in errors)
        )

    def test_backed_finding_location_with_line_number_is_accepted(self) -> None:
        self.assertEqual([], self.validate_pair(comprehensive_evidence(), comprehensive_report()))

    def test_detached_tree_reports_a_repo_root_hint(self) -> None:
        errors = self.validate_pair(comprehensive_evidence(), comprehensive_report(), materialize=False)
        self.assertTrue(any("pass --repo-root" in error for error in errors))

    def test_repo_root_override_resolves_paths(self) -> None:
        data = comprehensive_evidence()
        with tempfile.TemporaryDirectory() as artifacts, tempfile.TemporaryDirectory() as tree:
            docs = Path(artifacts) / ".docs"
            docs.mkdir()
            self.materialize_inventory(Path(tree), data)
            report_path = docs / data["artifacts"]["report"]
            evidence_path = docs / data["artifacts"]["evidence"]
            report_path.write_text(comprehensive_report(data), encoding="utf-8")
            evidence_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertTrue(
                any(
                    "pass --repo-root" in error
                    for error in validate_bug_audit.run_validation(evidence_path, report_path)
                )
            )
            self.assertEqual(
                [],
                validate_bug_audit.run_validation(evidence_path, report_path, Path(tree)),
            )

    def test_comprehensive_allows_mapped_only_in_a_provisional_report(self) -> None:
        data = narrowed_comprehensive_evidence()
        report = comprehensive_report(data).replace(
            "# Repository Bug Audit\n",
            "# Repository Bug Audit\n\n**Provisional report**\n",
            1,
        )
        self.assertEqual([], self.validate_pair(data, report))

        data["execution"]["provisional"] = False
        errors = self.validate_pair(data, comprehensive_report(data))
        self.assertTrue(
            any("cannot leave in-scope items mapped" in error for error in errors)
        )

    def test_comprehensive_mapped_item_requires_a_reason(self) -> None:
        data = narrowed_comprehensive_evidence()
        del data["inventory"][2]["reason"]
        report = comprehensive_report(data).replace(
            "# Repository Bug Audit\n",
            "# Repository Bug Audit\n\n**Provisional report**\n",
            1,
        )
        errors = self.validate_pair(data, report)
        self.assertTrue(any("required for mapped items" in error for error in errors))

    def test_rapid_mapped_item_needs_no_reason(self) -> None:
        self.assertEqual([], self.validate_pair(rapid_evidence(), rapid_report()))

    def test_critical_coverage_is_recomputed_from_inventory(self) -> None:
        data = comprehensive_evidence()
        data["coverage"]["critical_read_files"] = 0
        errors = self.validate_pair(data, comprehensive_report(data))
        self.assertTrue(any("coverage.critical_read_files" in error for error in errors))

    def test_unread_core_file_forbids_medium_confidence(self) -> None:
        data = rapid_evidence()
        data["inventory"][0]["status"] = "mapped"
        data["inventory"][1]["status"] = "read"
        data["coverage"].update({"critical_read_files": 0, "critical_percentage": 0.0})
        errors = self.validate_pair(data, rapid_report(data))
        self.assertTrue(any("every core/high-risk file to be read" in error for error in errors))

    def test_inventory_without_a_core_or_high_tier_is_rejected(self) -> None:
        data = comprehensive_evidence()
        data["inventory"][0]["risk_tier"] = "standard"
        data["coverage"].update(
            {"critical_in_scope_files": 0, "critical_read_files": 0, "critical_percentage": 0.0}
        )
        errors = self.validate_pair(data, comprehensive_report(data))
        self.assertTrue(any("core or high risk tier" in error for error in errors))

    def test_report_must_state_core_path_coverage(self) -> None:
        data = comprehensive_evidence()
        report = comprehensive_report(data).replace("| Core-path coverage | 1 / 1, 100% |\n", "")
        errors = self.validate_pair(data, report)
        self.assertTrue(any("must state core-path coverage" in error for error in errors))

    def test_findings_table_requires_the_emoji_severity_label(self) -> None:
        data = comprehensive_evidence()
        data["findings"] = [defect_finding("Low")]
        data["dimensions"][0]["finding_ids"] = ["BUG-001"]
        report = comprehensive_report(data).replace("🟢 Low /", "Low /")
        errors = self.validate_pair(data, report)
        self.assertTrue(any("emoji severity label" in error for error in errors))

    def test_emoji_severity_in_evidence_is_rejected(self) -> None:
        data = comprehensive_evidence()
        report = comprehensive_report(data)  # rendered before the evidence is corrupted
        finding = defect_finding()
        finding["severity"] = "🟡 Medium"
        data["findings"] = [finding]
        errors = self.validate_pair(data, report)
        self.assertTrue(any("is not in the allowed enum" in error for error in errors))

    def test_unreadable_input_returns_exit_code_two(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code = validate_bug_audit.main(
                ["--evidence", str(root / "missing.json"), "--report", str(root / "missing.md")]
            )
            self.assertEqual(2, code)


if __name__ == "__main__":
    unittest.main()
