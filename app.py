import tkinter as tk
import ttkbootstrap as ttk
import re
from tkinter.filedialog import askdirectory
from ttkbootstrap.dialogs import Messagebox
from threading import Thread
from pathvalidate import is_valid_filepath, validate_filename

from crawler import Crawler
from config import read_config, write_config
from info import *
from mode import *

class App(ttk.Frame):
  def __init__(self, master:tk.Tk):
    super().__init__(master)
    master.title(f'{appname} {version}')
    screen_width = master.winfo_screenwidth()
    screen_height = master.winfo_screenheight()
    master.geometry(f'+{int(0.3*screen_width)}+{int(0.35*screen_height)}')
    master.columnconfigure(0, weight=1)
    self.master = master
    self.grid(row=0, column=0, padx=(30, 30), sticky=ttk.E+ttk.W)
    self.columnconfigure(1, weight=1)
    self.columnconfigure(2, weight=1, minsize=300)

    s = ttk.Style()
    label_font = ('Microsoft YaHei', 12)
    s.configure('my.TButton', font=label_font)

    ttk.Label(self, text="網址 (URL)", font=label_font)\
      .grid(row=0, column=0, pady=(15,5), padx=(0,5))
    self.url = ttk.StringVar(self)
    self.url_entry = ttk.Entry(self, textvariable=self.url, bootstyle='primary', validate='focusout',
              validatecommand=(self.register(self.validate_url), '%P'), 
              invalidcommand=(self.register(self.show_error), 'URL'))
    self.url_entry.grid(row=0, column=1, columnspan=3, pady=(15,5), padx=(5,0), sticky=ttk.E+ttk.W)

    ttk.Label(self, text="存放路徑 (Save Folder)", font=label_font) \
      .grid(row=1, column=0, pady=(5,5), padx=(0,5))
    self.saveFolder = ttk.StringVar(self)
    self.saveFolder_entry = ttk.Entry(self, textvariable=self.saveFolder, bootstyle='primary', validate='focusout',
              validatecommand=(self.register(self.validate_folder), '%P'), 
              invalidcommand=(self.register(self.show_error), 'Save Folder'))
    self.saveFolder_entry.grid(row=1, column=1, columnspan=2, pady=(5,5), padx=(5,5), sticky=ttk.E+ttk.W)
    ttk.Button(self, text="瀏覽", command=self.get_directory, style='my.TButton') \
      .grid(row=1, column=3, pady=(5,5), padx=(5,0))

    ttk.Label(self, text="儲存檔名 (FileName)", font=label_font) \
      .grid(row=2, column=0, pady=(5,5), padx=(0,5))
    self.fileNameMode = ttk.StringVar(self, value=FileNameMode.AUTO)
    self.fileNameFrame = ttk.Frame(self)
    self.fileNameFrame.grid(row=2, column=1, pady=(5,5), padx=(5,5), sticky=ttk.E+ttk.W)
    tk.Radiobutton(self.fileNameFrame, text='自動', var=self.fileNameMode, value=FileNameMode.AUTO, font=label_font,
                   command=self.fileName_radio_event) \
      .pack(side=ttk.LEFT, padx=(0,5))
    tk.Radiobutton(self.fileNameFrame, text='自訂', var=self.fileNameMode, value=FileNameMode.CUSTOM, font=label_font,
                   command=self.fileName_radio_event) \
      .pack(side=ttk.LEFT, padx=(5,0))
    self.fileName = ttk.StringVar(self)
    self.fileName_entry = ttk.Entry(self, textvariable=self.fileName, bootstyle='primary', validate='focusout',
              validatecommand=(self.register(self.validate_fileName), '%P'), 
              invalidcommand=(self.register(self.show_error), 'FileName'))
    self.fileName_entry.grid(row=2, column=2, columnspan=2, pady=(5,5), padx=(5,5), sticky=ttk.E+ttk.W)

    self.progbar = ttk.Progressbar(self, bootstyle='warning')
    self.progbar.grid(row=3, column=0, columnspan=4, pady=(15,5), sticky=ttk.E+ttk.W)

    self.progressMsg = ttk.StringVar(self)
    self.progressMsg_label = ttk.Label(self, textvariable=self.progressMsg, font=label_font)
    self.progressMsg_label.grid(row=4, column=0, columnspan=3, pady=(5,15), padx=(0,5))

    self.btn = ttk.Button(self, text="Crawl It!", command=self.run_crawl, style='my.TButton')
    self.btn.grid(row=5, column=0, columnspan=4, pady=(0,15), sticky=ttk.E+ttk.W)

    read_config(self.url, self.saveFolder, self.fileNameMode, self.fileName)
    self.fileName_radio_event()

    master.protocol("WM_DELETE_WINDOW", self.save_setting)

    self.running = False

  def get_directory(self):
    self.update_idletasks()
    d = askdirectory()
    if d:
      self.saveFolder.set(d)

  def run_crawl(self):
    if not self.url_entry.validate() or not self.saveFolder_entry.validate():
      return

    self.running = True
    self.btn['state'] = ttk.DISABLED
    self.progressMsg_label.configure(bootstyle='default')

    def task():
      try:
        self.progbar.configure(maximum=3)
        self.progressMsg.set('Fetch URL...')
        crawler = Crawler(self.url.get(), self.saveFolder.get())
        crawler.fetch()
        self.progbar.step(1)
        self.progressMsg.set('Get Book Title...')
        info = crawler.get_book_info()
        print(info)
        self.progbar.step(1)
        self.progressMsg.set('Find All Chapters...')
        ch_len = len(crawler.get_chapter_list())
        self.progbar.step(1)

        self.progbar.configure(maximum=ch_len)
        fileName = None if self.fileNameMode.get() == FileNameMode.AUTO else self.fileName.get()
        for i, msg in enumerate(crawler.crawl(fileName)):
          msg = f'{i}/{ch_len} - {msg}'
          print(msg)
          self.progressMsg.set(msg)
          self.progbar.step(1)
        
        self.progressMsg.set(f'Finish downloading {info["title"]} >_<')
        self.master.after(0, lambda : Messagebox.ok(title='Information', message=f'Finish downloading {info["title"]}'))
      except Exception as e:
        print(e)
        error = str(e)
        self.progressMsg_label.configure(bootstyle='danger')
        self.progressMsg.set(f'Downloading failed QAQ')
        self.master.after(0, lambda : Messagebox.show_error(title='Unexcepted Error', message=error, parent=self))
      finally:
        self.btn['state'] = ttk.NORMAL
        self.running = False

    self.thread = Thread(target=task, daemon=True)
    self.thread.start()

  def save_setting(self):
    if self.running:
      if not Messagebox.okcancel(title='Exit', message='Do you want to exit?', parent=self.master):
        return
    write_config(self.url, self.saveFolder, self.fileNameMode, self.fileName)
    self.master.destroy()

  def validate_url(self, value):
    return re.match(r"https:\/\/czbooks\.net\/n\/\w+$", value) is not None

  def validate_folder(self, value):
    return value == '' or is_valid_filepath(value)
  
  def validate_fileName(self, value):
    return value != '' and validate_filename(value)
  
  def show_error(self, text):
    if hasattr(self, 'progressMsg'):
      self.progressMsg.set(f'{text} is invalid.')
      self.progressMsg_label.configure(bootstyle='danger')

  def fileName_radio_event(self):
    if self.fileNameMode.get() == str(FileNameMode.AUTO):
      self.fileName_entry.configure(state=ttk.DISABLED, bootstyle='readonly')
    else:
      self.fileName_entry.configure(state=ttk.NORMAL, bootstyle='primary')
  