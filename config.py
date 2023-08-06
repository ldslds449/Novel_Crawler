import yaml
import ttkbootstrap as ttk
from os import path, makedirs
from platformdirs import user_data_dir

from info import *

config_folder = user_data_dir(appname.replace(' ', '_'), appauthor)
config_filename = path.join(config_folder, 'setting.yaml')

def read_config(url:ttk.StringVar, saveFolder:ttk.StringVar):
  if path.exists(config_filename):
    with open(config_filename, 'r') as fp:
      config = yaml.safe_load(fp)
      url.set(config['url'])
      saveFolder.set(config['saveFolder'])
      return config

def write_config(url:ttk.StringVar, saveFolder:ttk.StringVar):
  if not path.exists(config_folder):
    makedirs(config_folder)
  with open(config_filename, 'w') as fp:
    yaml.dump({
      'url': url.get(),
      'saveFolder': saveFolder.get()
    }, fp)
