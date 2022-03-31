from setuptools import setup

setup(name='petcluster',
      version='1.0',
      description='TU Delft ESS E&I, Petrochemical cluster of Port of Rotterdam',
      author='Michael Tan',
      license='Apache Licence 2.0',
      packages=['petcluster'],
      install_requires = [
          'xlrd',
          'pyexcel',
          'pandas',
          'numpy',
          'epynet'
      ],
      zip_safe=False)
