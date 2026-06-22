# Project and Work Group Space

Each computing-time project gets a Unix group and storage space to share data and executables.

## Accessing project storage (replace <project-id>, e.g. rwth2125)
- $HOME: `/home/<project-id>/`
- $WORK: `/work/<project-id>/`
- $HPCWORK: `/hpcwork/<project-id>/`
Any member of the project group can access these. By default a project gets the same quota as a user.

## Permissions
- Top-level project dirs have the setgid attribute, so files/dirs created inside inherit the group ownership automatically.
- Default umask is 007, giving group members access + modification rights.
- When COPYING files in, check group permissions and fix with `chmod` if needed; when MOVING files in, you may need `chgrp` to set group ownership.
- Do not add users to your personal group (gives them access to all your personal dirs).
- Do not revoke group permissions in shared space (so members can still manage files after you leave).

## Quotas
- `r_quota` — your personal quotas. `r_quota -u <project-id>` — project/group quotas (needs read permission).
- All quotas are directory/tree quotas: every file under the directory counts, regardless of owner.
- Request more space via the IT-ServiceDesk: give project id, filesystem, amount, (for $HPCWORK also file-quota increase), and duration. $HOME is expensive (backup) — prefer increasing $WORK / $HPCWORK.

## Recommended layout (project rwth2125)
- /work/rwth2125/repos, /work/rwth2125/docker, /work/rwth2125/docs
- /hpcwork/rwth2125/datasets, /models, /checkpoints, /results, /logs
Git tracks code/configs/Dockerfiles only — never datasets, checkpoints, or outputs.
