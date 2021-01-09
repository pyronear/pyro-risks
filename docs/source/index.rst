Pyronear Wildfire Risk Forecasting Documentation
================================================

.. raw:: html

      <p >
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
      </p>

The pyro-risks project aims at providing the pyronear-platform with a machine learning based wildfire forecasting capability.
The :mod:`pyro_risks` package aggregates pre-processing pipelines and models for wildfire forecasting.


.. toctree::
   :maxdepth: 2   
   :caption: Getting Started

   overview/README

.. toctree::
   :maxdepth: 1
   :caption: Publicly Available Datasets

   overview/datasets/NASA-FIRMS_ACTIVE-FIRE_VIIRS
   overview/datasets/CEMS-ECMWF_FDI
   overview/datasets/C3S-ECMWF_ERA5T
   overview/datasets/C3S-ECMWF_ERA5LAND

.. toctree::
   :maxdepth: 1
   :caption: Pyro Risks Package References

   modules/datasets/modules
   modules/models/modules

.. automodule:: pyro_risks
   :members:


.. toctree::
   :maxdepth: 1
   :caption: Contributing

   overview/CONTRIBUTING

Acknowledgements
-----------------

This project is developed and maintained by the repo owner and volunteers from
`Data for Good <https://dataforgood.fr/>`_.

License
-------

This project is distributed under the GPLv3 Licenses. 
See `LICENSE <https://github.com/pyronear/pyro-risks/blob/master/LICENSE>`_ for more information.
