#package_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
#add_to_all(0, package_folder)

#sdwis_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"SDWIS")))
#add_to_all(0, sdwis_folder)

#def add_to_all(directory):
#    for module in os.listdir(os.path.dirname(directory)):
#        if module == '__init__.py' or module[-3:] != '.py':
#            continue
#        __all__.append(module[:-3])

__all__ = ["Violation"]