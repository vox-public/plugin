import json
import os
import re
import subprocess
import unittest
from pathlib import Path

from scripts.build import ROOT


MCP_CALL_BLOCK = re.compile(r"```mcp-call\s*\n(.*?)\n```", re.DOTALL)
API_VALIDATOR = r"""
import json
import sys
import uuid

from pydantic import ValidationError
from app.dto.improvement import (
    AutomaticImprovementCaseCreateInput,
    AutomaticImprovementEventAppendInput,
    ImprovementEventAppendInput,
)

examples = json.load(sys.stdin)
errors = []
for example in examples:
    arguments = example["arguments"]
    action = arguments["action"]
    try:
        if action == "create":
            AutomaticImprovementCaseCreateInput.model_validate(arguments["payload"])
        elif action == "event":
            uuid.UUID(arguments["case_id"])
            body = arguments["payload"]["payload"]
            if body["kind"] == "evaluation_reported" and body.get("register_holdout") is True:
                # Holdout registration is accepted only by the explicit events API.
                # The MCP turns holdout_scenario into the API's canonical scenario string.
                command = json.loads(json.dumps(arguments["payload"]))
                inner = command["payload"]
                structured = inner.pop("holdout_scenario", None)
                if structured is not None:
                    inner["scenario"] = json.dumps(
                        {"task_kind": "agent_partial_edit", **structured},
                        ensure_ascii=False, separators=(",", ":"), sort_keys=True,
                    )
                ImprovementEventAppendInput.model_validate(command)
            else:
                AutomaticImprovementEventAppendInput.model_validate(arguments["payload"])
        else:
            raise ValueError("unsupported save_work_record action")
    except ValidationError as error:
        errors.extend(
            {"action": action, "loc": list(item["loc"]), "type": item["type"]}
            for item in error.errors(include_url=False)
        )
    except ValueError as error:
        errors.append({"action": action, "type": type(error).__name__})

if errors:
    sys.stderr.write(json.dumps(errors, ensure_ascii=False))
    sys.exit(1)
"""


def load_calls():
    text = (ROOT / "references/workflow-examples.md").read_text()
    return [json.loads(block) for block in MCP_CALL_BLOCK.findall(text)]


