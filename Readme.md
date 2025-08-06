# 🌱 Earth Engine Weather & Crop Analysis Toolkit

This repository contains scripts and tools developed during Summer 2025 for collecting, processing, and analyzing environmental data using **Google Earth Engine (GEE)** and **Python**. The focus is on extracting weather, evapotranspiration (ET), and crop/land cover datasets like **CDL** and **NLCD**.

---

## Repository Structure

```
/
├── earthengine-js/         # JavaScript GEE scripts (linked below)
├── earthengine-python/     # Python API scripts for GEE
├── analysis/               # Python scripts for post-processing and analysis
├── notebooks/              # Jupyter Notebooks for exploration or summary
├── data/                   # (Optional) Contains exported sample files or metadata
└── README.md
```

---

## Earth Engine Scripts (JavaScript)

> All JavaScript scripts are hosted in the shared GEE repository below:

- 🔗 **[Main Earth Engine Repo](https://code.earthengine.google.com/?repo=users/yourusername/projectname)**

### Key Scripts:
- [ET Monthly Extractor](https://code.earthengine.google.com/INSERT_LINK)  
- [CDL Clipping & Export](https://code.earthengine.google.com/INSERT_LINK)  
- [Weather Stats by Region (HUC8/County)](https://code.earthengine.google.com/INSERT_LINK)

> _Replace the links with actual shared script links._

---

## Earth Engine Python API Scripts

Located in `earthengine-python/`:

| Script | Description |
|--------|-------------|
| `get_et_gridmet.py` | Extracts GridMET ET data using GEE API |
| `get_cdl_by_year.py` | Downloads CDL rasters for specific years |
| `huc_zonal_stats.py` | Computes zonal statistics over HUC8/HUC12 |
| `merge_gee_exports.py` | Merges multiple CSV exports and cleans data |

---

## 📊 Data Analysis Scripts

Located in `analysis/`:

| Script | Description |
|--------|-------------|
| `et_trend_analysis.py` | Performs trend analysis (Mann-Kendall, Sen's Slope) |
| `cropwise_et_summary.py` | Summarizes ET by crop classes from CDL |
| `visualize_map.py` | Generates maps from raster data using matplotlib/cartopy |

---

## Jupyter Notebooks

Located in `notebooks/` for interactive exploration of:
- Zonal statistics visualization
- Correlation between ET and land cover
- ET change over time

---

## Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/project-repo.git
   cd project-repo
   ```

2. **Authenticate and initialize Earth Engine** (for Python API):
   ```python
   import ee
   ee.Authenticate()
   ee.Initialize()
   ```

3. **Install required Python packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run scripts** as needed from the appropriate folders.

---

## Requirements

- Google Earth Engine Python API
- `pandas`, `geopandas`, `matplotlib`, `rasterio`, `shapely`, `numpy`
- Earth Engine authentication enabled

---

## Credits

Developed by **[Dinesh Gulati]**  
Project under **[IWARRI]**, **[UOI]**  
Summer 2025

---

## 📬 Contact

For questions:  
 gula7530@vandals.uidaho.edu 
 [LinkedIn](https://www.linkedin.com/in/dinesh-gulati-120779149/)
