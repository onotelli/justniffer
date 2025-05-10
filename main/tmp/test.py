import sys
import os

def activate_virtualenv(venv_path):
    if os.path.exists(venv_path):
        site_packages = os.path.join(venv_path, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
        print('Found site_packages at %s' % site_packages)
        bin_path = os.path.join(venv_path, 'bin')
        if os.path.exists(site_packages) and site_packages not in sys.path:
            sys.path.insert(0, site_packages)
        if os.path.exists(bin_path):
            os.environ['PATH'] = os.pathsep.join([bin_path, os.environ.get('PATH', '')])
        os.environ['VIRTUAL_ENV'] = venv_path
        os.environ.pop('PYTHONHOME', None)

def find_and_activate_virtualenv():
    
    if 'VIRTUAL_ENV' in os.environ:
        path = os.environ['VIRTUAL_ENV']
        print('Found virtualenv at %s' % path)
        activate_virtualenv(path)
    else:
        print('No virtualenv found')

find_and_activate_virtualenv()
import loguru
print (loguru.__file__)