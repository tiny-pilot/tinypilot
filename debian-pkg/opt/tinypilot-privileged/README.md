# tinypilot-privileged

This directory contains all TinyPilot executables and libraries that run with root privileges.

## Rationale

Scripts that run as `root` must be owned by `root`.

The other directory for TinyPilot executables is `/opt/tinypilot/scripts`, but the `tinypilot` user has write access to files in that directory. If we placed executables in that directory that `tinypilot` can run with `sudo`, then there would be an elevation of privilege vulnerability. An attacker who compromised the `tinypilot` user could trivially elevate privilege to `root` by modifying a `tinypilot`-owned file that runs with `sudo` and replacing it with malicious behavior.

An example elevation of privilege attack might look like this:

```bash
echo "#!/bin/bash" > /opt/tinypilot/scripts/executable-with-sudo-enabled
echo "rm -rf /" >> /opt/tinypilot/scripts/executable-with-sudo-enabled
sudo /opt/tinypilot/scripts/executable-with-sudo-enabled
```

By separating scripts that run as `sudo` into a separate `tinypilot-privileged` directory and ensuring that only `root` can write files in this directory, we mitigate the risk of an elevation of privilege attack.
