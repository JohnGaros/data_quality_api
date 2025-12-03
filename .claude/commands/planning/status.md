Show current feature status and quick orientation.

**Your task:**

1. Read `specs/.checkpoints/current.json` to find active feature (if exists)
   - If no current.json, scan for .checkpoint files with status = in_progress

2. For the active feature, read its `.checkpoint` file

3. Display a concise status in this format:

```
## Current Feature Status

Feature: [feature_name]
Status: [status]
Progress: [X]% complete ([tasks_completed]/[total_tasks] tasks)
Current Phase: Phase [N] - [phase_name]
Time Spent: [time_spent_minutes] minutes total

### Epic & Milestone

Epic: [epic_name] (read from parent EPIC.md)
Milestone: [milestone_name] (read from parent MILESTONE.md)
Location: [relative_path]

### Blockers

[List blockers, or "None"]

### Quick Actions

- Resume work: /planning/resume
- Update progress: /planning/checkpoint --complete-task "description"
- View all features: /planning/progress
- Switch feature: /planning/goto-feature [name]
```

**If no active feature:**
```
## No Active Feature

To start working on a feature:
1. View all features: /planning/progress
2. Switch to a feature: /planning/goto-feature [name]
3. Create new feature: /planning/new-feature

Recent features:
[List 3 most recently updated .checkpoint files with their status]
```

**Performance:**
- Should execute in < 3 seconds
- Read minimal files (current.json + 1 checkpoint + parent metadata)
