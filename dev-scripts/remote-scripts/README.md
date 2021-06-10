# Remote scripts

## Pull and run a specific git revision

```bash
ssh root@tinypilot -t "./pull origin/my-branch"
```

Without argument, it uses the latest version of the current branch.

```bash
ssh root@tinypilot -t "./pull"
```
