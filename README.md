# APPMAR 2

APPMAR 2 is a Python program for marine climate analysis.

![APPMAR 2 main window.](appmar2.png)

Some features:

* Download data from WAVEWATCH III® 30-year Hindcast Phase 2 in GRIB2 format.
* Extract time series at given coordinates and save data to CSV format.
* Load time series in CSV format.
* Perform mean and extreme climate graphical analyses over loaded data series.
* Show interactive statistical plots and allow the user to save them as 300-dpi PNG images.

## Installation

For installation on Windows, open Anaconda Prompt and run the following commands:

1. Install dependencies:

```
conda install -c conda-forge pandas numpy xarray matplotlib seaborn statsmodels cartopy cfgrib
```

2. Install APPMAR 2:

```
pip install pygubu appmar2
```

## Run

After installation, run the command `appmar2` on Anaconda Prompt.

## Authors

* German Rivillas-Ospina
* Diego Casas
* L.Paola Ospina
* Katherine Rivera
* Dennis Rudas