# Uploading / Moving Data

Large transfers go through the dedicated COPY login nodes: copy23-1 / copy23-2 (`.hpc.itc.rwth-aachen.de`), not the normal login nodes.

## rsync (Linux/Mac, recommended)
- Upload to $HOME: `rsync -aP -e ssh <file> <user>@copy23-1.hpc.itc.rwth-aachen.de:/home/<user>/`
- Upload to project scratch/fast storage: target `/work/rwth2125/...` or `/hpcwork/rwth2125/datasets/`.
- Download: `rsync -aP -e ssh <user>@copy23-1.hpc.itc.rwth-aachen.de:/path/file .`
- Flags: `-a` preserve metadata, `-P` progress, `-e ssh` use ssh.

## sftp
`sftp <user>@copy23-1.hpc.itc.rwth-aachen.de` then `cd /hpcwork/<user>`, `put <local>`, `get <remote>`, `quit`. For $WORK/$HPCWORK use the full path.

## WinSCP (Windows)
Enter hostname + credentials + MFA; drag and drop. For $WORK/$HPCWORK enter the explicit path.

## rclone (cluster <-> another cluster)
Available on copy23 nodes. `rclone config` to set up an sftp remote; `rclone copy`/`rclone sync`. Use `--multi-thread-streams` / `--transfers` carefully to avoid overloading the filesystem; test with a small amount first.

## Tips
- Transferring a few large files is much faster than many small ones — tar them first: `tar -cf archive.tar data/`.
- Other options: FastX File Manager and HPC JupyterHub (small transfers only).

## Git workflow for code
- On a login node: `cd /work/rwth2125/repos && git clone <repo-url>`.
- Round trip: edit/commit/push from your laptop → on the login node `git pull` → `sbatch`.
