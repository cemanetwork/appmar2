"""
APPMAR 2

by

CEMAN
Diego A. Casas
Katherine Rivera
"""

import os
from datetime import datetime
from itertools import product
from threading import Thread
from tkinter import PhotoImage
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, showerror

import numpy as np
import pandas as pd
import pygubu
import xarray as xr

from .libappmar2 import (azimuth, download_grib, extractor, format_as_dms,
                         format_filename, parse_coord, parse_fname, URL_BASE, PATH)
from .libplot import plot_dist, plot_joint, plot_rose, save_map

APPMAR2_DIR = os.path.join(os.path.expanduser('~'), 'APPMAR2')
DATA_PATH = os.path.dirname(__file__)
YEARS = range(1979, 2009 + 1)
MONTHS = range(1, 12 + 1)
NMONTHS = len(YEARS) * len(MONTHS)
GRID_ID = {
    'Global 30 min': 'glo_30m',
    'Arctic Ocean curvilinear': 'aoc_15m',
    'Gulf of Mexico and NW Atlantic 10 min': 'ecg_10m',
    'US West Coast 10 min': 'wc_10m',
    'Pacific Islands 10 min': 'pi_10m',
    'Alaskan 10 min': 'ak_10m',
    'North Sea Baltic 10 min': 'nsb_10m',
    'Mediterranean 10 min': 'med_10m',
    'North West Indian Ocean 10 min': 'nwio_10m',
    'Australia 10 min': 'oz_10m',
    'Gulf of Mexico and NW Atlantic 4 min': 'ecg_4m',
    'US West Coast 4 min': 'wc_4m',
    'Alaskan 4 min': 'ak_4m',
    'North Sea Baltic 4 min': 'nsb_4m',
    'Australia 4 min': 'oz_4m'
}
STR_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
              'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

VARS = {
    'hs': ['swh'],
    'tp': ['perpw'],
    'dp': ['dirpw'],
    'wind': ['u', 'v']
}

DISTRIB = {
    'Significant wave height': ['swh'],
    'Period': ['perpw'],
    'Joint probability': ['swh', 'perpw']
}

LABELS = {
    'hs': 'Significant\nwave height\n(m)',
    'swh': 'Significant wave height (m)',
    'tp': 'Period (s)',
    'perpw': 'Period (s)',
    'wind': 'Wind speed\n(m/s)'
}


