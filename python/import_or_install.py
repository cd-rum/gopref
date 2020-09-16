import pip

if int(pip.__version__.split('.')[0]) > 9:
  from pip._internal import main
else:
  from pip import main

def import_or_install(package):
  try:
    __import__(package)
  except ImportError:
    main(['install', package])
