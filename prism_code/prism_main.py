from datetime import datetime
import os
from utils import *

clim_var = 'ppt'  # climate variable: ppt, tmin, tmax, etc.
region = 'us'     # region: usually 'us'
res = '4km'       # resolution: 4km, 800m, etc.

year = 2016  # target year for the data
start_date = datetime(year-1, 10, 1) #YYMMDD for daily, YYYYMM for monthly, YYYY for annual
end_date = datetime(year, 9, 30)

# Example usage:
base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, 'prism_data_monthly')
os.makedirs(output_dir, exist_ok=True)

prism_data(clim_var, region, res, start_date, end_date, output_dir)

files = filter_monthly_files_for_water_year(
    folder=output_dir,
    year=year,
    variable=clim_var,
    res='25m'  # Adjust resolution as needed
)

unzip_nc_files(files, f"unzipped/wateryear_{year}")

combine_band1_monthly_to_cube(
    folder="unzipped/wateryear_2016",
    output_path=f"raw_water_years/{clim_var}_wy2016.nc",
    clim_var=clim_var
)
