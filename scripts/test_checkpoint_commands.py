#!/usr/bin/env python3
"""
Test script for checkpoint command functionality.
Simulates all checkpoint update operations.
"""

import yaml
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys

def load_checkpoint(feature_path: Path) -> dict:
    """Load checkpoint YAML file."""
    checkpoint_file = feature_path / ".checkpoint"
    with open(checkpoint_file) as f:
        return yaml.safe_load(f)

def save_checkpoint(feature_path: Path, data: dict):
    """Save checkpoint using atomic write."""
    checkpoint_file = feature_path / ".checkpoint"
    with tempfile.NamedTemporaryFile(
        mode='w', delete=False, dir=feature_path, suffix='.tmp'
    ) as tmp:
        yaml.dump(data, tmp, default_flow_style=False, sort_keys=False)
        tmp_path = tmp.name
    shutil.move(tmp_path, checkpoint_file)

def complete_task(feature_path: Path, task_description: str):
    """Mark a task as complete in current phase."""
    checkpoint = load_checkpoint(feature_path)
    
    if not checkpoint['current_phase']:
        print("Error: No active phase. Start a phase first.")
        return
    
    # Calculate time since session started
    if checkpoint['session_started']:
        session_started = datetime.fromisoformat(checkpoint['session_started'])
        session_duration = (datetime.now() - session_started).total_seconds() / 60
    else:
        session_duration = 0
    
    # Update current phase
    current_phase_idx = checkpoint['current_phase'] - 1
    phase = checkpoint['phases'][current_phase_idx]
    
    phase['tasks_completed'] += 1
    phase['time_spent_minutes'] += session_duration
    checkpoint['time_spent_minutes'] += session_duration
    
    # Reset session
    checkpoint['session_started'] = datetime.now().isoformat()
    checkpoint['last_updated'] = datetime.now().isoformat()
    
    save_checkpoint(feature_path, checkpoint)
    
    print(f"✓ Task completed: {task_description}")
    print(f"  Phase {checkpoint['current_phase']}: {phase['tasks_completed']}/{phase['tasks_total']} tasks")
    print(f"  Time: +{session_duration:.1f} min (total: {checkpoint['time_spent_minutes']:.1f} min)")

def next_phase(feature_path: Path):
    """Complete current phase and move to next."""
    checkpoint = load_checkpoint(feature_path)
    
    if not checkpoint['current_phase']:
        print("Error: No active phase.")
        return
    
    current_phase_idx = checkpoint['current_phase'] - 1
    current_phase = checkpoint['phases'][current_phase_idx]
    
    # Calculate final time for current phase
    if checkpoint['session_started']:
        session_started = datetime.fromisoformat(checkpoint['session_started'])
        session_duration = (datetime.now() - session_started).total_seconds() / 60
        current_phase['time_spent_minutes'] += session_duration
        checkpoint['time_spent_minutes'] += session_duration
    
    # Mark current phase complete
    current_phase['status'] = 'completed'
    current_phase['completed_at'] = datetime.now().isoformat()
    
    # Move to next phase
    next_phase_idx = current_phase_idx + 1
    if next_phase_idx < len(checkpoint['phases']):
        next_phase_data = checkpoint['phases'][next_phase_idx]
        next_phase_data['status'] = 'in_progress'
        next_phase_data['started_at'] = datetime.now().isoformat()
        checkpoint['current_phase'] = next_phase_data['phase']
        checkpoint['session_started'] = datetime.now().isoformat()
        
        print(f"✓ Phase {current_phase['phase']} completed")
        print(f"  Moving to Phase {next_phase_data['phase']}: {next_phase_data['name']}")
    else:
        checkpoint['status'] = 'completed'
        checkpoint['current_phase'] = None
        print(f"✓ All phases completed! Feature done.")
    
    checkpoint['last_updated'] = datetime.now().isoformat()
    save_checkpoint(feature_path, checkpoint)

def start_phase(feature_path: Path, phase_num: int):
    """Start a specific phase."""
    checkpoint = load_checkpoint(feature_path)
    
    if phase_num < 1 or phase_num > len(checkpoint['phases']):
        print(f"Error: Invalid phase number. Must be 1-{len(checkpoint['phases'])}")
        return
    
    phase_idx = phase_num - 1
    phase = checkpoint['phases'][phase_idx]
    
    checkpoint['status'] = 'in_progress'
    checkpoint['current_phase'] = phase_num
    checkpoint['session_started'] = datetime.now().isoformat()
    checkpoint['last_updated'] = datetime.now().isoformat()
    checkpoint['updated_by'] = 'claude'
    
    phase['status'] = 'in_progress'
    phase['started_at'] = datetime.now().isoformat()
    
    save_checkpoint(feature_path, checkpoint)
    
    print(f"✓ Started Phase {phase_num}: {phase['name']}")
    print(f"  Tasks: {phase['tasks_total']} to complete")

def show_status(feature_path: Path):
    """Show current status."""
    checkpoint = load_checkpoint(feature_path)
    
    print(f"\n{'='*60}")
    print(f"Feature: {checkpoint['feature_name']}")
    print(f"Status: {checkpoint['status']}")
    print(f"{'='*60}")
    
    if checkpoint['current_phase']:
        phase_idx = checkpoint['current_phase'] - 1
        phase = checkpoint['phases'][phase_idx]
        progress = (phase['tasks_completed'] / phase['tasks_total'] * 100) if phase['tasks_total'] > 0 else 0
        
        print(f"\nCurrent Phase: {checkpoint['current_phase']} - {phase['name']}")
        print(f"Progress: {phase['tasks_completed']}/{phase['tasks_total']} tasks ({progress:.1f}%)")
        print(f"Time spent: {checkpoint['time_spent_minutes']:.1f} minutes")
    else:
        print("\nNo active phase")
    
    if checkpoint['blockers']:
        print(f"\nBlockers:")
        for blocker in checkpoint['blockers']:
            print(f"  - {blocker}")
    
    print()

if __name__ == "__main__":
    feature_path = Path("specs/milestones/M1_MVP_FOUNDATION/epics/E1_CORE_VALIDATION/features/e2e_file_testing")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/test_checkpoint_commands.py status")
        print("  python scripts/test_checkpoint_commands.py start-phase <N>")
        print("  python scripts/test_checkpoint_commands.py complete-task <description>")
        print("  python scripts/test_checkpoint_commands.py next-phase")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        show_status(feature_path)
    elif command == "start-phase" and len(sys.argv) >= 3:
        start_phase(feature_path, int(sys.argv[2]))
    elif command == "complete-task" and len(sys.argv) >= 3:
        complete_task(feature_path, " ".join(sys.argv[2:]))
    elif command == "next-phase":
        next_phase(feature_path)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
