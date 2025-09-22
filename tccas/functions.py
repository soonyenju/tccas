import os, sys, shutil, warnings
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def setup_canvas(nx, ny, figsize = (10, 6), sharex = True, sharey = True, markersize = 2, fontsize = 16, flatten = True, labelsize= 15, wspace = 0, hspace = 0, panels = False):
    plt.rcParams.update({'lines.markersize': markersize, 'font.size': fontsize})
    fig, axes = plt.subplots(nx, ny, figsize = figsize, sharex = sharex, sharey = sharey)
    if nx * ny == 1: axes = np.array([axes])
    if flatten: axes = axes.flatten()
    for ax in axes.flatten():
        ax.tick_params(direction = "in", which = "both", labelsize = labelsize)

    if panels:
        for i in range(len(axes)):
            axes[i].text(0.05, 0.8, f'({chr(97 + i)})', transform = axes[i].transAxes)

    plt.subplots_adjust(wspace = wspace, hspace = hspace)

    if len(axes) == 1:
        return fig, axes[0]
    else:
        return fig, axes
    
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

def load_csv(p, index_col = 0, format = '%Y-%m-%d'):
    df = pd.read_csv(p, index_col = 0)
    df.index = pd.to_datetime(df.index, format = format)
    return df

def load_output_meta(site, root_proj, prior = True):
    if prior: 
        suffix = '_prior'
    else:
        suffix = '_posterior'
    
    loadfolder = root_proj.joinpath(f'resources/{site}{suffix}')
    meta = []
    for p in loadfolder.glob('*.nc'):
        _, freq, dt2 = p.stem.split('_')
        freq = freq.split('-')[0]
        dt_s, dt_e = dt2.split('-')
        dt_s = pd.to_datetime(dt_s, format = '%Y%m%d')
        dt_e = pd.to_datetime(dt_e, format = '%Y%m%d')
        meta.append([freq, dt_s, dt_e, p])

    meta = pd.DataFrame(meta, columns = ['FREQ', 'START', 'END', 'PATH']).set_index('FREQ')
    return meta


import xarray as xr

def load_DB_outputs(site, root_proj, prior = True, freq = 'daily'):
    if freq == 'daily':
        sites_database = load_DB_outputs_daily(site, root_proj, prior = prior)
    else:
        assert freq == 'hourly', f'ERROR: {freq}'
        sites_database = load_DB_outputs_hourly(site, root_proj, prior = prior)
    return sites_database

def load_DB_outputs_daily(site, root_proj, prior = True, force_regenerate = True):
    if prior: 
        suffix = '_prior'
    else:
        suffix = '_posterior'
    meta = load_output_meta(site, root_proj, prior = prior)
    ncd = xr.open_dataset(meta.loc['daily', 'PATH']) # daily netcdf

    savefile0 = root_proj.joinpath(f'resources/{site}{suffix}_daily_pft0.csv')
    savefile1 = root_proj.joinpath(f'resources/{site}{suffix}_daily_pft1.csv')

    day_sites_database = {} # dictionnary in format {site: data}
    if (not force_regenerate) & savefile0.exists() & savefile1.exists():
        dft = pd.read_csv(savefile0, index_col = 0)
        dft.index = pd.to_datetime(dft.index, format = '%Y-%m-%d')
        day_sites_database[0] = dft
        dft = pd.read_csv(savefile1, index_col = 0)
        dft.index = pd.to_datetime(dft.index, format = '%Y-%m-%d')
        day_sites_database[1] = dft
    else:
        for g, gp in ncd.to_dataframe().reset_index().groupby('nsp'):
            # lonlat = gp[['lon', 'lat']].drop_duplicates().reset_index(drop = True)
            # assert len(lonlat) == 1, 'Wrong number of sites'
            gp = gp.set_index('time').drop(['nsp', 'ntc', 'yyyymmdd'], axis = 1).drop_duplicates()
            # day_sites_database[g] = [lonlat, gp]
            day_sites_database[g] = gp

        day_sites_database[0].to_csv(savefile0)
        day_sites_database[1].to_csv(savefile1)
    return day_sites_database

