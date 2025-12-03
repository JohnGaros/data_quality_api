#!/usr/bin/env python3
"""Parse checkpoints and generate progress dashboard.

This script scans all .checkpoint files in specs/ and generates a
progress dashboard showing milestone, epic, and feature status.
"""

from pathlib import Path
from typing import Dict, List
import yaml
import json
import sys


def parse_checkpoints(specs_dir: Path) -> Dict:
    """Parse all .checkpoint files and aggregate progress."""
    checkpoints = []

    for checkpoint_file in sorted(specs_dir.rglob(".checkpoint")):
        try:
            with open(checkpoint_file) as f:
                data = yaml.safe_load(f)

            # Calculate progress percentage
            progress_pct = calculate_progress(data)

            # Extract path components (milestone/epic/feature)
            rel_path = checkpoint_file.relative_to(specs_dir)
            path_parts = rel_path.parts

            # Parse milestone/epic from path
            milestone = path_parts[1] if len(path_parts) > 1 and path_parts[0] == "milestones" else "standalone"
            epic = path_parts[3] if len(path_parts) > 3 and path_parts[2] == "epics" else "none"

            checkpoints.append({
                "path": str(rel_path.parent),
                "feature_id": data.get("feature_id", "unknown"),
                "feature": data.get("feature_name", "Unknown"),
                "status": data.get("status", "unknown"),
                "progress_pct": progress_pct,
                "current_phase": data.get("current_phase"),
                "time_spent_minutes": data.get("time_spent_minutes", 0),
                "blockers": data.get("blockers", []),
                "milestone": milestone,
                "epic": epic,
            })
        except Exception as e:
            print(f"Warning: Failed to parse {checkpoint_file}: {e}", file=sys.stderr)
            continue

    return {
        "total_features": len(checkpoints),
        "completed": sum(1 for c in checkpoints if c["status"] == "completed"),
        "in_progress": sum(1 for c in checkpoints if c["status"] == "in_progress"),
        "blocked": sum(1 for c in checkpoints if c["status"] == "blocked"),
        "not_started": sum(1 for c in checkpoints if c["status"] == "not_started"),
        "total_time_minutes": sum(c["time_spent_minutes"] for c in checkpoints),
        "features": checkpoints,
    }


def calculate_progress(checkpoint: Dict) -> float:
    """Calculate percentage completion from phases."""
    phases = checkpoint.get("phases", [])
    if not phases:
        return 0.0

    total_tasks = sum(p.get("tasks_total", 0) for p in phases)
    completed_tasks = sum(p.get("tasks_completed", 0) for p in phases)

    return round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0.0


def group_by_milestone(features: List[Dict]) -> Dict[str, List[Dict]]:
    """Group features by milestone."""
    milestones = {}
    for feature in features:
        milestone = feature["milestone"]
        if milestone not in milestones:
            milestones[milestone] = []
        milestones[milestone].append(feature)
    return milestones


def format_time(minutes: int) -> str:
    """Format minutes into human-readable string."""
    if minutes == 0:
        return "0 min"
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
    return f"{mins}m"


def print_dashboard(data: Dict):
    """Print formatted progress dashboard."""
    print("=" * 80)
    print("DATA QUALITY PLATFORM - PROGRESS DASHBOARD")
    print("=" * 80)
    print()

    # Summary stats
    print("SUMMARY")
    print("-" * 80)
    print(f"Total Features:     {data['total_features']}")
    print(f"  Completed:        {data['completed']}")
    print(f"  In Progress:      {data['in_progress']}")
    print(f"  Blocked:          {data['blocked']}")
    print(f"  Not Started:      {data['not_started']}")
    print(f"Total Time Spent:   {format_time(data['total_time_minutes'])}")
    print()

    # Overall progress
    if data['total_features'] > 0:
        overall_pct = sum(f['progress_pct'] for f in data['features']) / data['total_features']
        print(f"Overall Progress:   {overall_pct:.1f}%")
        print()

    # Group by milestone
    milestones = group_by_milestone(data['features'])

    for milestone_name in sorted(milestones.keys()):
        features = milestones[milestone_name]

        # Milestone header
        print("=" * 80)
        print(f"MILESTONE: {milestone_name}")
        print("=" * 80)

        # Group by epic within milestone
        epics = {}
        for feature in features:
            epic = feature["epic"]
            if epic not in epics:
                epics[epic] = []
            epics[epic].append(feature)

        for epic_name in sorted(epics.keys()):
            epic_features = epics[epic_name]
            epic_progress = sum(f['progress_pct'] for f in epic_features) / len(epic_features) if epic_features else 0
            epic_time = sum(f['time_spent_minutes'] for f in epic_features)

            print()
            print(f"Epic: {epic_name} ({epic_progress:.1f}% - {format_time(epic_time)})")
            print("-" * 80)

            for feature in epic_features:
                status_icon = {
                    "completed": "✓",
                    "in_progress": "→",
                    "blocked": "✗",
                    "not_started": "○",
                }.get(feature["status"], "?")

                phase_info = f"Phase {feature['current_phase']}" if feature['current_phase'] else "Not started"
                time_info = format_time(feature['time_spent_minutes'])

                print(f"  {status_icon} {feature['feature']:30} {feature['progress_pct']:5.1f}%  {phase_info:12}  {time_info:8}")

                # Show blockers if any
                if feature['blockers']:
                    for blocker in feature['blockers']:
                        print(f"      BLOCKER: {blocker}")

        print()

    print("=" * 80)


def main():
    """Main entry point."""
    # Determine specs directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    specs_dir = project_root / "specs"

    if not specs_dir.exists():
        print(f"Error: specs directory not found: {specs_dir}", file=sys.stderr)
        sys.exit(1)

    # Parse checkpoints
    data = parse_checkpoints(specs_dir)

    # Print dashboard
    print_dashboard(data)

    # Optionally write JSON output
    output_file = specs_dir / ".checkpoints" / "progress_summary.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Progress summary written to: {output_file}")


if __name__ == "__main__":
    main()
