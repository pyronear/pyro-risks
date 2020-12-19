# C3S ECMWF - ERA5-Land

![](https://climate.copernicus.eu/sites/default/files/inline-images/AnimatedFigure.gif)
*The resolution enhancement for daily surface temperature: typical climate model 2°x2°, ERA5 0.25°x0.25 and ERA-Land 0.1°x0.1°. [Credit: Copernicus Climate Change Service/ECMWF](https://climate.copernicus.eu/high-resolution-climate-projections)*

<!--Soil temperatures in ERA-Interim, ERA5 and ERA5-Land. The charts show soil temperature of the top 7 cm of soil at 12 UTC on 15 March 2010 according to ERA-Interim (79 km grid spacing, left), ERA5 (31 km grid spacing, middle), and ERA5-Land (9 km grid spacing, right). (Credit: Copernicus Climate Change Service, ECMWF)-->

The ERA5-Land is a reanalysis dataset consistent with atmospheric data from the ERA5 reanalysis from 1950 onward. The ERA5-Land is produced by the European Center for Medium Range Weather Forecast (ECMWF) and distributed by the Copernicus Climate Change Service (C3S).

The ERA5-Land dataset provides global, hourly, historic and high-resolution (9 km) land-focused information for a more accurate representation of water and energy cycles. ERA5-Land is **updated monthly** with a **delay of about three months relatively to actual date**.

<!--https://climate.copernicus.eu/copernicus-releases-new-dataset-land-observation-->

## Technical Background

>*“Climate reanalyses combine past observations with models to generate consistent time series of multiple climate variables. Reanalyses are among the most-used datasets in the geophysical sciences. They provide a comprehensive description of the observed climate as it has evolved during recent decades, on 3D grids at sub-daily intervals.“ [Copenicus Climate Change Services](https://climate.copernicus.eu/climate-reanalysis)*

ECMWF short introductions to numerical weather prediction can be found in the following articles:

* *[Climate Reanalysis](https://www.ecmwf.int/en/research/climate-reanalysis)*
* *[Data Assimilation](https://www.ecmwf.int/en/research/data-assimilation)*
* *[Modeling and Prediction](https://www.ecmwf.int/en/research/modelling-and-prediction)*
  

## Downloading Dataset

***Copernicus Climate Data Store (CDS):*** You can access the ERA5-Land dataset via the Climate Data Store [ERA5-Land hourly data from 1981 to present](https://doi.org/10.24381/cds.e2161bac) page.

**ERA5T dataset used in Pyro-Risks Training**

<!--TODO PRECISIONS ON THE EXACT DATASET USED FOR TRAINING (temporal coverage and date of download)-->

```python
from pyro_risks.datasets import ERA5Land
era_land = ERA5Land()
```
<!--PRECISIONS ON THE EXACT DATASET USED FOR TRAINING-->

## Datasets Descriptions

| DATA DESCRIPTION |  |
|-|-|
| Data type | Gridded |
| Horizontal coverage | Global |
| Horizontal resolution | 0.1°x0.1°; Native resolution is 9 km. |
| Vertical coverage | From 2 m above the surface level, to a soil depth of 289 cm. |
| Vertical resolution | 4 levels of the ECMWF surface model: Layer 1: 0 -7cm,<br>Layer 2: 7 -28cm, Layer 3: 28-100cm, Layer 4: 100-289cm <br>Some parameters are defined at 2 m over the surface. |
| Temporal coverage | January 1981 to present |
| Temporal resolution | Hourly |
| File format | GRIB |
| Update frequency | Monthly with a delay of about three months relatively to actual date. |

Full description of the dataset variables is available on the Copernicus Climate Data Store [ERA5-Land hourly data from 1981 to present](https://doi.org/10.24381/cds.e2161bac) page. Further descriptions on the ERA5-Land dataset can be found in the ECMWF [ERA5-Land online documentation](https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation).

## Acknowledgments

We acknowledge the use of data generated using Copernicus Climate Change Service information 2020.
