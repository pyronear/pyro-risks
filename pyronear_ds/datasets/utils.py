import requests
import os 
import gzip
import tarfile
import shutil
import warnings

from io import BytesIO
from datetime import datetime
from urllib.parse import urlparse
from zipfile import ZipFile


def url_retrieve(url,timeout=None):
    """Retrives and pass the content of an URL request 

    Args:
        url (str): URL to request 
        timeout (int, optional): number of seconds before the request times out. Defaults to 4.

    Raises:
        requests.exceptions.ConnectionError: 

    Returns:
        bytes: content of the response
    """

    response =requests.get(url, timeout=timeout, allow_redirects=True)
    if response.status_code != 200:
        raise requests.exceptions.ConnectionError(f'Error code {response.status_code} - could not download {url}')
    return response.content 
    

def get_fname(url):
    """Find file name, extension and compression of an archive located by an URL

    Args:
        url (str): URL of the compressed archive

    Raises:
        ValueError: if URL contains more than one extension
        ValueError: if URL does not contain any of the supported compression formats (.tar.gz, .gz, .zip)
        ValueError: if URL contains more than one compression format

    Returns:
        tuple<str, str, str>: a tuple containing the base file name, extension and compression format
    """
    
    supported_compressions = ["tar","gz","zip"]
    supported_extensions = ["csv","geojson","shp","shx","nc"]

    archive_name = urlparse(url).path.rpartition('/')[-1]

    base = archive_name.split('.')[0]

    list_extensions = list(set(supported_extensions) & set(archive_name.split('.')))
    list_compressions = list(set(supported_compressions) & set(archive_name.split('.')))

    if len(list_extensions) == 0:
        extension = None 
    elif len(list_extensions) == 1:
        extension = list_extensions[0]
    else:
        raise ValueError(f'Error {url} contains more than one extension') 

    if len(list_compressions) == 0:
        compression = None 
    
    elif len(list_compressions) == 1:
        compression = list_compressions[0] 

    elif len(list_compressions) == 2:
        compression = "tar.gz"

    else:
        raise ValueError(f'Error {url} contains more than one compression format') 


    return (base, extension, compression)



def download(url, default_extension, unzip=True, destination='.'):
    """Helper function for downloading, unzipping and saving compressed file from a given URL.  

    Args:
        url (str): URL of the compressed archive
        default_extension (str): extension of the archive
        unzip (bool, optional): whether archive should be unzipped. Defaults to True.
        destination (str, optional): folder where the file should be saved. Defaults to '.'.
    """
# TODO Write case tests for zip, tar.gz, gz and uncompressed files
# Check if the destination directory is created each if not exist 
# Check if the file are  download
# Add print and logging statement add 
    base, extension, compression =  get_fname(url)

    if unzip == True and compression == "zip":
        content = url_retrieve(url)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with ZipFile(BytesIO(content)) as zip_file:
            zip_file.extractall(destination)

    elif unzip == True and compression == "tar.gz":
        content = url_retrieve(url)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with tarfile.open(BytesIO(content)) as tar_file:
            tar_file.extractall(destination)

    elif unzip == True and compression == "gz":
        content = url_retrieve(url)
        file_name = f"{base}.{extension}" if extension != None else f"{base}.{default_extension}"
        full_path = os.path.join(destination,file_name)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with gzip.open(BytesIO(content)) as gzip_file, open(full_path, 'wb+') as unzipped_file:
            shutil.copyfileobj(gzip_file, unzipped_file)

    elif unzip == False and compression == None:
        content = url_retrieve(url)
        file_name = f"{base}.{extension}" if extension != None else f"{base}.{default_extension}"
        full_path = os.path.join(destination,file_name)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path,'wb+') as file:
            file.write(content)

    elif unzip == False and compression != None:
        content = url_retrieve(url)
        file_name = f"{base}.{compression}"
        full_path = os.path.join(destination,file_name)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path,'wb+') as file:
            file.write(content)

    else:
        raise ValueError("If the file is not compressed set unzip to False")


def get_ghcn(start_year=None, end_year=None, destination = './ghcn'):
    """Download yearly Global Historical Climatology Network - Daily (GHCN-Daily) (.csv) From 
    NOAA's National Centers for Environmental Information (NCEI).  

    Args:
        start_year (int, optional): first year to be retrieved. Defaults to None.
        end_year (int, optional): first that will not be retrieved. Defaults to None.
        destination (str, optional): destination directory. Defaults to './ghcn'.
    """
# TODO 
# Write case tests 
# Implement archive=False

    start_year = datetime.now().year if start_year == None else start_year
    end_year = datetime.now().year+1 if end_year == None or start_year == end_year else end_year

    for year in range(start_year,end_year):
        url = f"https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/{year}.csv.gz"
        download(url=url, default_extension='csv', unzip=True, destination=destination)


def get_modis(start_year=None, end_year=None, yearly=False, destination = './firms'):
    """Download last 24H or yearly France active fires from the Fire Information for Resource 
    Management System (FIRMS) NASA.

    Args:
        start_year (int, optional): first year to be retrieved. Defaults to None.
        end_year (int, optional): first that will not be retrieved. Defaults to None.
        yearly (bool, optional): whether to download yearly active fires or not. Defaults to False.
        destination (str, optional): destination directory. Defaults to './firms'.]
    """
    
    if yearly == True:
        start_year = datetime.now().year - 1 if start_year == None else start_year
        end_year = datetime.now().year if end_year == None or start_year == end_year else end_year

        for year in range(start_year,end_year):
            assert (start_year != 2020 or end_year != 2021), f'MODIS active fire archives are only available for the years from 2000 to 2019'
            url = f"https://firms.modaps.eosdis.nasa.gov/data/country/modis/{year}/modis_{year}_France.csv"
            download(url=url, default_extension='csv', unzip=False, destination=destination)
    
    else:
        if start_year != None:
            raise warnings.warn(f"The active fires from the last 24H of the MODIS Satellite will be download.")
        else:
            url = f"https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6/csv/MODIS_C6_Europe_24h.csv"
            download(url=url, default_extension='csv', unzip=False, destination=destination)
        
        

