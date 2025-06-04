import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import os
import re
import zipfile
import xarray as xr
import rioxarray
from affine import Affine
import glob

def prism_data(clim_var, region, res, start_date=None, end_date=None, output_dir=None):
    base_url = f'https://services.nacse.org/prism/data/get/{region}/{res}'

    # Download loop
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y%m')
        url = f"{base_url}/{clim_var}/{date_str}?format=nc"

        print(f"Downloading: {url}")
        response = requests.get(url, allow_redirects=True)

        if response.status_code == 200:
            if 'content-disposition' in response.headers:
                filename = response.headers['content-disposition'].split('filename=')[1].strip('"')
            else:
                filename = f"{clim_var}_{date_str}.{format}"  # fallback filename

            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Saved: {filepath}")
        else:
            print(f"Failed to download for {date_str}: HTTP {response.status_code}")

        time.sleep(2)
        current_date += relativedelta(months=1)

def filter_monthly_files_for_water_year(year, variable='ppt', res='4km',folder='prism_data_monthly'):
    """
    Filters zipped monthly PRISM NetCDF files for a given water year (Oct–Sep).

    Filename format: prism_{variable}_us_{res}_YYYYMM.zip

    Args:
        folder (str): Path to folder containing zipped files.
        year (int): Water year to target.
        variable (str): Climate variable (e.g., 'ppt').
        res (str): Resolution (e.g., '4km').

    Returns:
        List[str]: Sorted list of matching file paths.
    """
    pattern = re.compile(
         rf"prism_{variable}_us_{res}_(\d{{6}})\.zip"
    )
    start = datetime(year - 1, 10, 1)
    end = datetime(year, 9, 30)

    selected_files = []
    for filename in os.listdir(folder):
        match = pattern.match(filename)
        if match:
            date_str = match.group(1)
            file_date = datetime.strptime(date_str, "%Y%m")
            if start <= file_date <= end:
                selected_files.append(os.path.join(folder, filename))

    return sorted(selected_files)

def unzip_nc_files(file_list, dest_folder):
    """
    Unzips only the .nc files from each zip archive to the destination folder.

    Args:
        file_list (list): List of .zip file paths.
        dest_folder (str): Folder to extract the .nc files to.
    """
    os.makedirs(dest_folder, exist_ok=True)

    for zip_path in file_list:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find the .nc file
            nc_files = [f for f in zip_ref.namelist() if f.endswith('.nc')]
            for nc_file in nc_files:
                target_path = os.path.join(dest_folder, os.path.basename(nc_file))
                if not os.path.exists(target_path):
                    print(f"Extracting: {nc_file}")
                    zip_ref.extract(nc_file, dest_folder)
                else:
                    print(f"Already extracted: {nc_file}")

def extract_date_from_filename(filename):
    """
    Extracts datetime object from filename like 'prism_ppt_us_25m_202201.nc'
    """
    base = os.path.basename(filename)
    parts = base.split('_')
    date_str = parts[-1].replace('.nc', '')
    return datetime.strptime(date_str, "%Y%m")

def combine_band1_monthly_to_cube(folder, output_path, clim_var='ppt'):
    """
    Combines PRISM monthly NetCDFs into a time-stacked cube with proper CRS and transform.

    Args:
        folder (str): Path to folder with monthly .nc files.
        output_path (str): Output path for combined NetCDF.
    """
    # Step 1: Find all NetCDF files
    nc_files = sorted(glob.glob(os.path.join(folder, "*.nc")))
    if not nc_files:
        raise FileNotFoundError("No .nc files found in folder.")

    data_arrays = []

    # Step 2: Use first file for reference CRS and transform
    ref_ds = xr.open_dataset(nc_files[0])
    crs_wkt = ref_ds['crs'].attrs.get('crs_wkt')
    geotransform_str = ref_ds['crs'].attrs.get('GeoTransform')
    if not crs_wkt or not geotransform_str:
        raise ValueError("Missing CRS or GeoTransform in reference file.")
    
    geotransform = tuple(map(float, geotransform_str.split()))
    affine_transform = Affine.from_gdal(*geotransform)

    # Step 3: Load and expand each Band1 into time dimension
    for f in nc_files:
        ds = xr.open_dataset(f)
        band = ds['Band1'].expand_dims(dim='time')
        band = band.assign_coords(time=[extract_date_from_filename(f)])
        data_arrays.append(band)

    # Step 4: Concatenate into time-series cube
    combined = xr.concat(data_arrays, dim='time')
    combined.name = clim_var
    combined.attrs['units'] = 'mm'

    # Step 5: Apply CRS and transform
    combined = combined.rio.write_crs(crs_wkt)
    combined.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    combined.rio.write_transform(affine_transform, inplace=True)

    # Step 6: Build dataset and set grid mapping
    final_ds = combined.to_dataset(name=clim_var)
    final_ds['crs'] = ref_ds['crs']  # Copy full CRS metadata

    # Safely remove 'grid_mapping' from both attributes and encoding
    if 'grid_mapping' in final_ds[clim_var].attrs:
        del final_ds[clim_var].attrs['grid_mapping']
    if 'grid_mapping' in final_ds[clim_var].encoding:
        del final_ds[clim_var].encoding['grid_mapping']

    # Now set it
    final_ds[clim_var].attrs['grid_mapping'] = 'crs'

    # Step 7: Save output NetCDF
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_ds.to_netcdf(output_path)

    print(f"✅ Final NetCDF saved to: {output_path}")