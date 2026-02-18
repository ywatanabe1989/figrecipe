# Container Definitions

This directory contains container definition files for FigRecipe.

## Available Containers

| Container | Purpose | Format |
|-----------|---------|--------|
| `Dockerfile` | Base figrecipe environment | Docker |
| `Dockerfile.gui` | Browser-based figure editor | Docker |

## Building Containers

### Base Container

```bash
docker build -t figrecipe -f scripts/containers/Dockerfile .
```

### GUI Container

```bash
docker build -f scripts/containers/Dockerfile.gui -t figrecipe-gui .
```

## Usage

### Base Container

```bash
# Run a Python script
docker run --rm -v $(pwd):/workspace figrecipe python3 my_plot.py

# Interactive shell
docker run --rm -it -v $(pwd):/workspace figrecipe
```

### GUI Container

```bash
# Launch editor
docker run --rm -p 5050:5050 -v $(pwd):/workspace figrecipe-gui

# Custom port
docker run --rm -p 8080:8080 -v $(pwd):/workspace figrecipe-gui --port 8080
```

### Docker Compose

```bash
FIGRECIPE_PROJECT_DIR=$(pwd) docker compose -f scripts/containers/docker-compose.gui.yml up
```

Then open http://localhost:5050 in your browser.
