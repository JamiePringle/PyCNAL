import numpy as np
import matplotlib.pyplot as plt
from  matplotlib import cm, colors
from mpl_toolkits.basemap import Basemap
import pycnal
import pycnal_toolbox


def twoDview(var, tindex, grid, filename=None, \
          cmin=None, cmax=None, clev=None, fill=False, \
          contour=False, d=4, range=None, fts=None, \
          title=None, clb=True, pal=None, proj='merc', \
          fill_land=False, outfile=None):
    """
    map = twoDview(var, tindex, grid, {optional switch})

    optional switch:
      - filename         if defined, load the variable from file
      - cmin		 set color minimum limit
      - cmax		 set color maximum limit
      - clev		 set the number of color step
      - fill             use contourf instead of pcolor
      - contour          overlay contour (request fill=True)
      - d                contour density (default d=4) 
      - range            set axis limit
      - fts              set font size (default: 12)
      - title            add title to the plot
      - clb              add colorbar (defaul: True)
      - pal              set color map (default: cm.jet)
      - proj             set projection type (default: merc)
      - fill_land        fill land masked area with gray (defaul: True)
      - outfile          if defined, write figure to file

    plot 2-dimensions variable var. If filename is provided,
    var must be a string and the variable will be load from the file.
    grid can be a grid object or a gridid. In the later case, the grid
    object correponding to the provided gridid will be loaded.
    If proj is not None, return a Basemap object to be used with quiver 
    for example. 
    """

    # get grid
    if type(grid).__name__ == 'ROMS_Grid':
        grd = grid
    else:
        grd = pycnal.grid.get_ROMS_grid(grid)


    # get variable
    if filename == None:
        var = var
    else:
        data = pycnal.io.Dataset(filename)

        var = data.variables[var]


    Np, Mp, Lp = grd.vgrid.z_r[0,:].shape

    if tindex is not -1:
        assert len(var.shape) == 3, 'var must be 3D (time plus space).'
        K, M, L = var.shape
    else:
        assert len(var.shape) == 2, 'var must be 2D (no time dependency).'
        M, L = var.shape

    # determine where on the C-grid these variable lies
    if M == Mp and L == Lp:
        Cpos='rho'
        if fill == True:
            lon = grd.hgrid.lon_rho
            lat = grd.hgrid.lat_rho
        else:
            lon = grd.hgrid.lon_vert
            lat = grd.hgrid.lat_vert
        mask = grd.hgrid.mask_rho

    if M == Mp and L == Lp-1:
        Cpos='u'
        if fill == True:
            lon = grd.hgrid.lon_u
            lat = grd.hgrid.lat_u
        else:
            lon = 0.5 * (grd.hgrid.lon_vert[:,:-1] + grd.hgrid.lon_vert[:,1:])
            lat = 0.5 * (grd.hgrid.lat_vert[:,:-1] + grd.hgrid.lat_vert[:,1:])
        mask = grd.hgrid.mask_u

    if M == Mp-1 and L == Lp:
        Cpos='v'
        if fill == True:
            lon = grd.hgrid.lon_v
            lat = grd.hgrid.lat_v
        else:
            lon = 0.5 * (grd.hgrid.lon_vert[:-1,:] + grd.hgrid.lon_vert[1:,:])
            lat = 0.5 * (grd.hgrid.lat_vert[:-1,:] + grd.hgrid.lat_vert[1:,:])
        mask = grd.hgrid.mask_v

    if M == Mp-1 and L == Lp-1:
        Cpos='psi'
        if fill == True:
            lon = grd.hgrid.lon_psi
            lat = grd.hgrid.lat_psi
        else:
            lon = grd.hgrid.lon_rho
            lat = grd.hgrid.lat_rho
        mask = grd.hgrid.mask_psi

    # get 2D var
    if tindex == -1:
        var = var[:,:]
    else:
        var = var[tindex,:,:]

    # mask
    var = np.ma.masked_where(mask == 0, var)

    # plot
    if cmin is None:
        cmin = var.min()
    else:
        cmin = float(cmin)

    if cmax is None:
        cmax = var.max()
    else:
        cmax = float(cmax)

    if clev is None:
        clev = 100.
    else:
        clev = float(clev)

    dc = (cmax - cmin)/clev ; vc = np.arange(cmin,cmax+dc,dc)

    if pal is None:
        pal = cm.jet
    else:
        pal = pal

    if fts is None:
        fts = 12
    else:
        fts = fts

    #pal.set_over('w', 1.0)
    #pal.set_under('w', 1.0)
    #pal.set_bad('w', 1.0)

    pal_norm = colors.BoundaryNorm(vc,ncolors=256, clip = False)

    if range is None:
        lon_min = lon.min()
        lon_max = lon.max()
        lon_0 = (lon_min + lon_max) / 2.
        lat_min = lat.min()
        lat_max = lat.max()     
        lat_0 = (lat_min + lat_max) / 2.
    else:
        lon_min = range[0]
        lon_max = range[1]
        lon_0 = (lon_min + lon_max) / 2.
        lat_min = range[2]
        lat_max = range[3]
        lat_0 = (lat_min + lat_max) / 2.

    # clear figure
    #plt.clf()

    if proj is not None:
        map = Basemap(projection=proj, llcrnrlon=lon_min, llcrnrlat=lat_min, \
              urcrnrlon=lon_max, urcrnrlat=lat_max, lat_0=lat_0, lon_0=lon_0, \
                 resolution='h', area_thresh=5.)
        #map = pycnal.utility.get_grid_proj(grd, type=proj)
        x, y = list(map(lon,lat))
    
    if fill_land is True and proj is not None:
        # fill land and draw coastlines
        map.drawcoastlines()
        map.fillcontinents(color='grey')
    else:
        if proj is not None: 
            Basemap.pcolor(map, x, y, mask, vmin=-2, cmap=cm.gray, edgecolors='face')
            pycnal_toolbox.plot_coast_line(grd, map)
        else: 
            plt.pcolor(lon, lat, mask, vmin=-2, cmap=cm.gray, edgecolors='face')
            pycnal_toolbox.plot_coast_line(grd)
    
    if fill is True:
        if proj is not None: 
            cf = Basemap.contourf(map, x, y, var, vc, cmap = pal, \
                                  norm = pal_norm)
        else: 
            cf = plt.contourf(lon, lat, var, vc, cmap = pal, \
                              norm = pal_norm)
    else:
        if proj is not None: 
            cf = Basemap.pcolor(map, x, y, var, cmap = pal, norm = pal_norm, edgecolors='face')
        else: 
            cf = plt.pcolor(lon, lat, var, cmap = pal, norm = pal_norm, edgecolors='face')

    if clb is True:
    	clb = plt.colorbar(cf, fraction=0.075,format='%.2f')
    	for t in clb.ax.get_yticklabels():
    	    t.set_fontsize(fts)

    if contour is True:
        if fill is not True:
            raise Warning('Please run again with fill=True to overlay contour.')
        else:
            if proj is not None:
                Basemap.contour(map, x, y, var, vc[::d], colors='k', linewidths=0.5, linestyles='solid')
            else: 
                plt.contour(lon, lat, var, vc[::d], colors='k', linewidths=0.5, linestyles='solid')

    if proj is None and range is not None:
        plt.axis(range) 


    if title is not None:
            plt.title(title, fontsize=fts+4)

    if proj is not None:
        map.drawmeridians(np.arange(lon_min,lon_max, (lon_max-lon_min)/5.), \
                          labels=[0,0,0,1], fmt='%.1f')
        map.drawparallels(np.arange(lat_min,lat_max, (lat_max-lat_min)/5.), \
                          labels=[1,0,0,0], fmt='%.1f')

    if outfile is not None:
        if outfile.find('.png') != -1 or outfile.find('.svg') != -1 or \
           outfile.find('.eps') != -1:
            print('Write figure to file', outfile)
            plt.savefig(outfile, dpi=200, facecolor='w', edgecolor='w', \
                        orientation='portrait')
        else:
            print('Unrecognized file extension. Please use .png, .svg or .eps file extension.')	 


    if proj is None:
        return
    else:
        return map
