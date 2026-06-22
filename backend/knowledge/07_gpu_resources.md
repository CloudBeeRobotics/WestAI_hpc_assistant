# GPU Resources on CLAIX-2023 (c23g) and Project rwth2125

## Hardware
- GPU partition is **c23g**. Each node has **4× NVIDIA H100**, 80 GB VRAM each. No MIG slicing.
- VRAM is selected by GPU COUNT: 1 GPU = 80 GB, 2 = 160 GB, 3 = 240 GB, 4 = 320 GB (full node).
- One GPU is capped at ~24 CPUs and ~122 GB system RAM (one quarter of a node). Needing more CPU/RAM means requesting more GPUs.

## Project
- Project ID 160448917, group **rwth2125**, title: "Scalable Synthetic Experience, Multimodal Robotics Foundation Models, and World-Model-Based Autonomous Execution for Physical AI".
- GPU jobs: `#SBATCH --account=rwth2125` and `#SBATCH --partition=c23g`.
- devel test jobs: no `--account`.

## Sizing guidance
| Workload | GPU | CPU | RAM |
|----------|-----|-----|-----|
| GroundingSAM2 / NVBlox | 1 | 16–24 | 64 GB |
| VLM inference (Qwen-VL, InternVL) | 1 | 24 | 96 GB |
| Fine-tuning | 2–4 | 48–96 | 200+ GB |
| cuVSLAM (CPU-heavy) | 0–1 | 16–24 | 32 GB |
| DataForge daily dev | 1 | 24 | 64–96 GB |

## Interactive GPU session
`salloc --account=rwth2125 --partition=c23g --gres=gpu:1 --cpus-per-task=24 --time=04:00:00`
Then `module load CUDA`, `nvidia-smi`.

## GPU / CUDA diagnostics (on a compute node only)
- `nvidia-smi` — usage, memory, driver version, processes. `nvidia-smi -l 2` — live.
- `nvcc --version` — CUDA toolkit version.
- `python -c "import torch;print(torch.cuda.is_available(), torch.version.cuda)"`.

## Software (no root)
- No `sudo`/`apt`. Use modules: `module spider <name>`, `module load <name>`, `module list`, `module purge`.
- Docker is usually unavailable (needs root). Use **Apptainer**: `module load Apptainer`, `apptainer run --nv image.sif` (`--nv` exposes GPUs). No docker-compose equivalent.
