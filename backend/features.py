"""
features.py — registry of the features the team builds, each with sensible
default HPC resources and a repo scaffold. The user picks a feature (in the UI
form or via chat) and we help create the standalone repo + a tuned Slurm script.

This matches the two-phase workflow: build each feature in its own repo first,
then integrate into the webapp later.
"""

import slurm_gen as sg

REPOS_ROOT = "/work/rwth2125/repos"

# key -> profile. gpus/time are *defaults*; the user can override.
FEATURES = {
    "dataforge": {
        "label": "DataForge (multimodal dataset generation)",
        "gpus": 1, "time": "04:00:00",
        "command": "python -m dataforge.run --config configs/default.yaml",
        "blurb": "GroundingSAM2 → tracking → cuVSLAM → NVBlox → 3D → VLM → scene/capability graph.",
    },
    "grounding_sam2": {
        "label": "GroundingSAM2 (open-vocab segmentation)",
        "gpus": 1, "time": "02:00:00",
        "command": "python -m grounding_sam2.run --images data/images",
        "blurb": "Text-prompted detection + segmentation.",
    },
    "nvblox": {
        "label": "NVBlox (3D reconstruction)",
        "gpus": 1, "time": "02:00:00",
        "command": "python -m nvblox_pipeline.run --rgbd data/rgbd",
        "blurb": "GPU volumetric mapping from RGB-D.",
    },
    "cuvslam": {
        "label": "cuVSLAM (visual SLAM, CPU-heavy)",
        "gpus": 1, "time": "02:00:00",
        "command": "python -m cuvslam_pipeline.run --seq data/seq01",
        "blurb": "Visual-inertial odometry / SLAM.",
    },
    "vlm_inference": {
        "label": "VLM inference (Qwen-VL / InternVL)",
        "gpus": 1, "time": "04:00:00",
        "command": "python -m vlm.serve --model Qwen/Qwen2-VL-7B-Instruct",
        "blurb": "Vision-language model inference / serving.",
    },
    "finetune": {
        "label": "Fine-tuning (multi-GPU)",
        "gpus": 4, "time": "24:00:00",
        "command": "torchrun --standalone --nproc_per_node=4 train.py",
        "blurb": "Distributed fine-tuning across H100s.",
    },
    "webapp": {
        "label": "Webapp (integrate a feature / extend the assistant)",
        "gpus": 1, "time": "04:00:00",
        "command": "./run.sh",
        "blurb": "Phase-2 integration: run the assistant webapp and plug a finished feature in as a tool.",
    },
    "custom": {
        "label": "Custom / new feature",
        "gpus": 1, "time": "04:00:00",
        "command": "python main.py",
        "blurb": "Blank starting point for a brand-new feature repo.",
    },
}


def list_features():
    """Return a UI-friendly list for the frontend dropdown."""
    return [
        {"key": k, "label": v["label"], "gpus": v["gpus"],
         "time": v["time"], "blurb": v["blurb"]}
        for k, v in FEATURES.items()
    ]


def scaffold_feature(feature="custom", user="mayur", gpus=None, time=None):
    """Return a bash snippet that creates a standalone repo for the feature
    under /work/rwth2125/repos, including a tuned sbatch script and dev salloc."""
    feature = (feature or "custom").lower()
    if feature not in FEATURES:
        raise ValueError(f"unknown feature '{feature}'. Choose: {', '.join(FEATURES)}")
    f = FEATURES[feature]
    gpus = int(gpus) if gpus else f["gpus"]
    time = time or f["time"]
    cmd = f["command"]
    pkg = feature.replace("-", "_")

    # Webapp = phase-2 integration work, not a new data repo.
    if feature == "webapp":
        uname = sg.TEAM.get((user or "mayur").lower(), ("<user>",))[0]
        return f"""# ── Work on the assistant webapp (phase-2 integration) ──
# Run it locally:
cd {REPOS_ROOT}/hpc-assistant/webapp   # or wherever this repo lives
./run.sh                               # http://localhost:8000

# Integrate a FINISHED feature as a new LLM tool:
#  1) create backend/tools/<feature>.py that wraps the feature repo's entrypoint
#  2) define its TOOL schema + a handler that runs it
#  3) register it so app.py picks it up
#
# Run the webapp on a GPU node + reach it from your laptop:
{sg.generate_salloc(user=user, gpus=gpus, time=time).splitlines()[1]}
# then on the node:  cd webapp && PORT=8000 ./run.sh
# on your laptop:    ssh -J {uname}@{sg.LOGIN_NODE} -L 8000:localhost:8000 {uname}@<compute-node>
"""

    # tuned production sbatch + dev salloc reused from the deterministic generators
    sbatch = sg.generate_script(user=user, mode="production", gpus=gpus,
                                time=time, job_name=feature, command=cmd)
    salloc = sg.generate_salloc(user=user, gpus=gpus, time="04:00:00")
    salloc_oneline = salloc.splitlines()[1]  # the bare salloc command

    repo = f"{REPOS_ROOT}/{feature}"
    return f"""# ── Scaffold the "{feature}" feature repo ({f['label']}) ──
# {f['blurb']}
# Run these on a LOGIN node.

cd {REPOS_ROOT}
mkdir -p {feature}/{{{pkg},configs,data,slurm,logs,tests}}
cd {repo}
git init -q

# minimal Python package + entrypoint
touch {pkg}/__init__.py
cat > {pkg}/run.py <<'PY'
\"\"\"Entrypoint for the {feature} feature. Keep this importable so the webapp
can call it later during integration (phase 2).\"\"\"

def main():
    print("{feature}: TODO implement")

if __name__ == "__main__":
    main()
PY

cat > requirements.txt <<'TXT'
# pin your deps here
TXT

cat > configs/default.yaml <<'YML'
# {feature} config
YML

cat > README.md <<'MD'
# {feature}

{f['blurb']}

## Run
\\`\\`\\`bash
sbatch slurm/run.sh        # production on c23g
\\`\\`\\`
MD

cat > .gitignore <<'GI'
data/
logs/
*.ckpt
__pycache__/
GI

# tuned Slurm production script for this feature
mkdir -p slurm logs
cat > slurm/run.sh <<'SBATCH'
{sbatch}SBATCH
chmod +x slurm/run.sh

echo "Created {repo}"
echo
echo "Develop interactively first:"
echo '{salloc_oneline}'
"""


SCAFFOLD_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "scaffold_feature",
        "description": (
            "Create a standalone repo skeleton for a feature the user is working "
            "on (under /work/rwth2125/repos), with a tuned sbatch script and dev "
            "salloc command. Call this when the user picks a feature or says they "
            "want to start/scaffold/set up work on something."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "feature": {"type": "string", "enum": list(FEATURES.keys()),
                            "description": "Which feature to scaffold."},
                "user": {"type": "string", "enum": ["mayur", "madhava"]},
                "gpus": {"type": "integer", "minimum": 1, "maximum": 4,
                         "description": "Override default GPU count."},
                "time": {"type": "string", "description": "Override wall time."},
            },
            "required": ["feature"],
        },
    },
}
