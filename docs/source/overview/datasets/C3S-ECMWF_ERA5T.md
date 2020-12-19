# C3S ECMWF - ERA5T

![](https://climate.copernicus.eu/sites/default/files/inline-images/map_1month_anomaly_Global_ea_2t_201911_v02%20%281%29%20%281%29_1.png)
*C3S monthly surface air temperature bulletins, like this one for [November 2019](https://climate.copernicus.eu/surface-air-temperature-november-2019), rely on ERA5T data. [Credit: Copernicus Climate Change Service/ECMWF](https://climate.copernicus.eu/key-update-climate-dataset-brings-data-five-days-behind-real-time)*

The ERA5 is a climate reanalysis dataset produced by the European Center for Medium Range Weather Forecast (ECMWF) and distributed by the Copernicus Climate Change Service (C3S). 

The ERA5 dataset provides global hourly estimates of a large number of atmospheric, land and oceanic climate variables (surface air temperatures, precipitation, humidity, and soil moisture,  sea-ice temperature). ERA5 is updated daily with updates being available 5 days behind real time. In case that serious flaws are detected in this early release (called **ERA5T**), this data could be different from the final release **2 to 3 months later**.

## Technical Background

>*“Climate reanalyses combine past observations with models to generate consistent time series of multiple climate variables. Reanalyses are among the most-used datasets in the geophysical sciences. They provide a comprehensive description of the observed climate as it has evolved during recent decades, on 3D grids at sub-daily intervals.“ [Copenicus Climate Change Services](https://climate.copernicus.eu/climate-reanalysis)*

ECMWF short introductions to numerical weather prediction can be found in the following articles:

* *[Climate Reanalysis](https://www.ecmwf.int/en/research/climate-reanalysis)*
* *[Data Assimilation](https://www.ecmwf.int/en/research/data-assimilation)*
* *[Modeling and Prediction](https://www.ecmwf.int/en/research/modelling-and-prediction)*
  

## Downloading Dataset

***Copernicus Climate Data Store (CDS):*** You can access the ERA5T dataset via the Climate Data Store [ERA5 hourly data on single levels from 1979 to present](https://doi.org/10.24381/cds.adbb2d47) page.

**ERA5T dataset used in Pyro-Risks Training**

<!--TODO PRECISIONS ON THE EXACT DATASET USED FOR TRAINING (temporal coverage and date of download)-->

```python
from pyro_risks.datasets import ERA5T 
era = ERA5T()
```
<!--PRECISIONS ON THE EXACT DATASET USED FOR TRAINING-->

## Datasets Descriptions


| DATA DESCRIPTION |  |
|-|-|
| Data type | Gridded |
| Horizontal coverage | Global |
| Horizontal resolution | Reanalysis: 0.25°x0.25° (atmosphere), 0.5°x0.5° (ocean waves) Mean, <br>spread and members: 0.5°x0.5° (atmosphere), 1°x1° (ocean waves) |
| Temporal coverage | 1979 to present |
| Temporal resolution | Hourly |
| File format | GRIB |
| Update frequency | Daily |


Full description of the dataset variables is available on the Copernicus Climate Data Store [ERA5 hourly data on single levels from 1979 to present](https://doi.org/10.24381/cds.adbb2d47) page. Further descriptions can be found in the ECMWF [ERA5 online documentation](https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation).

## Acknowledgments

We acknowledge the use of data generated using Copernicus Climate Change Service information 2020.
