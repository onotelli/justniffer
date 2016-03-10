'''
Created on Mar 8, 2016

@author: oreste
'''
from argh import ArghParser
from pudb import set_trace as debugger  # @UnusedImport
from inspect import isfunction
from pystache.renderer import Renderer
from functools import lru_cache
from os.path import abspath, curdir, join
from datetime import datetime
from json import load
from pytz import timezone

class Configurator():
    
    def __init__(self, template_name):
        self.__template_name = template_name
    
    def _template_name(self):
        return self.__template_name
    
    def _info(self):
        info_file = join(self._search_dir(),"info.json")
        with open(info_file) as f:
            info_obj = load(f)
        date_dict = info_obj["date"]
        tzinfo = timezone("Europe/Rome")
        d = datetime(tzinfo=tzinfo,**date_dict)
        date_dict["week_day"] = d.strftime("%a")
        date_dict["time"] = d.strftime("%H:%M:%S")
        date_dict["offset"] = d.strftime("%z")
        date_dict["month_name"] = d.strftime("%B")
        return info_obj
    
    def _search_dir(self):
        dirpath = abspath(curdir)
        return dirpath
    
    @lru_cache()
    def _renderer(self):
        return Renderer(file_extension="in",search_dirs = [self._search_dir()] )
        
    def configure(self):
        tmpl = self._template_name()
        ctx = self._info()
        renderer = self._renderer()
        res = renderer.render_name(tmpl,  ctx)
        fullpath = join(self._search_dir(), tmpl)
        with open (fullpath, "w") as f:
            f.write(res)
        #print (res)

def configure():
    files = "justniffer.8", "configure.ac", "debian/changelog"
    for filename in files:
        c = Configurator(filename)
        c.configure()

def __main__():
    parser  = ArghParser()
    parser.add_commands(sorted([v  for k, v in globals().items() if not k.startswith("_") and not k == "main" and isfunction(v) and v.__module__ == "__main__"], key=lambda a:a.__name__))
    parser.dispatch()
    
if __name__ == "__main__":
    __main__()