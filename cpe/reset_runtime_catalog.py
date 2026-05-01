#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    sample_path = base_dir / "samples" / "procurement_capabilities.sample.json"
    runtime_dir = base_dir / "runtime"
    runtime_dir.mkdir(exist_ok=True)
    runtime_path = runtime_dir / "procurement_capabilities.runtime.json"
    shutil.copyfile(sample_path, runtime_path)
    print(f"reset runtime catalog: {runtime_path}")


if __name__ == "__main__":
    main()
