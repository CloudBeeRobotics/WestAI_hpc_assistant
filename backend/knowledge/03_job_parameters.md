# Slurm Job Parameters

Short form needs a space (`-J name`); long form needs `=` with no space (`--job-name=name`).

- Job name: `--job-name` / `-J`. Default = script name. Alphanumeric only.
- Run time: `--time` / `-t`, e.g. `--time=1-05:10:15` (1d 5h 10m 15s). Default 15 min. Mind your project's max run time.
- Output file: `--output` / `-o`. Default `output_%j.txt` (%j = job id). Use full explicit paths, not `~` or `$HOME`. Combine stderr into stdout (avoid `--error`).
- CPUs per task: `--cpus-per-task` / `-c` (OpenMP/threads). Default 1.
- Tasks (MPI): `--ntasks` / `-n`. Default 1. Tasks per node: `--ntasks-per-node`. Nodes: `--nodes` / `-N`.
- Memory: `--mem-per-cpu`, e.g. `--mem-per-cpu 2G`. Usually leave default (you get max memory without extra billing). Memory is per core, binary units (60G = 61440M).
- Exclusive node: `--exclusive`.
- Project/account: `--account` / `-A`, e.g. `-A rwth2125`. You must be a project member. Default = personal quota.
- GPU: `--gres=gpu:<N>`, e.g. `--gres=gpu:2`. One GPU gets a proportional share of CPUs/memory; more CPU/RAM per GPU means requesting more GPUs.
- Partition: `--partition` / `-p`, e.g. `-p c23g` (GPU), `-p c23ms` / `-p c23mm` (memory), `-p devel` (testing).
- BeeOND: `--beeond` (job becomes exclusive).

## devel partition
For short test jobs. Do NOT specify `--account` on devel. Example: `salloc -p devel -n 2 -t 25`.
