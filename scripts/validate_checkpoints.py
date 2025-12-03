#!/usr/bin/env python3
"""Validate checkpoint files against schema and check for common issues."""

from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import sys
from datetime import datetime

# Checkpoint schema definition
REQUIRED_FIELDS = [
    "feature_id",
    "feature_name",
    "status",
    "phases",
]

OPTIONAL_FIELDS = [
    "current_phase",
    "last_updated",
    "updated_by",
    "session_started",
    "time_spent_minutes",
    "blockers",
    "notes",
]

VALID_STATUSES = ["not_started", "in_progress", "completed", "blocked"]

PHASE_REQUIRED_FIELDS = ["phase", "name", "status", "tasks_total"]
PHASE_OPTIONAL_FIELDS = [
    "started_at",
    "completed_at",
    "tasks_completed",
    "time_spent_minutes",
]

PHASE_VALID_STATUSES = ["not_started", "in_progress", "completed"]


class CheckpointValidator:
    """Validates checkpoint YAML files."""

    def __init__(self, specs_dir: Path):
        self.specs_dir = specs_dir
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.validated_count = 0

    def validate_all(self) -> bool:
        """Validate all checkpoint files. Returns True if all valid."""
        checkpoint_files = list(self.specs_dir.rglob(".checkpoint"))

        if not checkpoint_files:
            self.warnings.append("No checkpoint files found")
            return True

        for checkpoint_file in checkpoint_files:
            self.validate_checkpoint(checkpoint_file)

        return len(self.errors) == 0

    def validate_checkpoint(self, checkpoint_file: Path) -> None:
        """Validate a single checkpoint file."""
        rel_path = checkpoint_file.relative_to(self.specs_dir)
        self.validated_count += 1

        try:
            with open(checkpoint_file) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"{rel_path}: Invalid YAML - {e}")
            return
        except Exception as e:
            self.errors.append(f"{rel_path}: Failed to read - {e}")
            return

        if data is None:
            self.errors.append(f"{rel_path}: Empty checkpoint file")
            return

        # Validate required fields
        for field in REQUIRED_FIELDS:
            if field not in data:
                self.errors.append(f"{rel_path}: Missing required field '{field}'")

        # Validate status
        if "status" in data and data["status"] not in VALID_STATUSES:
            self.errors.append(
                f"{rel_path}: Invalid status '{data['status']}' "
                f"(must be one of {VALID_STATUSES})"
            )

        # Validate feature_id matches directory name
        if "feature_id" in data:
            expected_id = checkpoint_file.parent.name
            if data["feature_id"] != expected_id:
                self.errors.append(
                    f"{rel_path}: feature_id '{data['feature_id']}' "
                    f"doesn't match directory name '{expected_id}'"
                )

        # Validate current_phase consistency
        if "current_phase" in data and data["current_phase"] is not None:
            if data["status"] == "not_started":
                self.warnings.append(
                    f"{rel_path}: current_phase is set but status is 'not_started'"
                )
            elif data["status"] == "completed":
                self.warnings.append(
                    f"{rel_path}: current_phase is set but status is 'completed'"
                )

        # Validate phases
        if "phases" in data:
            self.validate_phases(rel_path, data["phases"], data.get("current_phase"))

        # Validate timestamps
        self.validate_timestamps(rel_path, data)

        # Check for unknown fields (informational only)
        all_valid_fields = set(REQUIRED_FIELDS + OPTIONAL_FIELDS)
        unknown_fields = set(data.keys()) - all_valid_fields
        if unknown_fields:
            self.warnings.append(
                f"{rel_path}: Unknown fields: {', '.join(unknown_fields)}"
            )

    def validate_phases(
        self, rel_path: Path, phases: List[Dict], current_phase: Optional[int]
    ) -> None:
        """Validate phase structure and consistency."""
        if not isinstance(phases, list):
            self.errors.append(f"{rel_path}: 'phases' must be a list")
            return

        if not phases:
            self.errors.append(f"{rel_path}: 'phases' list is empty")
            return

        phase_numbers = []
        in_progress_count = 0

        for i, phase in enumerate(phases):
            if not isinstance(phase, dict):
                self.errors.append(f"{rel_path}: Phase {i+1} is not a dictionary")
                continue

            # Validate required fields
            for field in PHASE_REQUIRED_FIELDS:
                if field not in phase:
                    self.errors.append(
                        f"{rel_path}: Phase {i+1} missing required field '{field}'"
                    )

            # Validate phase number
            if "phase" in phase:
                phase_num = phase["phase"]
                phase_numbers.append(phase_num)
                if phase_num != i + 1:
                    self.errors.append(
                        f"{rel_path}: Phase number {phase_num} "
                        f"doesn't match position {i+1}"
                    )

            # Validate phase status
            if "status" in phase and phase["status"] not in PHASE_VALID_STATUSES:
                self.errors.append(
                    f"{rel_path}: Phase {i+1} has invalid status '{phase['status']}' "
                    f"(must be one of {PHASE_VALID_STATUSES})"
                )

            # Count in_progress phases
            if phase.get("status") == "in_progress":
                in_progress_count += 1

            # Validate task counts
            if "tasks_total" in phase and "tasks_completed" in phase:
                total = phase["tasks_total"]
                completed = phase["tasks_completed"]
                if completed > total:
                    self.errors.append(
                        f"{rel_path}: Phase {i+1} has tasks_completed ({completed}) > "
                        f"tasks_total ({total})"
                    )

            # Validate completed_at is set for completed phases
            if phase.get("status") == "completed" and "completed_at" not in phase:
                self.warnings.append(
                    f"{rel_path}: Phase {i+1} is completed but missing 'completed_at'"
                )

            # Validate started_at is set for in_progress phases
            if phase.get("status") == "in_progress" and "started_at" not in phase:
                self.warnings.append(
                    f"{rel_path}: Phase {i+1} is in_progress but missing 'started_at'"
                )

        # Validate only one phase is in_progress
        if in_progress_count > 1:
            self.errors.append(
                f"{rel_path}: Multiple phases ({in_progress_count}) "
                f"are in_progress (should be at most 1)"
            )

        # Validate current_phase matches in_progress phase
        if current_phase is not None:
            if current_phase not in phase_numbers:
                self.errors.append(
                    f"{rel_path}: current_phase {current_phase} "
                    f"doesn't correspond to any phase"
                )
            else:
                phase_idx = current_phase - 1
                if phase_idx < len(phases):
                    phase_status = phases[phase_idx].get("status")
                    if phase_status != "in_progress":
                        self.warnings.append(
                            f"{rel_path}: current_phase {current_phase} "
                            f"has status '{phase_status}' (expected 'in_progress')"
                        )

    def validate_timestamps(self, rel_path: Path, data: Dict[str, Any]) -> None:
        """Validate timestamp formats."""
        timestamp_fields = ["last_updated", "session_started"]

        for field in timestamp_fields:
            if field in data and data[field] is not None:
                try:
                    datetime.fromisoformat(str(data[field]).replace("Z", "+00:00"))
                except ValueError:
                    self.errors.append(
                        f"{rel_path}: Invalid timestamp format for '{field}' "
                        f"(expected ISO 8601)"
                    )

        # Validate phase timestamps
        if "phases" in data:
            for i, phase in enumerate(data["phases"]):
                for field in ["started_at", "completed_at"]:
                    if field in phase and phase[field] is not None:
                        try:
                            datetime.fromisoformat(
                                str(phase[field]).replace("Z", "+00:00")
                            )
                        except ValueError:
                            self.errors.append(
                                f"{rel_path}: Phase {i+1} has invalid timestamp "
                                f"format for '{field}' (expected ISO 8601)"
                            )

    def print_report(self) -> None:
        """Print validation report."""
        print(f"\n{'='*60}")
        print("Checkpoint Validation Report")
        print(f"{'='*60}\n")

        print(f"Validated: {self.validated_count} checkpoint file(s)")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):\n")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):\n")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All checkpoint files are valid!")

        print(f"\n{'='*60}\n")


def main():
    """Main entry point."""
    specs_dir = Path(__file__).parent.parent / "specs"

    if not specs_dir.exists():
        print(f"Error: specs directory not found at {specs_dir}")
        sys.exit(1)

    validator = CheckpointValidator(specs_dir)
    all_valid = validator.validate_all()
    validator.print_report()

    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
