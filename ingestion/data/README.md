# GIS Source Data — Download Instructions

This directory holds raw source data files used by the ingestion scripts.
**All files in this directory are git-ignored** (`*.csv`, `*.geojson`, `*.shp`, `*.tif`).

---

## NASA Global Landslide Catalog (GLC/COOLR)

**Required file:** `Global_Landslide_Catalog_Export.csv`

### Download steps

1. Visit the official NASA data.gov record:
   **https://catalog.data.gov/dataset/global-landslide-catalog-export**

2. Click the **Download** button for the CSV resource
   (the filename is typically `Global_Landslide_Catalog_Export.csv` or similar).

3. Save the file to this directory:
   ```
   ingestion/data/Global_Landslide_Catalog_Export.csv
   ```

4. Run the importer from the project root:
   ```bash
   python ingestion/import_nasa_glc.py
   ```
   Or with a custom path:
   ```bash
   python ingestion/import_nasa_glc.py --csv-file /path/to/download.csv
   ```

---

## Citation (required)

When using or referencing this data, cite both of the following publications:

> Kirschbaum, D. B., Adler, R., Hong, Y., Hill, S., & Lerner-Lam, A. (2010).
> *A global landslide catalog for hazard applications: method, results, and limitations.*
> Natural Hazards, 52(3), 561–575.
> **doi:10.1007/s11069-009-9401-4**

> Kirschbaum, D. B., Stanley, T., & Zhou, Y. (2015).
> *Spatial and Temporal Analysis of a Global Landslide Catalog.*
> Geomorphology.
> **doi:10.1016/j.geomorph.2015.03.016**

---

## License

This dataset is a product of NASA/GSFC (U.S. Government).
It is in the **public domain** as a U.S. government work.
Attribution to the above citations is requested.

---

## What this data is NOT

- ❌ Not a landslide susceptibility raster (no risk scores)
- ❌ Not a live warning feed
- ❌ Not a complete spatial inventory (only reported, documented events)
- ❌ Not a polygon/extent layer (events are reported as point locations only)

Use it only as a **historical event inventory** for GIS context.
