pyro_risks.datasets
###################

The datasets submodule contains datasets with entries indexed by location and datetime, to help prediction outbreak 
risks and wildfire evolution. Using those datasets means that you comply with the usage restrictions from the 
corresponding authors.

The following datasets are available:

.. contents:: Models
    :local:

.. currentmodule:: pyro_risks.datasets


Region tiling
==============

GPS coordinates often need to be mapped for later aggregation.
These tools are meant to help with the aggregation process by defining sub-areas in a country or geographical area.


France
------

.. autofunction:: get_french_geom



Weather data
============

Weather information about specific locations over a predefined time range.


France
------

.. autoclass:: NOAAWeather



Wildfire history
================

The frequency and intensity of wildfire in some areas can be a key indicator about future risks.


France
------

.. autoclass:: BDIFFHistory
