<h1 align="center">Pyronear Risks</h1>
<p align="center">
    <a href="LICENSE" alt="License">
        <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" /></a>
    <a href="https://github.com/pyronear/pyro-risks/actions?query=workflow%3Apython-package">
        <img src="https://github.com/pyronear/pyro-risks/workflows/python-package/badge.svg" /></a>
   <a href="https://www.codacy.com/gh/pyronear/pyro-risks/dashboard?utm_source=github.com&utm_medium=referral&utm_content=pyronear/pyro-risks&utm_campaign=Badge_Grade">
        <img src="https://camo.githubusercontent.com/6361a174bbd36acd5ee8c24b0ef27ba6a84803c2ac9354d57d60d1264d78a31a/68747470733a2f2f6170702e636f646163792e636f6d2f70726f6a6563742f62616467652f47726164652f6532623936393836356539663439633561623934343435643765346132613637" /></a>
    <a href="https://codecov.io/gh/pyronear/pyro-risks">
  		<img src="https://codecov.io/gh/pyronear/pyro-risks/branch/master/graph/badge.svg" /></a>
    <a href="https://github.com/psf/black">
        <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
    <a href="https://pyronear.github.io/pyro-risks">
  		<img src="https://img.shields.io/badge/docs-available-blue.svg" /></a>
</p>

The pyro-risks project aims at providing the pyronear-platform with a machine learning based wildfire forecasting capability. 

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Getting started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Web server](#web-server)
- [Examples](#examples)
  - [datasets](#datasets)
  - [Scripts](#scripts)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)

## Getting started

### Prerequisites

-   Python 3.6 (or more recent)
-   [pip](https://pip.pypa.io/en/stable/)
### Installation

You can install the package from github as follows:

```shell
pip install git+https://github.com/pyronear/pyro-risks
```

## Usage

Beforehand, you will need to set a few environment variables either manually or by writing an `.env` file in the root directory of this project, like in the example below:

```
CDS_UID=my_secret_uid
CDS_API_KEY=my_very_secret_key
```
Those values will allow your web server to connect to CDS [API](https://github.com/ecmwf/cdsapi), which is mandatory for your datasets access to be fully operational.

### Web server

To be able to expose model inference, you can run a web server using docker containers with this command:

```bash
PORT=8003 docker-compose up -d --build
```

Once completed, you will notice that you have a docker container running on the port you selected, which can process requests just like any web server.

## Examples
### datasets

Access the main pyro-risks datasets locally. 

```python
from pyro_risks.datasets import NASAFIRMS, NASAFIRMS_VIIRS, GwisFwi, ERA5T, ERALand

modis = NASAFIRMS()
viirs = NASAFIRMS_VIIRS()

fdi = GwisFwi()

era = ERA5T()
era_land = ERA5Land()
```
### Scripts

You are free to merge the datasets however you want and to implement any zonal statistic you want, but some are already provided for reference. In order to use them check the example scripts options as follows:

```shell
python scripts/example_ERA5_FIRMS.py --help
```

You can then run the script with your own arguments:

```shell
python scripts/example_ERA5_FIRMS.py --type_of_merged departements
```

## Documentation

The full package documentation is available [here](https://pyronear.org/pyro-risks/) for detailed specifications. The documentation was built with [Sphinx](https://www.sphinx-doc.org) using a [theme](https://github.com/readthedocs/sphinx_rtd_theme) provided by [Read the Docs](https://readthedocs.org).

## Contributing

Please refer to the [`CONTRIBUTING`](./CONTRIBUTING.md) guide if you wish to contribute to this project.

## Credits

This project is developed and maintained by the repo owner and volunteers from [Data for Good](https://dataforgood.fr/).

## License

Distributed under the GPLv3 Licenses. See [`LICENSE`](./LICENSE) for more information.
