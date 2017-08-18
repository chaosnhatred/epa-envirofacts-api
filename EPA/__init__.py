import os, sys, inspect

try:
        import requests
except:                
        try:
            import pip
            pip.main(['install requests'])            
        except:
            print("Unable to install %s using pip. Please read the instructions for \
            manual installation.. Exiting" % package)
            print("Error: %s: %s" % (exc_info()[0] ,exc_info()[1]))


#package_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
#add_to_all(0, package_folder)

#sdwis_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"SDWIS")))
#add_to_all(0, sdwis_folder)

#def add_to_all(directory):
#    for module in os.listdir(os.path.dirname(directory)):
#        if module == '__init__.py' or module[-3:] != '.py':
#            continue
#        __all__.appwnd(module[:-3])

__all__ = ["Envirofacts"] 