class APPMAR2:

    def __init__(self):
        self.parameters = []
        self.data = None

        # Create a builder
        self.builder = builder = pygubu.Builder()

        # Load an UI file
        builder.add_from_file(os.path.join(DATA_PATH, 'appmar2.ui'))

        # Create the mainwindow
        self.mainwindow = builder.get_object('win-main')

        self.dlg_select_grid = None
        self.cb_grid = None
        self.btn_grid_start = None
        self.dlg_progress = None
        self.strvar_current = None
        self.pb_progress = None
        self.dlg_input_coord = None
        self.ent_coord = None
        self.btn_coord_start = None

        self.cb_distrib = builder.get_object('cb-distrib')
        self.cb_distrib.current(0)

        self.lbl_map = builder.get_object('lbl-map')
        photo = PhotoImage(file=os.path.join(DATA_PATH, 'ceman.png'))
        self.lbl_map.config(image=photo)
        self.lbl_map.photo = photo

        self.frm_map = builder.get_object('frm-map')
        self.frm_map.config(text='APPMAR 2')

        # Connect widgets to commands
        builder.connect_callbacks(self)

        os.makedirs(APPMAR2_DIR, exist_ok=True)
        os.chdir(APPMAR2_DIR)

    def run(self):
        self.mainwindow.mainloop()

    def toggle_parameter(self, parameter):
        if parameter in self.parameters:
            self.parameters.remove(parameter)
        else:
            self.parameters.append(parameter)

    def show_dlg_select_grid(self):
        if self.dlg_select_grid is None:
            self.dlg_select_grid = self.builder.get_object(
                'dlg-select-grid', self.mainwindow)
            self.cb_grid = self.builder.get_object('cb-grid')
            self.cb_grid.current(2)
            self.btn_grid_start = self.builder.get_object('btn-grid-start')
            self.dlg_select_grid.run()
        else:
            self.dlg_select_grid.show()

    def show_dlg_progress(self):
        if self.dlg_progress is None:
            self.dlg_progress = self.builder.get_object(
                'dlg-progress', self.mainwindow)
            self.strvar_current = self.builder.get_variable('strvar-current')
            self.pb_progress = self.builder.get_object('pb-progress')
            self.dlg_progress.run()
        else:
            self.dlg_progress.show()

    def show_dlg_input_coord(self):
        self.dlg_select_grid.close()
        if self.dlg_input_coord is None:
            self.dlg_input_coord = self.builder.get_object(
                'dlg-input-coord', self.mainwindow)
            self.ent_coord = self.builder.get_object('ent-coord')
            self.btn_coord_start = self.builder.get_object('btn-coord-start')
            self.btn_coord_start['command'] = self.show_extract_progress
            self.dlg_input_coord.run()
        else:
            self.dlg_input_coord.show()

    def download_gribs(self):
        grid = GRID_ID[self.cb_grid.get()]
        for year, month, param in product(YEARS, MONTHS, self.parameters):
            str_month = STR_MONTHS[month - 1]
            self.strvar_current.set(f'Downloading {str_month} {year}...')
            download_grib(grid=grid, param=param, year=year, month=month)
            self.pb_progress.step(1)
        showinfo(title='Download finished', message=f'Download finished. All the data is in directory {APPMAR2_DIR}')
        self.dlg_progress.close()

    def show_download_progress(self):
        self.dlg_select_grid.close()
        self.show_dlg_progress()
        nparam = len(self.parameters)
        self.pb_progress['value'] = 0
        self.pb_progress['maximum'] = NMONTHS * nparam
        Thread(target=self.download_gribs).start()

    def extract_series(self):
        lat, lon = parse_coord(self.ent_coord.get())
        if lon < 0:
            lon += 360
        grid = GRID_ID[self.cb_grid.get()]
        load = extractor(grid, lat, lon)
        variables = [v for p in self.parameters for v in VARS[p]]
        darr = load(1979, 1, self.parameters[0])[variables[0]]
        if darr.isnull().all():
            raise ValueError('The given coordinates are out of the grid.')
        lat = float(darr.latitude)
        lon = float(darr.longitude)
        header = True
        fname = format_filename(lat, lon)
        try:
            with open(fname, 'x') as f:
                for year, month in product(YEARS, MONTHS):
                    str_month = STR_MONTHS[month - 1]
                    self.strvar_current.set(f'Extracting {str_month} {year}...')
                    dsets = [load(year, month, p) for p in self.parameters]
                    ds = xr.merge(dsets, join='exact')
                    df = ds.to_dataframe().set_index('time', append=True).swaplevel()
                    df[variables][1:].to_csv(
                        f, header=header, line_terminator='\n')
                    if header:
                        header = False
                    self.pb_progress.step(1)
            showinfo(title='Output file', message=f'Time series file {fname} written in directory {APPMAR2_DIR}')
        except FileExistsError:
            showerror(title='File already exist', message=f'You are trying to extract time series from a point you already extracted. You can find the time series file {fname} in {APPMAR2_DIR}')
        self.dlg_progress.close()

    def show_extract_progress(self):
        self.dlg_input_coord.close()
        self.show_dlg_progress()
        self.pb_progress['value'] = 0
        self.pb_progress['maximum'] = NMONTHS
        Thread(target=self.extract_series).start()

    def on_toggle_hs(self):
        self.toggle_parameter('hs')

    def on_toggle_tp(self):
        self.toggle_parameter('tp')

    def on_toggle_dp(self):
        self.toggle_parameter('dp')

    def on_toggle_wind(self):
        self.toggle_parameter('wind')

    def on_download(self):
        self.show_dlg_select_grid()
        self.btn_grid_start['command'] = self.show_download_progress

    def on_extract(self):
        self.show_dlg_select_grid()
        self.btn_grid_start['text'] = 'Continue'
        self.btn_grid_start['command'] = self.show_dlg_input_coord

    def on_load(self):
        fname = askopenfilename()
        if fname == '':
            return

        def date_parser(x): return datetime.strptime(x, '%Y-%m-%d')
        self.data = pd.read_csv(
            fname,
            parse_dates=['time'],
            date_parser=date_parser
        )
        try:
            lat, lon = parse_fname(fname)
            str_lat = format_as_dms(lat, 'lat')
            str_lon = format_as_dms(lon, 'lon')
            # it's an en dash, not a hyphen
            self.frm_map.config(text=f'{str_lat} – {str_lon}')
            save_map('map.png', lon, lat)
            photo = PhotoImage(file='map.png')
            self.lbl_map.config(image=photo)
            self.lbl_map.photo = photo
        except:
            pass
        showinfo(title='Load file', message=f'File {fname} was correctly loaded. Now you can run analyses and generate plots.')

    def on_distrib(self):
        if self.data is None:
            return
        lbl = self.cb_distrib.get()
        if "Joint" in lbl:
            plot_joint(
                self.data[DISTRIB[lbl][0]],
                self.data[DISTRIB[lbl][1]],
                LABELS[DISTRIB[lbl][0]],
                LABELS[DISTRIB[lbl][1]]
            )
            return
        plot_dist(
            self.data[DISTRIB[lbl][0]].values,
            LABELS[DISTRIB[lbl][0]]
        )

    def on_rose(self):
        rosetype = self.builder.tkvariables['rosetype'].get()
        if rosetype == 'wind':
            u = self.data['u']
            v = self.data['v']
            plot_rose(
                azimuth(u, v),
                np.sqrt(u**2 + v**2),
                LABELS[rosetype]
            )
            return
        plot_rose(
            self.data['dirpw'].values,
            self.data[VARS[rosetype][0]].values,
            LABELS[rosetype]
        )

    def on_ext(self):
        pass