import requests
import os 
import gzip
import tarfile

from io import BytesIO
from datetime import datetime
from urllib.parse import urlparse
from zipfile import ZipFile


def url_retrieve(url,timeout=4):
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

    base = archive_name.split('.')[1]

    list_extensions = list(set(supported_extensions) & set(archive_name.split('.')))
    list_compressions = list(set(supported_compressions) & set(archive_name.split('.')))

    if len(list_extensions) == 0:
        extension = None 
    elif len(list_extensions) == 1:
        extension = list_extensions[0]
    else:
        raise ValueError(f'Error {url} contains more than one extension') 


    if len(list_compressions) == 0:
        raise ValueError(f'Error {url} does not contain any of the supported compression formats (.tar.gz, .gz, .zip))')
    
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
        unzip (bool, optional): wether archive should be unzipped. Defaults to True.
        destination (str, optional): folder where the file should be saved. Defaults to '.'.
    """

    base, extension, compression =  get_fname(url)

    if unzip == True and compression == "zip":
        content = url_retrieve(url)
        with ZipFile(BytesIO(content)) as zip_file:
            zip_file.extractall(destination)

    elif unzip == True and compression == "gz":
        content = url_retrieve(url)
        with gzip.open(BytesIO(content)) as gzip_file:
            gzip_file.extractall(destination)

    elif unzip == True and compression == "tar.gz":
        content = url_retrieve(url)
        with tarfile.open(BytesIO(content)) as tar_file:
            tar_file.extractall(destination)

    else:
        content = url_retrieve(url)
        file_name = f"{base}.{extension}" if extension != None else f"{base}.{default_extension}"
        with open(os.path.join(destination,file_name),'wb') as file:
            file.write(content)


def get_ghcn(start_year=None, end_year=None):
    #start_year = str(datetime.now().year) if start_year == None 
    #end_year = str(datetime.now().year+1) if end_year == None 
    pass

def get_isd():
    pass        

def get_nasa_firm_modis(url):
    pass