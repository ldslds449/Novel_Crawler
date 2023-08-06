from ttkbootstrap import Style
from app import App

style = Style('darkly')

root = style.master
myapp = App(root)
myapp.mainloop()