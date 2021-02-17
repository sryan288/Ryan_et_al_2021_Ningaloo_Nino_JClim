'''
 Plotting utilities for the Northwest Atlantic
'''
'''
    1) plot_map          Plot bathymetry map of NWA
    2) finished_plot     Either show plot or save if name is provided
    3) calculate_ticks   Align ticks for twinx or twiny
    4) find_bounds       Find bounds for vmin,vmax based in max,min values in dataset
    5) plot_ipo_bar      Plot bar indicating IPO phases on top of panel
'''

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
import matplotlib.dates as dates
import xarray as xr


#
#------------------------------------------------------------------------
# 1) plot bathymetry map

def plot_map(figsize=(10,8),c=np.arange(0,6000,500)):
    " Input: figsize"
    
    # bounds to cut out NWA
    x_bnds, y_bnds = [810,993], [602,758]
    
    # open bathymetry
    bathy = xr.open_dataset('/vortex/clidex/data/ORCA/mesh_files/mesh_zgr.nc').sel(x=slice(*x_bnds),y=slice(*y_bnds))
    bathy['hdept'] = bathy['hdept'].where(bathy['hdept']!=0)

    ########## Plotting ####################
    proj = ccrs.PlateCarree()

    fig,ax = plt.subplots(figsize=figsize,subplot_kw = dict(projection=proj))
    # Bathymetry
    cc= ax.pcolormesh(bathy.nav_lon,bathy.nav_lat,bathy['hdept'][0,:,:],
                    cmap=plt.get_cmap('Blues',len(c)),vmin=np.min(c),vmax=np.max(c))
    # formatting
    ax.set_extent([-78,-60,30,48])
    ax.coastlines(resolution='50m',color='gray')
    gl = ax.gridlines(crs=proj,draw_labels=True)
    #                             xlocs=range(-0,160,20),ylocs=range(-45,45,15))
    gl.yformatter = LATITUDE_FORMATTER
    gl.xformatter = LONGITUDE_FORMATTER
    ax.add_feature(cartopy.feature.LAND, color='lightgray')

    #     if i==0: gl.ylabels_right = False
    gl.ylabels_right = False
#     plt.colorbar(cc)
    return fig,ax


#
#------------------------------------------------------------------------
# 2) If a figure name is defined, save the figure to that file. Otherwise, display the figure on screen.
def finished_plot (fig, fig_name=None, dpi=300):

    if fig_name is not None:
        print('Saving ' + fig_name)
        fig.savefig(fig_name, dpi=dpi,bbox_inches='tight')
    else:
        fig.show()
        
        
#
#
#-------------------------------------------------------------------------
# 3) align ticks for twin axes
def calculate_ticks(ax, ticks,axis = 'x', round_to=0.1, center=False):
    if axis=='x':
        upperbound = np.ceil(ax.get_xbound()[1]/round_to)
        lowerbound = np.floor(ax.get_xbound()[0]/round_to)
    elif axis=='y':
        upperbound = np.ceil(ax.get_ybound()[1]/round_to)
        lowerbound = np.floor(ax.get_ybound()[0]/round_to)
    dy = upperbound - lowerbound
    fit = np.floor(dy/(ticks - 1)) + 1
    dy_new = (ticks - 1)*fit
    if center:
        offset = np.floor((dy_new - dy)/2)
        lowerbound = lowerbound - offset
    values = np.linspace(lowerbound, lowerbound + dy_new, ticks)
    return values*round_to


#
#
#-------------------------------------------------------------------------
# 4) Find bounds for vmin,vmax based in max,min values in dataset
def find_bounds(ds,decimals,anomaly=False):
    vmin = np.round(ds.min(skipna=True).values- 0.5 * 10**(-decimals),decimals=int(decimals)) # work around, as floor&ceil don't take decimals
    vmax = np.round(ds.max(skipna=True).values+ 0.5 * 10**(-decimals),decimals=int(decimals))
    if anomaly is True:
        vmax = np.max(np.abs((vmin,vmax)))
        vmin = vmax*(-1)
    return vmin,vmax

#
#
#
#------------------------------------------------------------------------
# add ipo phase as bar
# Create rectangle x coordinates
def add_ipo_bar(ax):
    import matplotlib.dates as mdates
    indices = xr.open_dataset('/vortex/clidex/data/obs/climate_indices/indices_noaa_psl_May_13_2020.nc')
    cols = ['dodgerblue','indianred','dodgerblue','indianred']
    text = ['-IPO','+IPO','-IPO','']
    years = [1956,1977,1999,2013,2020]
    for i in range(len(years)-1):
        startTime = indices.sel(Month=slice(str(years[i]) + '-01-01',str(years[i]) + '-01-31'))['Month'].values
        endTime =  indices.sel(Month=slice(str(years[i+1]-1) + '-12-01',str(years[i+1]-1) + '-12-31'))['Month'].values#startTime + timedelta(seconds = 1)
        # convert to matplotlib date representation
        start = mdates.date2num(startTime)
        end = mdates.date2num(endTime)
        width = end - start
        middle = (width/2)+start
        
        ulim = ax.get_ybound()[1]
        llim = ax.get_ybound()[1] - ax.get_ybound()[1]/6 
        rect = Rectangle((start[0], llim), width, ulim, color=cols[i],alpha=0.5)
        ax.text(middle,(ulim-llim)/2+llim,text[i],fontsize=8,fontweight='bold',verticalalignment='center',
               horizontalalignment='center')
        ax.add_patch(rect)
