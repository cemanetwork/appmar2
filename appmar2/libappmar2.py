import os
import shutil
import urllib.request

import numpy as np
import xarray as xr

URL_BASE = 'https://polar.ncep.noaa.gov/waves/hindcasts/'
PATH = 'nopp-phase2/{year}{month:02}/gribs/multi_reanal.{grid}.{param}.{year}{month:02}.grb2'


def download_grib(**metadata):
    """Downloads a WAVEWATCH III® 30-year Hindcast Phase 2 GRIB file with the given metadata."""
    path = PATH.format(**metadata)
    with urllib.request.urlopen(URL_BASE + path) as res:
        if not os.path.exists(path) or os.path.getsize(path) != res.length:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as file:
                shutil.copyfileobj(res, file)


def parse_coord(s):
    lat, lon = s.split(',')
    return float(lat), float(lon)


def extractor(grid, lat, lon):
    def f(year, month, param):
        path = PATH.format(grid=grid, year=year, month=month, param=param)
        dset = xr.open_dataset(path, engine='cfgrib').sel(
            latitude=lat, longitude=lon, method='nearest')
        return dset
    return f


def format_filename(lat, lon):
    if lat >= 0:
        str_lat = f'{lat}N'
    else:
        str_lat = f'{abs(lat)}S'
    if lon > 180:
        str_lon = f'{(360 - lon)}W'
    else:
        str_lon = f'{lon}E'

    return f'appmar2-{str_lat}-{str_lon}.csv'


def azimuth(x, y):
    az = np.degrees(np.arctan2(x, y))
    return az + 360 * (az < 0)


def parse_fname(fname):
    _, str_lat, str_lon = os.path.splitext(
        os.path.split(fname)[1]
    )[0].lower().split('-')
    assert (str_lat[-1] in ['n', 's']), "Not a valid latitude."
    assert (str_lon[-1] in ['e', 'w']), "Not a valid longitude."
    lat = float(str_lat[:-1])
    lon = float(str_lon[:-1])
    if str_lat[-1] == 's':
        lat *= -1
    if str_lon[-1] == 'w':
        lon *= -1
    return lat, lon


def dd_to_dms(dd):
    m, s = divmod(abs(dd) * 3600, 60)
    d, m = divmod(m, 60)
    return np.sign(dd)*d, m, s

def format_as_dms(dd, mode):
    d, m, s = dd_to_dms(dd)
    dirs = ['N', 'S'] if mode == 'lat' else ['E', 'W']
    sym = dirs[1] if d < 0 else dirs[0]
    return f'{abs(d):.0f}°{m:.0f}\'{s:.0f}"{sym}'