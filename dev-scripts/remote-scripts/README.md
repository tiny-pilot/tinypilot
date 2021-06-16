# Remote scripts

## Pull

Run a specific git revision of the backend server.

```bash
ssh root@tinypilot -t /opt/tinypilot/dev-scripts/remote-scripts/pull origin/my-branch
```

Without argument, it pulls the latest version of the current branch.

```bash
ssh root@tinypilot -t /opt/tinypilot/dev-scripts/remote-scripts/pull
```
