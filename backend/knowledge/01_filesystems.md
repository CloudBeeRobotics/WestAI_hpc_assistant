# CLAIX File Systems

Three permanent file systems on CLAIX-2023. You are responsible for your own backups; the cluster is not long-term storage.

## $HOME — /home/<username>
- Permanent, has snapshots ($HOME_SNAPSHOT), has BACKUP.
- Quota: 250 GB space, 1 million files.
- Use for: source code, configuration files, important results that are hard to reproduce.
- Avoid frequent/massive file creation, deletion, or transfers here.

## $WORK — /work/<username>
- Same storage system as $HOME but NO backup. Has snapshots ($WORK_SNAPSHOT).
- Quota: 250 GB space, 1 million files.
- Use for: I/O intensive computing jobs, scratch, git repos.

## $HPCWORK — /hpcwork/<username>
- Different storage system, better I/O performance (Lustre). No backup, no snapshots.
- Quota: 1000 GB space, 1 million files. HDD pool by default; limited SSD pool for very fast I/O.
- Use for: I/O intensive jobs and LARGE files (datasets, models, checkpoints).

## $BEEOND — local SSD on compute nodes (BeeGFS On-Demand)
- Temporary, stored per-job. ML segment / HPC segment ~1.44 TB/node. Job becomes exclusive when using BeeOND.

## Switching and quotas
- `cd $HOME`, `cd $WORK`, `cd $HPCWORK` to switch.
- `r_quota` shows your personal quotas (Blocks = space, Files = inode count).
- User quotas are NOT extendable; project quotas CAN be increased on request.
