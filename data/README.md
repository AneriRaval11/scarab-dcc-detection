# Data

No satellite data is stored in this repository. All data come from **MOSDAC** (Meteorological and Oceanographic Satellite Data Archival Centre, ISRO): https://www.mosdac.gov.in/

Registration is required to download, and use is subject to MOSDAC's data policy, so the files are not redistributed here.

## Products used

| Instrument | Product (file prefix) | Used for |
|---|---|---|
| SAPHIR (Megha-Tropiques) | Level-1A, `MT1SAPSL1A_...h5` | Brightness temperatures TB1-TB6, incidence angle, lat/lon, scan time |
| ScaRaB (Megha-Tropiques) | Level-1A, `MT1SCASL1A_...h5` | Visible / infrared filtered radiances (match-up and threshold analysis) |

Period worked on: January 2014. Match-up lists of SAPHIR and ScaRaB orbit files are paired by acquisition time.

## Expected layout when running the notebooks

```
data/
├── Jan2014/                     # downloaded .h5 files
├── MT1SAP_<...>.h5.pkl          # gridded per-orbit dictionaries produced by the preprocessing step
└── sap_dict.pkl                 # one gridded orbit, input to scripts/reproduce_gmm_result.py
```

The notebooks were written in Google Colab and still contain Colab paths such as `/content/Jan2014/...`; change them to your local `data/` paths.
