# Submitting Jobs with Slurm

Slurm is the workload manager/scheduler. You request cores, memory, time, GPUs from a login node; Slurm queues the job and runs it on compute nodes.

## Batch script structure
A batch script has three parts:
1. Shebang — always `#!/usr/bin/zsh` (the cluster default shell is zsh).
2. `#SBATCH` lines specifying job parameters.
3. The program code (starts at the first non-comment line; after that no more #SBATCH is read).

Example:
```
#!/usr/bin/zsh
#SBATCH --ntasks=8
#SBATCH --time=00:15:00
#SBATCH --job-name=example_job
#SBATCH --output=stdout.txt
#SBATCH --account=<project-id>   # or delete the line
srun hostname
```

## Submit and monitor
- `sbatch batch_script.sh` → returns a job id (e.g. "Submitted batch job 12345678").
- The directory you run `sbatch` from becomes the working directory.
- `squeue --me` → your pending (PD) and running (R) jobs. Gone from the list = finished.

## Best practices
- Test on a login node first; put all start commands (incl. module loads + shebang) in a script.
- Don't load modules in your `.zshrc`/`.bashrc`.
- Use the `devel` partition / short 5-minute time first so failures happen fast.
- Long computations → split into chain jobs. Parameter sweeps → array jobs.
- Use full explicit paths for `--output` (do NOT use `~` or `$HOME`).
