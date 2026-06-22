# Slurm Job Management Commands

Do not run squeue/sinfo/spart more often than once every 2 minutes.

- `sbatch <script>` — submit a batch job, returns a job id.
- `squeue --me` — your pending/running jobs. `squeue --me --start` — estimated start times.
- `squeue --Format=state -p c23g -h | sort | uniq -c` — running/pending counts on the GPU partition.
- `scancel <jobid>` — cancel a job. `scancel --me` — cancel all your jobs. `scancel -v <jobid>` — verbose.
- `salloc [opts]` — request an INTERACTIVE job; once it starts you get a shell on the head node; exiting ends the job. Example: `salloc -p c23g --gres=gpu:1 -n 24 -t 1:00:00`.
- `sacct` — accounting for pending/running/past jobs (Slurm shows cpu cores as "cpu").
  - `sacct -S $(date -I --date="yesterday")` — jobs since yesterday.
  - `sacct -o JobName%15,JobID,AllocTres%70` — billing/allocated resources.
  - `sacct -j <jobid> -o JobID,Account` — which account a job was charged to.
- `sinfo` — cluster info. `seff <jobid>` — job efficiency report (run after it finishes).

## Interactive development workflow
1. `salloc ...` to get an interactive node (use a FRESH shell — salloc injects SLURM_* env vars that linger).
2. `module load CUDA`, `nvidia-smi`, activate env / start container, iterate.
3. `exit` releases the node.
Only convert to an `sbatch` production script after it works interactively.
