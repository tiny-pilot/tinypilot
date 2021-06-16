# Remote scripts

Please setup the SSH configuration on your device as described in [CONTRIBUTING.md](../../CONTRIBUTING.md).

## `pull`

Run a specific git revision of the backend server.

```bash
ssh root@tinypilot -t /opt/tinypilot/dev-scripts/remote-scripts/pull origin/my-branch
```

Without argument, it pulls the latest version of the current branch.

```bash
ssh root@tinypilot -t /opt/tinypilot/dev-scripts/remote-scripts/pull
```