def load_DB_outputs_hourly(site, root_proj, prior = True, force_regenerate = True):
    if prior: 
        suffix = '_prior'
    else:
        suffix = '_posterior'
    meta = load_output_meta(site, root_proj, prior = prior)
    nch = xr.open_dataset(meta.loc['hourly', 'PATH']) # hourly netcdf
    nch_vars = list(nch.variables)

    savefile0 = root_proj.joinpath(f'resources/{site}{suffix}_hourly_pft0.csv')
    savefile1 = root_proj.joinpath(f'resources/{site}{suffix}_hourly_pft1.csv')

    hour_sites_database = {} # dictionnary in format {site: data}
    if (not force_regenerate) & savefile0.exists() & savefile1.exists():
        dft = pd.read_csv(savefile0, index_col = 0)
        dft.index = pd.to_datetime(dft.index, format = '%Y-%m-%d %H:%M:%S')
        hour_sites_database[0] = dft
        dft = pd.read_csv(savefile1, index_col = 0)
        dft.index = pd.to_datetime(dft.index, format = '%Y-%m-%d %H:%M:%S')
        hour_sites_database[1] = dft
    else:
        for g in nch['nsp'].data:
            # print(f'Converting site {g} data into dataframe...')
            dat = nch[[
                'swrad', 'temperature', 'raux', 'fapar', 'sif', 'trans', 
                'pevap_soil', 'pevap_canopy', 'temp_sd', 'temp_sw', 'temp_canopy', 
                'rn_s', 'rn_c', 'vpd', 'rld', 'rlu', 'rho_tot', 'gpp', 'raut', 'rhet', 'nee'
            ]].copy()
            dft = dat.where(dat['nsp'] == g, drop = True).to_dataframe()
            dft.index = dft.index.droplevel(level = 1)
            dat.close(); del(dat) # delete the temporary data array that is no longer in use.

            # ===========================================================================================================================================
            dat = nch['gs'].copy()
            gs = dat.where(dat['nsp'] == g, drop = True).to_dataframe().reset_index().drop('nsp', axis = 1).pivot(index = 'time', columns = 'nlayer')
            gs.columns = [('{0}l{1}'.format(*tup)) for tup in gs.columns]
            dat.close(); del(dat) # delete the temporary data array that is no longer in use.

            # ===========================================================================================================================================
            dat = nch['cpools'].copy()
            pools = dat.where(dat['nsp'] == g, drop = True).to_dataframe().reset_index().drop('nsp', axis = 1).pivot(index = 'time', columns = 'ncpool')
            pools.columns = pools.columns.droplevel(0)
            pools.columns = dat.pool_names.split(',')
            dat.close(); del(dat) # delete the temporary data array that is no longer in use.

            # ===========================================================================================================================================
            dat = nch['cfluxes'].copy()
            fluxes = dat.where(dat['nsp'] == g, drop = True).to_dataframe().reset_index().drop('nsp', axis = 1).pivot(index = 'time', columns = 'ncflux')
            fluxes.columns = fluxes.columns.droplevel(0)
            fluxes.columns = dat.flux_names.split(',')
            dat.close(); del(dat) # delete the temporary data array that is no longer in use.

            hour_sites_database[g] = pd.concat([dft, gs, pools, fluxes], axis = 1)

        hour_sites_database[0].to_csv(savefile0)
        hour_sites_database[1].to_csv(savefile1)
    return hour_sites_database

