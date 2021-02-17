#######################################################
# Miscellaneous useful tools for xarray
#######################################################

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from numpy.polynomial.polynomial import polyval,polyfit
import matplotlib.dates as dates
import xarray as xr

#--------------------------------------------------------------------------
# anomaly plot
def anomaly(ax,x,y,offset):
    ax.fill_between(x, 0+offset[0], y, where = y>0+offset[0], facecolor='indianred', interpolate=True)
    ax.fill_between(x, 0-offset[1], y, where = y<0-offset[1], facecolor='royalblue', interpolate=True)

#
#
#--------------------------------------------------------------------------
# for comparison find common values for vmin and vmax so that colormap is equal
def find_common_cmax(data1,data2):    
    vmin1 = np.round(np.min((data1.fillna(0).values,data1.fillna(0).values)),decimals=2)
    vmax1 = np.round(np.max((data1.fillna(-100000).values,data1.fillna(-100000).values)),decimals=2)
    vmin2 = np.round(np.min((data2.fillna(0).values,data2.fillna(0).values)),decimals=2)
    vmax2 = np.round(np.max((data2.fillna(-100000).values,data2.fillna(-100000).values)),decimals=2)    
    vval = np.max(np.abs((vmin1,vmax1,vmin2,vmax2)))
    return vval

#
#
#--------------------------------------------------------------------------
# derive weighted mean if weights are provides, normal mean otherwise
def mean_weighted(self, dim=None, weights=None):
    if weights is None:
        return self.mean(dim)
    else:
        return (self * weights).sum(dim) / weights.sum(dim)

#
#
#--------------------------------------------------------------------------
# rolling cross-correlation    
def rolling_xcorr(ds,var,window):
    """
    Function to perform moving window cross-correlation
    
    As I haven't found another way yet, the xarray data is converted into pandas array 
    and back to xarray at the end.
    Interpolates across NaNs
    
    INPUT:
    ds = xarray dataset with both variables
    var = array with both variable names
    window = window size as integer
    
    OUTPUT:
    rolling_r = vector with rolling correlation coefficient (padded with nan at sides)
    
    """
    
    # separate both time series, convert to pandas and interpolate in case of nans
    var1 = ds[var[0]].to_dataframe().interpolate()
    var2 = ds[var[1]].to_dataframe().interpolate()

    # rolling window correlation
    # Compute rolling window synchrony
    rolling_r = var1[var[0]].rolling(window=window, center=True).corr(var2[var[1]])
    
    return rolling_r