# UV vs Poetry — Docker Build Benchmark

Measures cold Docker build times for UV and Poetry across three dependency tiers. Results are tracked in MLflow.

## Experiment tiers

| Tier   | Packages |
|--------|----------|
| light  | requests, pydantic |
| medium | + numpy, pandas |
| heavy  | + matplotlib, scikit-learn, transformers, datasets, accelerate |

Each tier inherits all packages from the previous one.

## Setup

```bash
pip install -r requirements.txt
```

Docker must be running.

## Run

```bash
python benchmark.py
```

Then open MLflow UI to explore results:

```bash
mlflow ui
# → http://localhost:5000
```

## Regenerate lock files

```bash
bash generate_locks.sh
```

Requires both `uv` and `poetry` installed locally.

## Project structure

```
experiments/
  light/
    uv/      pyproject.toml, uv.lock, Dockerfile
    poetry/  pyproject.toml, poetry.lock, Dockerfile
  medium/    (same structure)
  heavy/     (same structure)
benchmark.py       runner + MLflow logging
requirements.txt   benchmark runner deps
generate_locks.sh  regenerate all lock files
```
