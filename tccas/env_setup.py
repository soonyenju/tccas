import os, sys, shutil, warnings
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import pyplot as plt
from pathlib import Path
from google.colab import drive

warnings.simplefilter('ignore')

drive.mount('/content/drive', force_remount = False)
# root = Path.cwd().joinpath('drive/My Drive')
home_dir = Path('/content')
# home_dir = [p for p in Path('/home').glob('*') if p.stem != 'conda'][0]
root_proj = home_dir.joinpath('tccas_r10043')
sys.path.append(root_proj.parent.joinpath('notebooks').as_posix())
sys.path.append(root_proj.parent.joinpath('notebooks_main_dev').as_posix())
from .functions import colors, setup_canvas, load_csv, load_output_meta, load_DB_outputs, load_observations, copybak, get_PFT_name, aggPFT, set_iteration_number

os.chdir(root_proj)
home_dir.joinpath('tccas_r10043/resources').mkdir(exist_ok = True)
home_dir