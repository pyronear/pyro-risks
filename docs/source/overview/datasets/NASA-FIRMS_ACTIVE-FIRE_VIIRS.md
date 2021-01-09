# NASA FIRMS - Active Fire

![](https://cdn.earthdata.nasa.gov/conduit/upload/11755/FIRMS.jpg)

NASA's Fire Information for Resource Management System (FIRMS) distributes Near Real-Time (NRT) **Active Fire Data** within 3 hours of satellite observation from NASA's Moderate Resolution Imaging Spectroradiometer (MODIS) and NASA's Visible Infrared Imaging Radiometer Suite (VIIRS).

The European Forest Fire Information System (EFFIS) uses and redistributes the **Active Fire Data** provided by the NASA FIRMS.

## Technical Background

The algorithms used by the MODIS and VIIRS instruments detect active fires on the basis of the thermal anomalies they produce. The contextual algorithms compare the temperature of a potential fire with the temperature of the land cover around it. If the difference in temperature is above a given threshold, the potential fire is confirmed as an active fire or "hot spot".

A complete description of the MODIS and VIIRS algorithms can be found in the following articles:
- *[Giglio, Louis, et al. "An enhanced contextual fire detection algorithm for MODIS.
  <br>Remote sensing of environment 87.2-3 (2003): 273-282.](https://www.sciencedirect.com/science/article/abs/pii/S0034425703001846?via%3Dihub)*

- *[Schroeder, Wilfrid, et al. "The New VIIRS 375 m active fire detection data product:
Algorithm description and initial assessment." Remote Sensing of Environment 143 (2014): 85-96.](https://cdn.earthdata.nasa.gov/conduit/upload/4681/Schroeder_et_al_2014b_RSE.pdf)*

## Downloading Datasets


***NASA FIRMS:*** 
  - You can download MODIS and VIIRS Active Fire Data for the last **24, 48 hours and 7 days (.shp, .kml, .csv)** from NASA Fire Information For Resource Management System [here](https://firms.modaps.eosdis.nasa.gov/active_fire/#firms-txt).

  - **Archive downloads for active fire/hotspot** information older than the last 7 days are accessible [here](https://firms.modaps.eosdis.nasa.gov/download/) (**country yearly summaries**).


***EFFIS:*** You can access the Modis and VIIRS Active Fire Data via the EFFIS data request for: [https://effis.jrc.ec.europa.eu/static/data.request.form/](https://effis.jrc.ec.europa.eu/static/data.request.form/)
  

**VIIRS dataset used in Pyro-Risks Training**

<!--TODO PRECISIONS ON THE EXACT DATASET USED FOR TRAINING-->

```python
from pyro_risks.datasets import NASAFIRMS, NASAFIRMS_VIIRS
viirs = NASAFIRMS_VIIRS()
modis = NASAFIRMS()
```
<!--PRECISIONS ON THE EXACT DATASET USED FOR TRAINING-->
## Datasets Descriptions

### VIIRS MODIS Differences

The spatial resolution of the active fire detection pixel from MODIS is **1 km**. The VIIRS active fire products provides an improved spatial resolution, as compared to MODIS. The spatial resolution of the active fire detection pixel for VIIRS is **375 m**. Additionally, **VIIRS is able to detect smaller fires and can help delineate perimeters of ongoing large fires**. Additional information on the MODIS and VIIRS Active Fire products is available here ([MCD14DL](https://earthdata.nasa.gov/earth-observation-data/near-real-time/firms/c6-mcd14dl), [VNP14IMGTDL_NRT](https://earthdata.nasa.gov/earth-observation-data/near-real-time/firms/v1-vnp14imgt)).

| Datasets | Availability | Update<br>Frequency | Temporal<br>Coverage | Revisit | Spatial <br>Resolution | Spatial <br>Coverage |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| MODIS C6<br>STANDARD | 2-3 month | X | November 2000<br>-<br>Present | ~4-6 hours | 1 km | Global |
| VIIRS 375 m<br>(S-NPP) <br>STANDARD | 2-3 month | X | January 2012<br>-<br>Present | ~4-6 hours  | 375 m | Global |
| VIIRS 375 m<br>(NOAA-20)<br>STANDARD | 2-3 month | X | January 2020<br>-<br>Present | ~4-6 hours  | 375 m | Global |
| MODIS C6<br>NRT |  ~3 hours | ~6 hours | November 2000<br>-<br>Present | ~4-6 hours | 1 km | Global |
| VIIRS 375 m<br>(S-NPP)<br>NRT | ~3 hours | ~6 hours | January 2012<br>-<br>Present | ~4-6 hours | 375 m | Global |
| VIIRS 375 m<br>(NOAA-20)<br>NRT | ~3 hours | ~6 hours | January 2020<br>-<br>Present | ~4-6 hours | 375 m | Global |


### VIIRS NRT Attribute Fields 

| Attribute | Short Description | Long Description |
|:-:|:-:|-|
| Latitude | Latitude | Center of nominal 375 m fire pixel |
| Longitude | Longitude | Center of nominal 375 m fire pixel |
| Bright_ti4 | Brightness <br>temperature I-4 | VIIRS I-4 channel brightness temperature <br>of the fire pixel measured in Kelvin. |
| Scan | Along Scan pixel size | The algorithm produces approximately 375 m <br>pixels at nadir. Scan and track reflect <br>actual pixel size. |
| Track | Along Track pixel size | The algorithm produces approximately 375 m <br>pixels at nadir. Scan and track reflect <br>actual pixel size. |
| Acq_Date | Acquisition Date | Date of VIIRS acquisition. |
| Acq_Time | Acquisition Time | Time of acquisition/overpass of the satellite<br>(in UTC). |
| Satellite | Satellite | N= Suomi National Polar-orbiting Partnership <br>(Suomi NPP) |
| Confidence | Confidence | This value is based on a collection of intermediate <br>algorithm quantities used in the detection process. <br>It is intended to help users gauge the quality of <br>individual hotspot/fire pixels.<br><br>Confidence values are set to low, nominal and high.<br>Low confidence daytime fire pixels are typically <br>associated with areas of sun glint and lower relative<br>temperature anomaly (<15K) in the mid-infrared <br>channel I4. Nominal confidence pixels are those free <br>of potential sun glint contamination during the day <br>and marked by strong (>15K) temperature anomaly in <br>either day or nighttime data. High confidence fire <br>pixels are associated with day or nighttime saturated <br>pixels.<br><br>Please note: Low confidence nighttime pixels occur only<br>over the geographic area extending from 11° E to 110° W <br>and 7° N to 55° S. This area describes the region of <br>influence of the South Atlantic Magnetic Anomaly which <br>can cause spurious brightness temperatures in the <br>mid-infrared channel I4 leading to potential false <br>positive alarms. These have been removed from the NRT <br>data distributed by FIRMS. |
| Version | Version <br>(Collection and source) | Version identifies the collection (e.g. VIIRS Collection 1) <br>and source of data processing: Near Real-Time (NRT suffix <br>added to collection) or Standard Processing (collection only).<br>1.0NRT - Collection 1 NRT processing.<br>1.0 - Collection 1 Standard processing. |
| Bright_ti5 | Brightness <br>temperature I-5 | I-5 Channel brightness temperature of the fire pixel measured<br>in Kelvin. |
| FRP | Fire Radiative Power | FRP depicts the pixel-integrated fire radiative power in <br>MW (megawatts). Given the unique spatial and spectral <br>resolution of the data, the VIIRS 375 m fire detection <br>algorithm was customized and tuned in order to optimize<br>its response over small fires while balancing the <br>occurrence of false alarms. <br><br>Frequent saturation of the mid-infrared I4 channel <br>(3.55-3.93 µm) driving the detection of active fires requires<br>additional tests and procedures to avoid pixel classification <br>errors. As a result,sub-pixel fire characterization (e.g.,<br>fire radiative power [FRP] retrieval) is only viable across <br>small and/or low-intensity fires.<br><br>Systematic FRP retrievals are based on a hybrid approach <br>combining 375 and 750 m data. <br><br>In fact, starting in 2015 the algorithm incorporated additional<br>VIIRS channel M13 (3.973-4.128 µm) 750 m data in both <br> aggregated and unaggregated format. |
| Type* | Inferred hot spot type | 0 = presumed vegetation fire<br>1 = active volcano<br>2 = other static land source<br>3 = offshore detection (includes all detections over water) |
| DayNight | Day or Night | D= Daytime fire, N= Nighttime fire |
*This attribute is only available for VJ114IMGT (standard quality) data (coming soon)

Full description of the VIIRS dataset is available on the NASA Earth science data platform [VNP14IMGTDL_NRT](https://earthdata.nasa.gov/earth-observation-data/near-real-time/firms/v1-vnp14imgt) page.

### MODIS NRT Attribute Fields

| Attribute | Short Description | Long Description |
|:-:|:-:|:-:|
| Latitude | Latitude | Center of 1km fire pixel but not necessarily the <br>actual location of the fire as one or more fires<br>can be detected within the 1km pixel. |
| Longitude | Longitude | Center of 1km fire pixel but not necessarily the <br>actual location of the fire as one or more fires <br>can be detected within the 1km pixel. |
| Brightness | Brightness <br>temperature<br>21 (Kelvin) | Channel 21/22 brightness temperature of the fire<br>pixel measured in Kelvin. |
| Scan | Along Scan pixel size | The algorithm produces 1km fire pixels but MODIS<br>pixels get bigger toward the edge of scan. Scan <br>and track reflect actual pixel size. |
| Track | Along Track pixel size | The algorithm produces 1km fire pixels but MODIS<br>pixels get bigger toward the edge of scan. Scan <br>and track reflect actual pixel size. |
| Acq_Date | Acquisition Date | Data of MODIS acquisition. |
| Acq_Time | Acquisition Time | Time of acquisition/overpass of the satellite <br>(in UTC). |
| Satellite | Satellite | A = Aqua and T = Terra. |
| Confidence | Confidence<br>(0-100%) | This value is based on a collection of intermediate <br>algorithm quantities used in the detection process. <br>It is intended to help users gauge the quality of <br>individual hotspot/fire pixels. <br><br>Confidence estimates range between 0 and 100% <br>and are assigned one of the three fire classes <br>(low-confidence fire, nominal-confidence fire, <br>or high-confidence fire). |
| Version | Version<br>(Collection and source) | Version identifies the collection (e.g. MODIS <br>Collection 6) and source of data processing: <br>Near Real-Time (NRT suffix added to collection) <br>or Standard Processing (collection only).<br><br>"6.0NRT" - Collection 6 NRT processing.<br>"6.0" - Collection 6 Standard processing. <br>Find out more on collections and on the <br>differences between FIRMS data sourced<br>from LANCE FIRMS and University of Maryland. |
| Bright_T31 | Brightness<br>temperature 31<br>(Kelvin) | Channel 31 brightness temperature of the fire pixel<br> measured in Kelvin. |
| FRP | Fire Radiative<br>Power<br>(MW - megawatts) | Depicts the pixel-integrated fire radiative power <br>in MW (megawatts). |
| Type* | Inferred hot<br>spot type | 0 = presumed vegetation fire<br>1 = active volcano<br>2 = other static land source<br>3 = offshore |
| DayNight | Day or Night | D= Daytime fire, N= Nighttime fire |
*This attribute is only available for MCD14ML (standard quality) data


Full description of the MODIS dataset is available on the NASA Earth science data platform [MCD14DL](https://earthdata.nasa.gov/earth-observation-data/near-real-time/firms/c6-mcd14dl) page.
## Acknowledgments

Data were provided by the European Forest Fire Information System – EFFIS [(https://effis.jrc.ec.europa.eu)](https://effis.jrc.ec.europa.eu) of the European Commission Joint Research Centre.

We acknowledge the use of data and imagery from LANCE FIRMS operated by NASA's Earth Science Data and Information System (ESDIS) with funding provided by NASA Headquarters.