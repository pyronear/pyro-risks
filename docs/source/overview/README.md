# Package installation

## Prerequisites

-   Python 3.6 (or more recent)
-   [pip](https://pip.pypa.io/en/stable/)

## Installation

You can install the package from github as follows:

```shell
pip install git+https://github.com/pyronear/pyro-risks
```

# Package usage

## Importing publicly available datasets

Access all pyro-risks datasets. 

```python
from pyro_risks.datasets import NASAFIRMS, NOAAWeather
firms = NASAFIRMS()
noaa = NOAAWeather()
```

## Running examples scripts

You are free to merge the datasets however you want and to implement any zonal statistic you want, but some are already provided for reference. In order to use them check the example scripts options as follows:

```shell
python scripts/example_ERA5_FIRMS.py --help
```

You can then run the script with your own arguments:

```shell
python scripts/example_ERA5_FIRMS.py --type_of_merged departements
```