class WorkflowExampleTests(unittest.TestCase):
    def test_manual_body_examples_decode_newlines(self):
        manuals = [call for call in load_calls() if call["tool"] == "save_manual"]
        self.assertEqual(len(manuals), 2)
        for call in manuals:
            content = call["arguments"]["payload"]["content"]
            self.assertIn("\n", content)
            self.assertNotIn("\\n", content)

    def test_receipt_reads_keep_default_budget_and_document_retry(self):
        calls = load_calls()
        receipt_reads = 0
        for previous, call in zip(calls, calls[1:]):
            if call["tool"] in {"save_agent", "save_manual"} and "context_receipt" in call["arguments"]:
                self.assertEqual(previous["tool"], "get_work_context")
                self.assertGreaterEqual(previous["arguments"].get("max_tokens", 3000), 3000)
                receipt_reads += 1
        self.assertEqual(receipt_reads, 3)
        for path in (
            "references/execution-contract.md",
            "references/workflow-examples.md",
            "references/host-adapters.md",
            "skills/agents-platform/SKILL.md",
            "README.md",
        ):
            text = (ROOT / path).read_text()
            self.assertIn("MEMORY_CONTEXT_BUDGET_TOO_SMALL", text, path)
            self.assertIn("details.required_tokens", text, path)

    def test_shared_work_examples_validate_with_api_dtos(self):
        calls = [call for call in load_calls() if call["tool"] == "save_work_record"]
        self.assertEqual([call["arguments"]["action"] for call in calls], ["create", "event", "event", "event"])

        def is_holdout(call):
            body = call["arguments"]["payload"].get("payload", {})
            return body.get("kind") == "evaluation_reported" and body.get("register_holdout") is True

        for call in calls:
            source = call["arguments"]["payload"]["source"]
            self.assertTrue(source["explicit_quote"].strip())
            if is_holdout(call):
                continue
            self.assertNotIn("source_thread_id", source)

        feedback = next(
            call for call in calls
            if call["arguments"]["action"] == "event"
            and call["arguments"]["payload"]["payload"]["kind"] == "feedback_reported"
        )
        feedback_payload = feedback["arguments"]["payload"]["payload"]
        self.assertIn("고객 보고", feedback_payload["statement"])
        self.assertIn("독립 call 조회는 아직 없음", feedback_payload["statement"])
        self.assertIsNone(feedback_payload.get("call_id"))

        holdout = next(
            call for call in calls
            if call["arguments"]["action"] == "event"
            and call["arguments"]["payload"]["payload"]["kind"] == "evaluation_reported"
        )
        holdout_payload = holdout["arguments"]["payload"]["payload"]
        self.assertTrue(holdout_payload["register_holdout"])
        holdout_command = holdout["arguments"]["payload"]
        self.assertNotIn("expected_settings_revision", holdout_command)
        self.assertNotIn("expected_settings_epoch", holdout_command)
        holdout_source = holdout_command["source"]
        self.assertEqual(holdout_source["source_host"], "embedded")
        self.assertTrue(holdout_source["source_thread_id"] and holdout_source["source_message_id"])
        self.assertEqual(holdout_payload["evaluation_kind"], "text_contract")
        # The example uses the structured holdout_scenario, never a hand-built scenario string.
        self.assertNotIn("scenario", holdout_payload)
        structured = holdout_payload["holdout_scenario"]
        self.assertEqual(
            set(structured), {"base_configuration", "requested_change", "required_preservation"}
        )
        self.assertTrue(1 <= len(structured["required_preservation"]) <= 6)

        # The holdout source ids come from a get_work_context pending_recent_inputs item,
        # so the guidance and example must say to copy them instead of guessing.
        examples_text = (ROOT / "references/workflow-examples.md").read_text()
        for text in (
            examples_text,
            (ROOT / "references/workflow-guidance.md").read_text(),
            (ROOT / "references/execution-contract.md").read_text(),
            (ROOT / "skills/resume-agent-work/SKILL.md").read_text(),
        ):
            self.assertIn("pending_recent_inputs", text)
            self.assertIn("source_thread_id", text)
        self.assertIn(
            f'"source_id":"{holdout_source["source_message_id"]}","source_thread_id":"{holdout_source["source_thread_id"]}"',
            examples_text,
        )
        # Eligibility is an observable rule, never a host-name rule: an embedded Copilot runtime
        # (Codex-based) once refused to register because guidance called Codex an "external host".
        prohibition = re.compile(r"(외부 호스트|external hosts?)[^.]{0,80}(등록할 수 없|사용할 수 없|cannot register)")
        for path in (
            "references/workflow-examples.md",
            "references/workflow-guidance.md",
            "references/execution-contract.md",
            "skills/resume-agent-work/SKILL.md",
            "README.md",
        ):
            text = (ROOT / path).read_text()
            self.assertIsNone(prohibition.search(text), path)
            if path != "README.md":
                self.assertIn("호스트 이름", text, path)
                self.assertIn("get_work_context(agent_id)", text, path)
                self.assertIn("해당 항목이 없으면 등록할 수 없다고 안내한다", text, path)
        for path in (
            "references/workflow-examples.md",
            "references/workflow-guidance.md",
            "references/execution-contract.md",
            "skills/resume-agent-work/SKILL.md",
        ):
            self.assertIn("holdout_scenario", (ROOT / path).read_text(), path)
        schema = json.loads((ROOT / "references/tool-schemas/save_work_record.json").read_text())
        holdout_description = schema["inputSchema"]["$defs"]["HoldoutRegistrationPayload"]["description"]
        self.assertIn("Do not decide eligibility from the host name", holdout_description)
        self.assertIn("holdout_scenario", holdout_description)
        self.assertIn("holdout_scenario", schema["inputSchema"]["$defs"]["HoldoutRegistrationPayload"]["properties"])
        # Negative example: routine-only fields on a holdout are rejected field by field.
        self.assertIn("잘못된 예", examples_text)
        self.assertIn("INVALID_ARGUMENTS", examples_text)
        self.assertIn("details.problems", examples_text)
        negative = next(line for line in examples_text.splitlines() if line.startswith("잘못된 예"))
        self.assertIn("register_holdout: true", negative)
        self.assertIn("expected_settings_revision", negative)
        self.assertIn("no provider execution", holdout_payload["observed_result"].lower())

        api_root = Path(os.environ.get("VOX_API_ROOT", ROOT.parent / "api")).resolve()
        python = api_root / ".venv/bin/python"
        if not python.is_file():
            self.skipTest("API worktree virtualenv unavailable; set VOX_API_ROOT to enable DTO validation")

        examples = [{"arguments": call["arguments"]} for call in calls]
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run(
            [str(python), "-B", "-c", API_VALIDATOR],
            cwd=api_root,
            env=env,
            input=json.dumps(examples, ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
        self.assertEqual(result.returncode, 0, f"API DTO validation failed: {result.stderr.strip()}")
        self.assertEqual(result.stdout, "")


class ClaimWithdrawalGuidanceTests(unittest.TestCase):
    GUIDANCE_FILES = [
        "references/execution-contract.md",
        "references/host-adapters.md",
        "references/workflow-guidance.md",
        "skills/resume-agent-work/SKILL.md",
    ]

    def test_schema_snapshot_accepts_claim_withdrawn_on_the_explicit_route_only(self):
        schema = json.loads((ROOT / "references/tool-schemas/save_work_record.json").read_text())["inputSchema"]
        defs = schema["$defs"]
        withdrawn = defs["ClaimWithdrawnPayload"]
        self.assertEqual(withdrawn["required"], ["kind", "claim_id", "reason"])
        self.assertEqual(withdrawn["properties"]["reason"]["maxLength"], 300)
        self.assertIn(
            "claim_withdrawn", defs["ImprovementEventAppendInput"]["properties"]["payload"]["discriminator"]["mapping"]
        )
        self.assertNotIn(
            "claim_withdrawn",
            defs["AutomaticImprovementEventAppendInput"]["properties"]["payload"]["discriminator"]["mapping"],
        )

    def test_guidance_separates_single_memory_withdrawal_from_source_deletion(self):
        for relative in self.GUIDANCE_FILES:
            text = (ROOT / relative).read_text()
            with self.subTest(file=relative):
                self.assertIn("같은 출처에서 나온 사용자의 모든 case 기록을 함께 지운다", text)
                self.assertIn("`claim_withdrawn`(claim_id, reason, 중복이면 duplicate_of_claim_id)", text)
                self.assertIn("실행 전에 함께 지워지는 다른 기록을 알린다", text)
                self.assertIn("되묻지 말고 `claim_corrected`로 기존 결정을 정정해 기록한다", text)


class HoldoutLiteralGuidanceTests(unittest.TestCase):
    HOLDOUT_FILES = [
        "references/execution-contract.md",
        "references/workflow-guidance.md",
        "skills/resume-agent-work/SKILL.md",
    ]
    BAD_EXAMPLE = "환불 문의의 영수증 요청 문구"

    def test_schema_snapshot_carries_optional_literal_fields(self):
        schema = json.loads((ROOT / "references/tool-schemas/save_work_record.json").read_text())["inputSchema"]
        scenario = schema["$defs"]["HoldoutRegistrationPayload"]["properties"]["holdout_scenario"]
        self.assertEqual(scenario["required"], ["base_configuration", "requested_change", "required_preservation"])
        self.assertEqual(
            (scenario["properties"]["required_additions"]["minItems"], scenario["properties"]["required_additions"]["maxItems"]),
            (1, 4),
        )
        self.assertEqual(scenario["properties"]["retired_literals"]["maxItems"], 4)

    def test_holdout_guidance_requires_literal_text_and_shows_the_duplicated_fact_case(self):
        for relative in [*self.HOLDOUT_FILES, "references/workflow-examples.md"]:
            text = (ROOT / relative).read_text()
            with self.subTest(file=relative):
                self.assertNotIn(self.BAD_EXAMPLE, text)
                self.assertIn("글자 그대로 복사한", text)
                self.assertIn("채점", text)
                self.assertIn("required_additions", text)
                self.assertIn("retired_literals", text)
                self.assertIn("오후 8시", text)
                self.assertIn("오후 7시", text)

    def test_editing_skills_end_with_a_decision_record_step(self):
        for name in ("edit-manual-safely", "tune-voice-behavior", "try-and-improve-voice-agent"):
            text = (ROOT / f"skills/{name}/SKILL.md").read_text()
            with self.subTest(skill=name):
                self.assertIn("앞으로도 지킬 규칙·결정", text)
                self.assertIn('"앞으로", "항상", "다음에도"', text)
                self.assertIn("`save_work_record`의 `decision_set`으로 짧게 기록한다", text)
                self.assertIn("OFF이거나 사용자가 기록하지 말라고 했으면 제외", text)


if __name__ == "__main__":
    unittest.main()
