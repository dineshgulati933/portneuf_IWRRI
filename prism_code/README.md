# 📈 PRISM Climate Data Downloader and Processor

Recommended to use VS Code for this. If possible along with anaconda environment

This Python script automates the download, filtering, and conversion of **monthly PRISM climate data** (e.g., precipitation, temperature) into a NetCDF data cube for a specified **water year**.

---

## 📦 Features

- Download monthly PRISM climate data (e.g., `ppt`, `tmin`, `tmax`)
- Filter downloaded files based on water year (Oct 1 – Sep 30)
- Unzip `.zip` archives containing NetCDF files
- Combine Band 1 of monthly files into a multi-band NetCDF cube

---

## 🔧 Requirements

Install dependencies with:

```bash
pip install -r requirements.txt


project-root/
│
├── prism_data_monthly/           # Raw downloaded ZIP files
├── unzipped/wateryear_2016/      # Extracted NetCDF files
└── raw_water_years/              # Final NetCDF data cube output

After this data_analysis.ipynb is provided with minimum code to clip based on aoi, and calculating totals