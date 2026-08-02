import csv
with open('network_devices.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    network_devices = []
    for row in reader:
        network_devices.append(row)
    for device in network_devices:
        print(device)