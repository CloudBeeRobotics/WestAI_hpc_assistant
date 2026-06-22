"""
bundle.py — build a downloadable project ZIP that implements the full round-trip
the team wants with NO commands to memorise:

  laptop:  unzip -> ./scripts/local_setup.sh   (git init + commit + push)
  HPC:     ./scripts/hpc_pull_run.sh            (clone/pull + sbatch + squeue)
  HPC(1x): ./scripts/hpc_filesystem_setup.sh    (build shared project folders)

The zip contains a proper, ready-to-run feature folder with a tuned Slurm job.
"""

import io
import zipfile

import features as ft
import slurm_gen as sg

DEFAULT_REMOTE = "git@github.com:CloudBeeRobotics/WestAI_hpc_assistant.git"
REPOS_ROOT = "/work/rwth2125/repos"


def _local_setup(feature, remote):
    return f"""#!/usr/bin/env bash
# Run on your LAPTOP, from inside this folder. Creates the git repo and pushes it.
# Usage: ./scripts/local_setup.sh [git-remote-url]
set -euo pipefail
REMOTE="${{1:-{remote}}}"

cd "$(dirname "$0")/.."           # repo root (this folder)
git init -q
git add .
git commit -q -m "Add {feature} feature scaffold (WestAI HPC Assistant)" || echo "nothing to commit"
git branch -M main
git remote add origin "$REMOTE" 2>/dev/null || git remote set-url origin "$REMOTE"
git push -u origin main
echo "Pushed to $REMOTE (branch main)."
"""


def _hpc_pull_run(feature, remote):
    return f"""#!/usr/bin/zsh
# Run on an HPC LOGIN node. Pulls the latest code and submits the job.
# Usage: ./scripts/hpc_pull_run.sh [git-remote-url]
REMOTE="${{1:-{remote}}}"
mkdir -p {REPOS_ROOT}
cd {REPOS_ROOT}

if [ -d "{feature}/.git" ]; then
  cd {feature} && git pull --ff-only
else
  git clone "$REMOTE" {feature} && cd {feature}
fi

mkdir -p logs
sbatch slurm/run.sh
squeue --me
echo "Submitted. Watch with: squeue --me   |   logs in {REPOS_ROOT}/{feature}/logs/"
"""


def _hpc_fs_setup():
    return """#!/usr/bin/zsh
# Run ONCE on an HPC login node to build the shared project folder layout.
# Project dirs already have setgid + umask 007, so files are group-shared.
set -e
echo ">> groups:"; groups
echo ">> project quota:"; r_quota -u rwth2125 || true

mkdir -p /work/rwth2125/{repos,docker,docs}
mkdir -p /hpcwork/rwth2125/{datasets,models,checkpoints,results,logs}

echo ">> Created:"
echo "   /work/rwth2125/{repos,docker,docs}"
echo "   /hpcwork/rwth2125/{datasets,models,checkpoints,results,logs}"
ls -ld /work/rwth2125/repos /hpcwork/rwth2125/datasets
"""


def _readme(feature, user, remote, gpus, time):
    return f"""# {feature} — WestAI HPC Assistant bundle

Owner: {user} · Project rwth2125 · CLAIX-2023 (c23g / H100)
Resources: {gpus} GPU, {time}

## Workflow (no commands to memorise)

1. **On your laptop** — create the repo and push:
   ```bash
   ./scripts/local_setup.sh {remote}
   ```
2. **On an HPC login node** — pull and run:
   ```bash
   ./scripts/hpc_pull_run.sh {remote}
   ```
3. (Once per project) build shared storage on HPC:
   ```bash
   ./scripts/hpc_filesystem_setup.sh
   ```

Monitor: `squeue --me` · efficiency after finish: `seff <jobid>`

## Contents
- `slurm/run.sh` — tuned sbatch job for this feature
- `{ft.FEATURES[feature]['command'].split()[0] if feature in ft.FEATURES else 'src'}` entrypoint, `configs/`, `.gitignore`
- `scripts/` — local_setup, hpc_pull_run, hpc_filesystem_setup
"""


def build_bundle(feature="custom", user="mayur", gpus=None, time=None,
                 remote=DEFAULT_REMOTE):
    """Return (filename, zip_bytes) for the feature project bundle."""
    feature = (feature or "custom").lower()
    if feature not in ft.FEATURES:
        raise ValueError(f"unknown feature '{feature}'")
    prof = ft.FEATURES[feature]
    gpus = int(gpus) if gpus else prof["gpus"]
    time = time or prof["time"]
    remote = remote or DEFAULT_REMOTE
    pkg = feature.replace("-", "_")

    run_sh = sg.generate_script(user=user, mode="production", gpus=gpus,
                                time=time, job_name=feature, command=prof["command"])

    root = feature
    files = {
        f"{root}/README.md": _readme(feature, user, remote, gpus, time),
        f"{root}/slurm/run.sh": run_sh,
        f"{root}/scripts/local_setup.sh": _local_setup(feature, remote),
        f"{root}/scripts/hpc_pull_run.sh": _hpc_pull_run(feature, remote),
        f"{root}/scripts/hpc_filesystem_setup.sh": _hpc_fs_setup(),
        f"{root}/{pkg}/__init__.py": "",
        f"{root}/{pkg}/run.py": (
            f'"""Entrypoint for {feature}. Keep importable for phase-2 webapp '
            f'integration."""\n\n\ndef main():\n    print("{feature}: TODO")\n\n\n'
            f'if __name__ == "__main__":\n    main()\n'),
        f"{root}/configs/default.yaml": f"# {feature} config\n",
        f"{root}/.gitignore": "data/\nlogs/\n*.ckpt\n__pycache__/\n*.pyc\n",
    }

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for path, content in files.items():
            info = zipfile.ZipInfo(path)
            # make shell scripts executable inside the zip (rwxr-xr-x)
            info.external_attr = (0o755 if path.endswith(".sh") else 0o644) << 16
            z.writestr(info, content)
    buf.seek(0)
    return f"{feature}_bundle.zip", buf.getvalue()
