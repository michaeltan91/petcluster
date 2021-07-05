#

# Process
```python
from petcluster import Process
# Initialize the Process Class and load an Aspen Plus backup file
M1 = Process()
M1.process_data('M1 Methanol.bkp')
# Report the detailed mass and energy balances of the process to Excel
M1.report('process_data.xlsx')

# Add manual steam generation utility to the process
M1.add_manual_steam_gen('MPS-GEN', 'M1-R02', 'HS-2', 'S-MPS')
# MPS-GEN is the steam type
# M1-R02 is the block the utility will be assigned to
# HS-2 is the heat stream name
# S-MPS is the name of the steam utility stream

# Add manual natural gas utility to the process
M1.add_manual_natural_gas('M1-FU01','FS-CH4-2')
# M1-FU01 is the name of the block the utility will be assigned to
# FS-CH4-2 is the name of the natural gas stream flowing to M1-FU01

# Close the Aspen Plus model
M1.close_aspen()
```

# Petrochemical cluster
```python
from petcluster import Cluster
PoR = Cluster()

# Generate static table from all aspen plus backup files in the current directory
# Static table is a Pandas DataFrame 
PoR.create_static_table()
# View the static table
PoR.table
# Export the static table to Excel 
PoR.table.export_to_excel('cluster.xlsx', index = False)
# Load previously exported table back in Python
PoR.load_static_table('cluster.xlsx')
# Add a process to the current static table
PoR.add_process_static_table('M4 DME.bkp')

# Load the complete mass and energy balances from all aspen plus backup files in the current directory
PoR.load_cluster()
```



