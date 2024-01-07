import numpy
import pandas as pd
ports = []
file = open('./text_test.txt', 'r')
data = file.readlines()
for line in data:
    if line.startswith('port'):
        if len(line.split()) > 5:
            print(line.split())
            ports.append(line.split())
print(ports)
# Works well---------------------------------
# file.readline()
# data = file.read()
# file.close()
# stripped = data.strip()
#
# for line in data.splitlines():
#     print(line.split())
# --------------------------------------------

# data = pd.read_csv('./text_test.txt', names=['Port', 'Name', 'Status', 'Vlan', 'Duplex', 'Speed', 'Type'], dtype=str)

# print(data.head())
# print(data.info())