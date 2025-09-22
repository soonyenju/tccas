import os, sys, shutil, warnings, subprocess
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import pyplot as plt
from pathlib import Path
from google.colab import drive

def config_netcdf():
    # Update package list
    subprocess.run(["apt-get", "update", "-qq"], check=True)
    
    # Install NetCDF C library
    subprocess.run(["apt-get", "install", "-y", "libnetcdf-dev"], check=True)
    
    # Install NetCDF Fortran library
    subprocess.run(["apt-get", "install", "-y", "libnetcdff-dev"], check=True)

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def prepare_tccas(home_dir):
    # Define paths
    source_file = Path("/content/drive/My Drive/tccas/bak/tccas_r10043.tgz")
    dest_file = home_dir.joinpath("tccas_r10043.tgz")
    extract_dir = home_dir.joinpath("tccas_r10043")

    # 1. Remove old copy if exists
    if dest_file.exists():
        print(f"Removing existing {dest_file}")
        dest_file.unlink()

    # 2. Copy file from Google Drive
    print(f"Copying {source_file} -> {dest_file}")
    subprocess.run(["cp", str(source_file), str(dest_file)], check=True)

    # 3. Extract tarball
    print(f"Extracting {dest_file}")
    subprocess.run(["tar", "-xvzf", str(dest_file)], check=True)

    # 4. Create symbolic link for mk.compile
    mk_compile_link = extract_dir / "mk.compile"
    mk_compile_target = extract_dir / "config" / "mk.compile-gfortran"

    print(f"Linking {mk_compile_target} -> {mk_compile_link}")
    if mk_compile_link.exists():
        mk_compile_link.unlink()  # remove existing link if needed

    # # If you work on '/content/':
    # subprocess.run(["ln", "-fs", str(mk_compile_target), str(mk_compile_link)], check=True)
    # If you work on Google Drive:
    subprocess.run(["cp", str(mk_compile_target), str(mk_compile_link)], check=True)

    print("✅ TCCAS prepared successfully!")

warnings.simplefilter('ignore')

drive.mount('/content/drive', force_remount = False)
# home_dir = Path('/content')
home_dir = Path('/content/drive/My Drive/tccas')
# home_dir = Path.cwd().joinpath('drive/My Drive/tccas')
# home_dir = [p for p in Path('/home').glob('*') if p.stem != 'conda'][0]
os.chdir(home_dir)
config_netcdf()
prepare_tccas(home_dir)
root_proj = home_dir.joinpath('tccas_r10043')
sys.path.append(root_proj.parent.joinpath('notebooks').as_posix())
sys.path.append(root_proj.parent.joinpath('notebooks_main_dev').as_posix())
from .functions import colors, setup_canvas, load_csv, load_output_meta, load_DB_outputs, load_observations, copybak, get_PFT_name, aggPFT, set_iteration_number

try:
    import netCDF4
except ModuleNotFoundError as e:
    print(f"{e}, so `netCDF4` is installing it for you...")
    install('netCDF4')
    import netCDF4


if not root_proj.exists():
    root_proj.mkdir(parents=True, exist_ok=True)
os.chdir(root_proj)
home_dir.joinpath('tccas_r10043/resources').mkdir(exist_ok = True)
home_dir.joinpath('tccas_r10043/analysis').mkdir(exist_ok = True)
