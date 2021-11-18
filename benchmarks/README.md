# Benchmark install time

1. In a Python interpreter with a supported Python version ([see currently supported versions](../README.md#installation)), download and install SimulariumIO and all its dependencies by running `conda install readdy` and then `pip install simulariumio[all] --no-cache-dir`.

### 11/18/21
**Environment**: 2019 MacBook Pro, SimulariumIO 1.4.0, Python 3.9, 100 Mbps connection
- With all dependencies (step #1 above): ~2.5 minutes
- With only base dependencies (`pip install simulariumio --no-cache-dir`): ~20 seconds

# Benchmark conversion time

1. Unless you've already downloaded them, download benchmark files by running `download_benchmark_resources.py` in a Python interpreter with `simulariumio[benchmark]` installed. The files will be saved to `benchmarks/resources`.
2. Run `benchmark_simulariumio.py` 

### 11/18/21
**Environment**: 2019 MacBook Pro, SimulariumIO 1.4.0, Python 3.9
- 1GB Cytosim file
  - Conversion ran in ~2.5 minutes
  - Total time (including write to file) was ~5 minutes
- 50MB SpringSaLaD file
  - Conversion ran in ~10 seconds
  - Total time (including write to file) was ~45 seconds