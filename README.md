# Simpipe: N-body Cosmological Simulation Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Simpipe is a streamlined pipeline for running Gadget-4 N-body cosmological simulations on high-performance computing environments. It automates the setup, configuration, and execution of simulations on clusters like S3DF and Sherlock.

## Features

- **Multiple HPC Environments**: Support for Sherlock 3/4 and S3DF computing clusters
- **Automated Setup**: Handles Gadget-4 configuration, compilation, and job submission
- **Optimized Performance**: Pre-configured benchmarks for different systems
- **Flexible Configuration**: Easily adjust simulation parameters like particle count, box size, etc.
- **Resource Management**: Automatic memory requirement estimation based on simulation size

## Prerequisites

- Access to Sherlock or S3DF computing clusters
- Basic knowledge of cosmological simulations
- Python 3.6+

## Quick Start

```bash
# Clone the repository
git clone https://github.com/marcelo-alvarez/simpipe.git

# Set up the environment
source simpipe/scripts/load-env.sh

# Set your email for job notifications
export EMAIL=your_email_address

# Run a simulation with default parameters
python simpipe/py/makesim.py
```

## Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--N` | Number of particles per dimension | 1024 |
| `--Npm` | PM grid size | 2048 |
| `--boxsize` | Simulation box size in Mpc/h | 200 |
| `--Ntasks` | Number of MPI tasks | 96 |
| `--system` | Computing environment | Auto-detected |
| `--z_in` | Initial redshift | 99 |
| `--z_out` | Output redshift | 0 |

## Example Usage

### Basic Simulation

```bash
python simpipe/py/makesim.py --N 1024 --Npm 2048 --boxsize 200 --Ntasks 96
```

### High-Resolution Simulation

```bash
python simpipe/py/makesim.py --N 2048 --Npm 4096 --boxsize 500 --Ntasks 384
```

### Specifying Computing Environment

```bash
python simpipe/py/makesim.py --system s3df-milano --N 1024 --Ntasks 192
```

## Pipeline Structure

When you run a simulation, Simpipe:

1. Creates a run directory with a unique identifier
2. Downloads and configures Gadget-4 if needed
3. Generates appropriate parameter files based on your inputs
4. Estimates required computational resources
5. Creates and submits a job to the cluster scheduler
6. Provides monitoring information

## Supported Systems

- `sh3-cbase`: Sherlock 3 with cbase partition
- `sh4-cscale`: Sherlock 4 with cscale partition
- `sh4-cbase`: Sherlock 4 with cbase partition
- `s3df-milano`: S3DF with milano nodes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The Gadget-4 team for developing the N-body simulation code
- SLAC and Stanford for providing HPC resources