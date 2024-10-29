import csv
import numpy as np
import sys

reportcols=["CPU_ALL2", "CPU_TREE2", "CPU_PM_GRAVITY2"]
step=-1

cpufile=sys.argv[1]
if len(sys.argv) >= 3:
    step=int(sys.argv[2])
if len(sys.argv) >= 4:
    reportcols=sys.argv[3].split(',')

cpudata={}
with open(cpufile, mode='r') as file: 
    # Create a CSV reader object 
    csv_reader = csv.reader(file)

    # Read the header
    cols = next(csv_reader, None)
    for i in range(len(cols)):
        cols[i] = cols[i].strip()
    cols.remove("MULTIPLEDOMAIN") # this column is missing in Gadget-4 cpu.csv rows
    colnum=0
    for col in cols:
        cpudata[col]=[]

    numcols = len(cols)

    # Iterate over each row in the CSV file 
    for row in csv_reader:
        colnum=0
        for celldata in row:
            col = cols[colnum]
            cpudata[col].append(celldata)
            colnum += 1
    colnum=0
    for col in cols:
        cpudata[col]=np.asarray(cpudata[col])
        colnum += 1
nsteps=len(cpudata[cols[0]])
stepstring="at step"
if step < 0:
    step=nsteps-1

colnum=0
print(f"{step}",end='')
for col in reportcols:
    dt_sec=cpudata[col][step]
    print(f"{dt_sec} ",end='')


