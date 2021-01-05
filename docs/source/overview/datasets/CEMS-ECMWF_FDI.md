# CEMS ECMWF - Fire Danger Indices 

![](https://pbs.twimg.com/media/D9KxVa4WkAAGhC0.jpg)


The ***Fire Danger Indices*** dataset is produced by the European Center for Medium Range Weather forecast (ECMWF) for the European Forest Fire Information System (EFFIS) on behalf of the Copernicus Emergency Management Service (CEMS). 

The Copernicus program distributes the ***Fire Danger Indices*** via the Copernicus [Climate Data Store](https://cds.climate.copernicus.eu/cdsapp#!/home).

## Technical Background

The fire danger indices are calculated by the Global ECMWF Fire Forecasting model (GEFF) from numerical weather prediction (NWP). 
The GEFF outputs characterise different aspects of fire danger conditions, their relationship is describe bellow.

![](https://www.ecmwf.int/sites/default/files/NL_147_-_M4_-_Di_Guiseppe_Fig_2_coloured_0.png)

A complete description of the GEFF multi-model platform can be found in the following articles:


* *[Di Giuseppe, Francesca, et al. "NWP-driven fire danger forecasting for Copernicus". ECMWF Newsletter. (2016): 34-39.](https://www.ecmwf.int/en/newsletter/147/meteorology/nwp-driven-fire-danger-forecasting-copernicus)* 


* *[Di Giuseppe, Francesca, et al. "The potential predictability of fire danger provided by numerical weather prediction." Journal of Applied Meteorology and Climatology 55.11 (2016): 2469-2491.](https://doi.org/10.1175/JAMC-D-15-0297.1)* 


* *[Di Giuseppe, Francesca, et al. "Fire Weather Index: the skill provided by the European Centre for Medium-Range Weather Forecasts ensemble prediction system." Natural Hazards and Earth System Sciences 20.8 (2020): 2365-2378.
](https://nhess.copernicus.org/articles/20/2365/2020/nhess-20-2365-2020.html)* 

More details on the ***Fire Danger Indices*** can be found in the Copernicus Climate Data Store [Fire Danger Indices product user guide](https://datastore.copernicus-climate.eu/c3s/published-forms/c3sprod/cems-fire-historical/Fire_In_CDS.pdf)


## Downloading Dataset

***Copernicus Climate Data Store (CDS):*** You can access the Fire Danger Indices historical dataset via the Climate Data Store [Fire Danger Indices](https://doi.org/10.24381/cds.0e89c522) page.

<!--***EFFIS:*** You can access the Fire Danger Indices historical via the EFFIS data request form: [EFFIS](https://effis.jrc.ec.europa.eu/static/data.request.form/)-->

**Fire Danger Indices dataset used in Pyro-Risks Training**

<!--TODO PRECISIONS ON THE EXACT DATASET USED FOR TRAINING-->

```python
from pyro_risks.datasets import GwisFwi
fdi = GwisFwi()
```
<!--PRECISIONS ON THE EXACT DATASET USED FOR TRAINING-->

## Datasets Descriptions

| DATA DESCRIPTION |  |
|-|-|
| Data type | Gridded |
| Horizontal coverage | Global |
| Horizontal resolution | 0.1°x0.1°; Native resolution is 9 km. |
| Vertical coverage | From 2 m above the surfacelevel, to a soil depth of 289 cm. |
| Vertical resolution | 4 levels of the ECMWF surface model: Layer 1: 0 -7cm,<br>Layer 2: 7 -28cm, Layer 3: 28-100cm, Layer 4: 100-289cm <br>Some parameters are defined at 2 m over the surface. |
| Temporal coverage | January 1981 to present |
| Temporal resolution | Hourly |
| File format | GRIB |
| Update frequency | Monthly with a delay of about three months relatively to actual date. |


Full description of the dataset variables is available on the Copernicus Climate Data Store [Fire Danger Indices](https://doi.org/10.24381/cds.0e89c522) page.

<center>

| Name | Units |
|:-:|:-:|
| Build-up index | Dimensionless |
| Burning index | 10ft |
| Danger rating | Dimensionless |
| Drought code | Dimensionless |
| Duff moisture code | Dimensionless |
| Energy release component | 25Btu ft2 -1 |
| Fine fuel moisture code | Dimensionless |
| Fire daily severity index | Dimensionless |
| Fire danger index | Dimensionless |
| Fire weather index | Dimensionless |
| Ignition component | % |
| Initial spread index | Dimensionless |
| Keetch-Byram drought index | Dimensionless |
| Spread component | Dimensionless |

</center>

## Acknowledgments

We acknowledge the use of data generated using Copernicus Climate Change Service information 2020.