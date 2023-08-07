import yaml
import ttkbootstrap as ttk
from os import path, makedirs
from platformdirs import user_data_dir

from info import *

config_folder = user_data_dir(appname.replace(' ', '_'), appauthor)
config_filename = path.join(config_folder, 'setting.yaml')

def read_config(url:ttk.StringVar, saveFolder:ttk.StringVar, fileNameMode:ttk.StringVar, fileName:ttk.StringVar):
  if path.exists(config_filename):
    with open(config_filename, 'r') as fp:
      config = yaml.safe_load(fp)
      if 'url' in config: url.set(config['url'])
      if 'saveFolder' in config: saveFolder.set(config['saveFolder'])
      if 'fileNameMode' in config: fileNameMode.set(config['fileNameMode'])
      if 'fileName' in config: fileName.set(config['fileName'])
      return config

def write_config(url:ttk.StringVar, saveFolder:ttk.StringVar, fileNameMode:ttk.StringVar, fileName:ttk.StringVar):
  if not path.exists(config_folder):
    makedirs(config_folder)
  with open(config_filename, 'w') as fp:
    yaml.dump({
      'url': url.get(),
      'saveFolder': saveFolder.get(),
      'fileNameMode': fileNameMode.get(),
      'fileName': fileName.get()
    }, fp)
