""" 
Nelvin: Using this file to collect pydantic submodules
Otherwise PyInstaller will not include them during build
"""
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules
hiddenimports = collect_submodules('pydantic')

# Add specific problematic imports
hiddenimports.extend([
    'pydantic.deprecated',
    'pydantic.deprecated.decorator',
    'pydantic.deprecated.decorator',
    'pydantic.validators',
    'pydantic.version',
    'pydantic.fields',
    'pydantic.main',
    'pydantic.error_wrappers',
    'pydantic.errors',
    'pydantic.schema',
    'pydantic.types',
    'pydantic.utils',
    'pydantic.color'
])

# Collect all data files
datas = collect_data_files('pydantic') 