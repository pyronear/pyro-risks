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
Beforehand, you will need to set a few environment variables either manually or by writing an `.env` file in the root directory of this project, like in the example below:

```
CDS_UID=my_secret_uid
CDS_API_KEY=my_very_secret_key
```
Those values will allow your web server to connect to CDS [API](https://github.com/ecmwf/cdsapi), which is mandatory for your datasets access to be fully operational.

## Importing publicly available datasets

Access the main pyro-risks datasets locally. 

```python
from pyro_risks.datasets import NASAFIRMS, NASAFIRMS_VIIRS, GwisFwi, ERA5T, ERALand

modis = NASAFIRMS()
viirs = NASAFIRMS_VIIRS()

fdi = GwisFwi()

era = ERA5T()
era_land = ERA5Land()
```

## Running examples scripts

You are free to merge the datasets however you want and to implement any relevant zonal statistic, but some are already provided for reference. In order to use them check the example scripts options as follows:

```shell
python scripts/example_ERA5_FIRMS.py --help
```

You can then run the script with your own arguments:

```shell
python scripts/example_ERA5_FIRMS.py --type_of_merged departements
```

## Running the web server

To be able to expose model inference, you can run a web server using docker containers with this command:

```bash
PORT=8003 docker-compose up -d --build
```

Once completed, you will notice that you have a docker container running on the port you selected, which can process requests just like any web server.