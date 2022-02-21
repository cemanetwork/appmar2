from math import tau  # tauday.com - Pi is wrong

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import seaborn as sns
import statsmodels.api as sm
import xarray as xr
from matplotlib import rc

import cartopy.crs as ccrs
import cartopy.feature as cfeature

plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.rm'] = 'serif'
plt.rcParams['mathtext.it'] = 'serif:italic'
plt.rcParams['mathtext.bf'] = 'serif:bold'
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 8.0
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams["figure.dpi"] = 300

WIDTH = 3.24
HEIGHT = 2.29

MAPWIDTH = 2.5
MAPHEIGHT = 1.25

NDIRS = 16
DIRS = np.linspace(0, 15*tau/16, 16)
RANGE = (-11.25, 371.25)
BARWIDTH = tau/16

STR_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def plot_dist(data, lbl):
    kde = sm.nonparametric.KDEUnivariate(data)
    kde.fit(bw='scott', gridsize=100, cut=0)
    fig, ax1 = plt.subplots(figsize=(WIDTH, HEIGHT))
    ax2 = ax1.twinx()
    bins = min(sns.distributions._freedman_diaconis_bins(data), 50)
    ax1.hist(data, bins=bins, density=True, color='0.75')
    ax2.plot(kde.support, kde.cdf, color='k')
    ax2.set_ylim([0, ax2.get_ylim()[1]])
    ax1.set_xlabel(lbl)
    ax1.set_ylabel('Probability density')
    ax2.set_ylabel('Cumulative probability')
    fig.tight_layout()
    fig.show()


def plot_joint(x, y, xlbl, ylbl):
    fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT))
    cmap = sns.cubehelix_palette(rot=0, hue=1, light=1, dark=0, as_cmap=True)
    sns.kdeplot(x, y, shade=True, shade_lowest=False,
                cut=0, cbar=True, cbar_kws={'label': 'Probability density'}, cmap=cmap)
    ax.set_xlabel(xlbl)
    ax.set_ylabel(ylbl)
    fig.tight_layout()
    fig.show()


def roseplot(d, x, bins=5, quantiles=False, opening=1.0, dirnames=False, xlabel=None, cmap=None, ax=None):
    if quantiles:
        bin_edges = np.quantile(x, np.linspace(0, 1, bins + 1))
    else:
        bin_edges = np.histogram_bin_edges(x, bins)
    bin_edges[-1] = np.inf
    n = len(d)
    hists = np.empty((bins, NDIRS))
    lbls = []
    for i in range(bins):
        x1 = bin_edges[i]
        x2 = bin_edges[i + 1]
        dbin = d[np.logical_and(x1 <= x, x < x2)]
        *hists[i], last = np.histogram(
            dbin, bins=NDIRS + 1, range=RANGE)[0] / n
        hists[i, 0] += last
        lbls.append(f'{x1:.1f}–{x2:.1f}')
    if ax is None:
        ax = plt.subplot(polar=True)
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location("N")
    if dirnames:
        ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
    if isinstance(cmap, str) or cmap is None:
        cmap = plt.get_cmap(cmap)
    colors = cmap(np.linspace(0, 1, bins))
    bottoms = np.empty_like(hists)
    bottoms[0] = 0
    bottoms[1:] = np.cumsum(hists[:-1], 0)
    width = opening * BARWIDTH
    for hist, color, lbl, bottom in zip(hists, colors, lbls, bottoms):
        ax.bar(DIRS, hist, width=width, color=color, label=lbl, bottom=bottom)
    ax.legend(loc='center left', bbox_to_anchor=(1.2, 0.5), title=xlabel)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0))
    return ax


def plot_rose(d, x, lbl):
    fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT),
                           subplot_kw={'projection': 'polar'})
    roseplot(d, x, dirnames=True, xlabel=lbl, ax=ax)
    fig.tight_layout()
    fig.show()


def save_map(filename, lon, lat):
    fig, ax = plt.subplots(figsize=(MAPWIDTH, MAPHEIGHT), subplot_kw={
                           'projection': ccrs.PlateCarree()})
    fig.subplots_adjust(right=0.995, bottom=0.005,
                        top=1, left=0)  # remove borders
    ax.gridlines(linewidth=0.5, color='black', alpha=0.2, linestyle='--')
    zoom = 10  # center the view
    ax.set_extent([lon-(zoom*2.4), lon+(zoom*1.9), lat-zoom, lat+zoom])
    ax.plot(lon, lat, markersize=4, marker='v',
             color='red', transform=ccrs.Geodetic())
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle=':')
    ax.add_feature(cfeature.LAKES, alpha=0.2)
    ax.add_feature(cfeature.RIVERS, linewidth=0.5)
    fig.savefig(filename, dpi=100)


def plot_clusters(pairs, centers, labels):
    fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT))
    sns.scatterplot(x=pairs[:, 0], y=pairs[:, 1], hue=labels.astype(str), ax=ax, s=2)
    ax.get_legend().remove()
    ax.scatter(centers[:, 0], centers[:, 1], c="white", s=10, edgecolor="k")
    ax.set_xlabel("Significant wave height (m)")
    ax.set_ylabel("Period (s)")
    fig.tight_layout()
    fig.show()

def plot_pot_month(df, str_p):
    q = int(str_p) / 100
    th = df.swh.quantile(q)
    nyears = len(df.time.dt.year.unique())
    pot = df.time[df.swh > th].groupby(df.time.dt.month).agg({"count"}) / nyears
    fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT))
    npeaks = pot.values.flatten()
    b = ax.bar(STR_MONTHS, npeaks, color="gray", label=f"$H_s$ > {th:.2f} m (P{str_p})")
    # ax.bar_label(b, fmt="%.1f", size=6)
    ax.set_ylabel("Average number of events per year")
    ax.tick_params(axis="x", labelrotation=60)
    ax.legend(handlelength=0,handletextpad=0, frameon=False)
    fig.tight_layout()
    fig.show()
    return (STR_MONTHS, npeaks, th)