def load_observations(site_obs, root_proj, freq = 'daily', mode = 'csv'):

    import datetime
    columns_dict = {
        'fapar':  ['FAPAR', 'sigma FAPAR' ] + ['ipft1', 'fcov ipft1', 'ipft2', 'fcov ipft_2'],
        'lvod':  ['VOD', 'sigma VOD' ] + ['ipft1', 'fcov ipft1', 'ipft2', 'fcov ipft_2'],
        'gpp':  ['GPP', 'sigma GPP' ] + ['ipft1', 'fcov ipft1', 'ipft2', 'fcov ipft_2'],
        'nee':  ['NEE', 'sigma NEE' ] + ['ipft1', 'fcov ipft1', 'ipft2', 'fcov ipft_2'],
        'sif':  ['SIF_743NM', 'sigma SIF_743NM'] + ['ipft1', 'fcov ipft1', 'ipft2', 'fcov ipft_2'],
        'slope':  ['SLOPE_MASKED', 'sigma SLOPE_MASKED'] + ['ipft1', 'fcov ipft1', 'ipft2', 'fcov ipft_2'],
        'sm':  ['SM', 'sigma SM'] + ['ipft1', 'fcov ipft1', 'ipft2', 'fcov ipft_2'],
        'tip-fapar':  ['FAPAR', 'sigma FAPAR'] + ['ipft1', 'fcov ipft1', 'ipft2', 'fcov ipft_2']
    }

    obs_database = {}
    for p in root_proj.joinpath('observations').glob(f'*_{site_obs}.csv'):
        var_ = p.stem.split('_')[0]

        with open(p, 'r') as f:
            # lines = [" ".join(l.split()) for l in f.readlines()]
            # columns = f.readline()
            # print(var_, " ".join(columns.split()).split('ipft')[0].split('ihour')[1])
            # print(f'Loading observations of {var_}')
            lines = [l.split() for l in f.readlines()[1::]]
            dft = pd.DataFrame(lines, columns = ['ihour'] + columns_dict[var_])
            dft = dft.astype(float)

            dft['ihour'] = dft['ihour'].map(
                lambda ihour: datetime.datetime(2015,1,1) + datetime.timedelta(hours=ihour)
            )
            dft = dft.rename(columns = {'ihour': 'time'})
            dft = dft.set_index('time', drop = True)
        
        if freq == 'daily': dft = dft
        obs_database[var_] = dft
    if (mode == 'csv') & (freq == 'daily'):
        return pd.concat([
            obs_database['lvod']['VOD'].rename('vod'),
            obs_database['lvod']['sigma VOD'].rename('vod_unc'),
            obs_database['gpp']['GPP'].rename('gpp') * 86400,
            obs_database['gpp']['sigma GPP'].rename('gpp_unc'),
            obs_database['nee']['NEE'].rename('nee') * 86400,
            obs_database['nee']['sigma NEE'].rename('nee_unc'),
            obs_database['slope']['SLOPE_MASKED'].rename('slope'),
            obs_database['slope']['sigma SLOPE_MASKED'].rename('slope_unc'),
            obs_database['fapar']['FAPAR'].rename('fapar'),
            obs_database['fapar']['sigma FAPAR'].rename('fapar_unc'),
            obs_database['sif']['SIF_743NM'].rename('sif743'),
            obs_database['sif']['sigma SIF_743NM'].rename('sif743_unc'),
            obs_database['sm']['SM'].rename('soil_moisture'),
            obs_database['sm']['sigma SM'].rename('soil_moisture_unc'),
            # obs_database['tip-fapar']['FAPAR']
        ], axis = 1).resample('1D').mean()
    elif (mode == 'csv') & (freq == 'hourly'):
        return pd.concat([
            obs_database['lvod']['VOD'].rename('vod'),
            obs_database['lvod']['sigma VOD'].rename('vod_unc'),
            obs_database['gpp']['GPP'].rename('gpp'),
            obs_database['gpp']['sigma GPP'].rename('gpp_unc'),
            obs_database['nee']['NEE'].rename('nee'),
            obs_database['nee']['sigma NEE'].rename('nee_unc'),
            obs_database['slope']['SLOPE_MASKED'].rename('slope'),
            obs_database['slope']['sigma SLOPE_MASKED'].rename('slope_unc'),
            obs_database['fapar']['FAPAR'].rename('fapar'),
            obs_database['fapar']['sigma FAPAR'].rename('fapar_unc'),
            obs_database['sif']['SIF_743NM'].rename('sif'),
            obs_database['sif']['sigma SIF_743NM'].rename('sif743_unc'),
            obs_database['sm']['SM'].rename('soil_moisture'),
            obs_database['sm']['sigma SM'].rename('soil_moisture_unc'),
            # obs_database['tip-fapar']['FAPAR']
        ], axis = 1)

    else:
        return obs_database

def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)

def copybak(root_proj):
    '''
    back up resources to working directory
    '''
    for fname in ['ES-LM1_prior', 'FI-Sod_prior', 'ES-LM1_posterior', 'FI-Sod_posterior']:
        src = root_proj.parent.joinpath('resources_bak').joinpath(fname)
        dst = root_proj.joinpath('resources').joinpath(fname)
        copytree(src, dst)
                
def copy2bak(root_proj):
    '''
    create back up resources
    '''
    for fname in ['ES-LM1_prior', 'FI-Sod_prior', 'ES-LM1_posterior', 'FI-Sod_posterior']:
        src = root_proj.joinpath('resources').joinpath(fname)
        dst = root_proj.parent.joinpath('resources_bak').joinpath(fname)
        copytree(src, dst)
        
def get_PFT_name(df):
    pft_codes = ['NoVeg', 'TrEv', 'TrDD','TmEv','TmSg', 'EvCn', 'SgCn', 'EShr', 'DShr', 'C3Gr', 'C4Gr', 'Tun', 'VSwamp', 'ArbC']
    pft_dict = dict(zip(np.arange(len(pft_codes)), pft_codes))
    pft_val = pft_dict[int(df['pft'].drop_duplicates().values)]
    return pft_val

def aggPFT(df1, df2, aggVar):
    if aggVar.lower() == 'vod':
        isVOD = True
    else:
        isVOD = False
    if isVOD:
        dfo = -np.log(np.exp(-df1[aggVar]) * df1['pft_fraction'] + np.exp(-df2[aggVar]) * df2['pft_fraction'])
    else:
        dfo = df1[aggVar] * df1['pft_fraction'] + df2[aggVar] * df2['pft_fraction']
    return dfo.rename(aggVar)

def set_iteration_number(root_proj, niter = 1000, verbose = 1):
    with open(root_proj.joinpath('opt.nml'), 'r') as f:
        lines = f.readlines()
    niter_in = lines[4].strip().split(' = ')[1]

    lines_out = [lines[i] if i != 4 else f' itmax = {niter}\n' for i in range(len(lines))]

    with open(root_proj.joinpath('opt.nml'), 'w') as f:
        f.writelines(lines_out)
    if verbose != 0:
        print(f"The iteration number 'itmax' has been changed from {niter_in} to {niter}")