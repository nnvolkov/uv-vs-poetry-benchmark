#!/usr/bin/env python3
"""Benchmark comparing UV vs Poetry Docker build times across dependency tiers."""

import subprocess
import time
from pathlib import Path

import mlflow

EXPERIMENTS = [
    {
        "name": "light",
        "packages": "requests, pydantic",
        "package_count": 2,
    },
    {
        "name": "medium",
        "packages": "requests, pydantic, numpy, pandas",
        "package_count": 4,
    },
    {
        "name": "heavy",
        "packages": "requests, pydantic, numpy, pandas, matplotlib, scikit-learn",
        "package_count": 6,
    },
]

TOOLS = ["uv", "poetry"]


def run_command(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def get_image_size_mb(image_name: str) -> float:
    result = run_command(
        ["docker", "image", "inspect", image_name, "--format", "{{.Size}}"]
    )
    if result.returncode != 0 or not result.stdout.strip():
        return 0.0
    return int(result.stdout.strip()) / (1024 * 1024)


def remove_image(image_name: str) -> None:
    run_command(["docker", "rmi", "-f", image_name])


def build_image(tool: str, experiment: str) -> dict:
    image_name = f"benchmark-{tool}-{experiment}-{int(time.time())}"
    context_path = Path(f"experiments/{experiment}/{tool}")

    print(f"    Building {image_name} ...")

    start = time.perf_counter()
    result = run_command(
        [
            "docker",
            "build",
            "--no-cache",
            "--progress=plain",
            "-t",
            image_name,
            str(context_path),
        ]
    )
    duration = time.perf_counter() - start

    success = result.returncode == 0
    size_mb = get_image_size_mb(image_name) if success else 0.0

    if not success:
        print("    BUILD FAILED — last 2000 chars of stderr:")
        print(result.stderr[-2000:])

    remove_image(image_name)

    return {
        "duration": duration,
        "size_mb": size_mb,
        "success": success,
    }


def main():
    mlflow.set_tracking_uri("mlruns")
    experiment_obj = mlflow.set_experiment("uv-vs-poetry-docker-benchmark")

    print("UV vs Poetry — Docker Build Time Benchmark")
    print("=" * 62)
    print(f"MLflow experiment: {experiment_obj.name}")
    print()

    all_results: list[dict] = []

    for exp in EXPERIMENTS:
        print(f"Experiment: {exp['name'].upper()}  ({exp['packages']})")
        print("-" * 62)

        for tool in TOOLS:
            print(f"  [{tool.upper()}]")

            with mlflow.start_run(run_name=f"{tool}-{exp['name']}"):
                mlflow.log_param("tool", tool)
                mlflow.log_param("experiment", exp["name"])
                mlflow.log_param("packages", exp["packages"])
                mlflow.log_param("package_count", exp["package_count"])

                build_result = build_image(tool, exp["name"])

                mlflow.log_metric("build_time_seconds", build_result["duration"])
                mlflow.log_metric("image_size_mb", build_result["size_mb"])
                mlflow.log_metric("success", int(build_result["success"]))

                all_results.append(
                    {"tool": tool, "experiment": exp["name"], **build_result}
                )

                status = "OK" if build_result["success"] else "FAILED"
                print(
                    f"    time={build_result['duration']:.2f}s  size={build_result['size_mb']:.1f}MB  [{status}]"
                )

        print()

    print("=" * 62)
    print(f"{'Experiment':<12} {'Tool':<10} {'Time (s)':<12} {'Size (MB)':<12} Status")
    print("-" * 62)
    for r in all_results:
        status = "OK" if r["success"] else "FAILED"
        print(
            f"{r['experiment']:<12} {r['tool']:<10} {r['duration']:<12.2f} {r['size_mb']:<12.1f} {status}"
        )

    print()
    print("View results: mlflow ui  → http://localhost:5000")


if __name__ == "__main__":
    main()
