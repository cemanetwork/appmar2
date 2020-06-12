import cartopy.crs as ccrs 
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

def map(filename,lon,lat):
    fig = plt.figure(figsize=(2.5,1.25))
    ax = plt.axes(projection=ccrs.PlateCarree())
    fig.subplots_adjust(right=0.995, bottom=0.005, top=1, left=0)#ajustar tamaño
    ax.gridlines(linewidth=0.5, color='black', alpha=0.2, linestyle='--')
    zoom = 10 # centrar la vista del punto
    extent = [lon-(zoom*2.4),lon+(zoom*1.9),lat-zoom,lat+zoom]
    ax.set_extent(extent) 
    plt.plot(lon,lat, markersize=4, marker='v', color='red',transform=ccrs.Geodetic())

    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE,linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5,linestyle=':')
    ax.add_feature(cfeature.LAKES, alpha=0.2)
    ax.add_feature(cfeature.RIVERS,linewidth=0.5)   
    plt.show()
    #plt.savefig(filename)
map("Prueba.png",-76.259029,10.691575,)
