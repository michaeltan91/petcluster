from setuptools import setup, find_packages

setup(name='petcluster',
      version='1.0',
      description='TU Delft ESS E&I, Petrochemical cluster of Port of Rotterdam',
      author='Michael Tan',
      license='BSD 3-Clause License',
      packages=find_packages(),
      install_requires = [
          'xlrd',
          'pyexcel',
          'pandas',
          'numpy',
          'epynet',
          'plotly',
          'py3plex @ git+https://github.com/michaeltan91/py3plex@testing',
          'aspenauto @ git+https://github.com/michaeltan91/aspenauto@a554828'
      ],
      zip_safe=False)
