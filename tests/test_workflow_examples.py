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
                ImprovementEventAppendInput.model_validate(arguments["payload"])
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


if __name__ == "__main__":
    unittest.main()
