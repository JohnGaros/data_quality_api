# Git Multi-Remote Push Skill

This skill helps Claude understand how to push commits to multiple remotes.

## Remote Configuration

| Remote | Platform | URL |
|--------|----------|-----|
| `origin` | **GitHub** | https://github.com/JohnGaros/data_quality_api.git |
| `secondary` | **Azure DevOps** | https://dev.azure.com/WeMetrix/Wemetrix%20Data%20Quality%20and%20Governance%20Platform/_git/Wemetrix%20Data%20Quality%20and%20Governance%20Platform |

## Push Command Reference

### Push to GitHub
When the user says "push to github", "push to origin", or similar:
```bash
git push origin <branch>
```

### Push to Azure DevOps
When the user says "push to azure", "push to secondary", "push to devops", or similar:
```bash
git push secondary <branch>
```

### Push to Both Remotes
When the user says "push to both", "push everywhere", "sync remotes", or similar:
```bash
git push origin <branch> && git push secondary <branch>
```

## Branch Operations

### Create and Push New Branch to GitHub
```bash
git checkout -b <branch-name>
git push -u origin <branch-name>
```

### Create and Push New Branch to Azure DevOps
```bash
git checkout -b <branch-name>
git push -u secondary <branch-name>
```

### Create and Push New Branch to Both
```bash
git checkout -b <branch-name>
git push -u origin <branch-name> && git push secondary <branch-name>
```

## Current Branch State

To check which remote a branch tracks:
```bash
git branch -vv
```

## Important Notes

1. **Default remote is `origin` (GitHub)** - If unspecified, prefer GitHub
2. **Azure DevOps remote is `secondary`** - Use for Azure-specific requests
3. **Always confirm branch name** before pushing to avoid mistakes
4. **Use `-u` flag** when pushing a new branch to set upstream tracking
5. **Check for unpushed commits** with `git log origin/<branch>..HEAD` before pushing

## User Intent Mapping

| User Says | Action |
|-----------|--------|
| "push to github" | `git push origin <branch>` |
| "push to origin" | `git push origin <branch>` |
| "push to azure" | `git push secondary <branch>` |
| "push to devops" | `git push secondary <branch>` |
| "push to secondary" | `git push secondary <branch>` |
| "push to both" | Push to both remotes |
| "sync remotes" | Push to both remotes |
| "create branch X on github" | Create branch, push to origin with -u |
| "create branch X on azure" | Create branch, push to secondary with -u |
| "create branch X everywhere" | Create branch, push to both with -u |
