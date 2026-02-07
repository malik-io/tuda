#!/usr/bin/env python3
"""Hardware/driver pre-flight checks for local quantized inference."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

LOG_PATH = Path(__file__).resolve().parent / "hardware_profile.log"
MIN_VRAM_MB = 4096


def _run(cmd: List[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "command failed")
    return proc.stdout.strip()


def _safe_torch_info() -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "available": False,
        "cuda_version": None,
        "gpus": [],
    }
    try:
        import torch

        info["available"] = bool(torch.cuda.is_available())
        info["cuda_version"] = torch.version.cuda
        if torch.cuda.is_available():
            for idx in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(idx)
                info["gpus"].append(
                    {
                        "index": idx,
                        "name": props.name,
                        "total_memory_mb": int(props.total_memory / (1024 * 1024)),
                        "compute_capability": f"{props.major}.{props.minor}",
                    }
                )
    except Exception as exc:  # pragma: no cover - optional dependency
        info["torch_error"] = str(exc)

    return info


def _nvidia_smi_info() -> Dict[str, Any]:
    try:
        csv = _run(
            [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,driver_version,compute_cap",
                "--format=csv,noheader,nounits",
            ]
        )
    except Exception as exc:
        return {"available": False, "error": str(exc), "gpus": []}

    gpus = []
    driver_version = None
    for line in csv.splitlines():
        idx, name, mem_total, driver_version, compute_cap = [p.strip() for p in line.split(",")]
        gpus.append(
            {
                "index": int(idx),
                "name": name,
                "total_memory_mb": int(mem_total),
                "compute_capability": compute_cap,
            }
        )

    return {
        "available": True,
        "driver_version": driver_version,
        "gpus": gpus,
    }


def compute_profile() -> Dict[str, Any]:
    torch_info = _safe_torch_info()
    smi_info = _nvidia_smi_info()

    merged_gpus: Dict[int, Dict[str, Any]] = {}
    for src in (smi_info.get("gpus", []), torch_info.get("gpus", [])):
        for gpu in src:
            merged_gpus.setdefault(gpu["index"], {}).update(gpu)

    gpu_list = [merged_gpus[i] for i in sorted(merged_gpus)]
    has_cuda = torch_info.get("available") or smi_info.get("available")
    min_vram_ok = any(g.get("total_memory_mb", 0) >= MIN_VRAM_MB for g in gpu_list)

    mode = "gpu" if has_cuda and min_vram_ok else "cpu"
    warning = None
    if mode == "cpu":
        warning = "Consciousness will be slow"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runtime_mode": mode,
        "warning": warning,
        "requirements": {"min_vram_mb": MIN_VRAM_MB},
        "cuda_detected": bool(has_cuda),
        "vram_requirement_met": bool(min_vram_ok),
        "torch": torch_info,
        "nvidia_smi": smi_info,
        "gpus": gpu_list,
    }


def write_log(profile: Dict[str, Any]) -> Path:
    LOG_PATH.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    return LOG_PATH


def main() -> int:
    profile = compute_profile()
    log_path = write_log(profile)

    print(f"Runtime mode: {profile['runtime_mode']}")
    if profile["warning"]:
        print(f"Warning: {profile['warning']}")
    print(f"Hardware profile written to: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
