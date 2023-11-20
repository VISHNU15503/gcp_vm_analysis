import os
import subprocess
import time

from googleapiclient.discovery import build

project_id = '<your_project_id>'
zone = 'us-east1-b'
instance_name = 'cc-testing-1'
debian_image = 'projects/debian-cloud/global/images/debian-11-bullseye-v20231010'

vm_config = {
    'name': instance_name,
    'zone': zone,
    # Whatever instance type we want to measure processing time for
    'machine_type': 'e2-medium',
    'vm_image': debian_image,
}

def create_instance(vm_name, zone,machine_type, vm_image):
    compute_service = build('compute', 'v1')
    subnet_selflink = 'projects/<your_project_id>/regions/us-east1/subnetworks/default'
    config = {
        'name': vm_name,
        'machineType': f'projects/<your_project_id>/zones/us-east1-b/machineTypes/{machine_type}',
        'disks': [{
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': vm_image
                }
            }],
        'networkInterfaces': [{
                'subnetwork': subnet_selflink,
                'accessConfigs': [{
                    'type': 'ONE_TO_ONE_NAT',
                    'name': 'External NAT'
                }]
            }],
            # Add a startup script to the instance ('script.sh')
        'metadata': {
            'items': [{
                'key': 'startup-script',
                'value': open('script.sh', 'r').read()
            }]
        }
    }
    request = compute_service.instances().insert(
    project=project_id, zone=zone, body=config)
    response = request.execute()
    print('VM instance created')

# Get ip address of the VM instance
def get_instance_ip(vm_name, zone):
    compute_service = build('compute', 'v1')
    request = compute_service.instances().get(project=project_id, zone=zone, instance=vm_name)
    response = request.execute()
    return response['networkInterfaces'][0]['accessConfigs'][0]['natIP']

# Function to stop the VM instance
def stop_instance(vm_name, zone):
    compute_service = build('compute', 'v1')
    request = compute_service.instances().stop(project=project_id, zone=zone, instance=vm_name)
    response = request.execute()

# Function to start the VM instance
def start_instance(vm_name, zone):
    compute_service = build('compute', 'v1')
    request = compute_service.instances().start(project=project_id, zone=zone, instance=vm_name)
    response = request.execute()

# Write a function to delete the VM instance
def delete_instance(vm_name, zone):
    compute_service = build('compute', 'v1')
    request = compute_service.instances().delete(project=project_id, zone=zone, instance=vm_name)
    response = request.execute()


# Get the status of the VM instance
def get_instance_status(vm_name, zone):
    compute_service = build('compute', 'v1')
    request = compute_service.instances().get(project=project_id, zone=zone, instance=vm_name)
    response = request.execute()
    return response['status']

# Wait until vm status is RUNNING
def wait_until_running(vm_name, zone):
    while True:
        get_instance_status(vm_name, zone)
        if get_instance_status(vm_name, zone) == 'RUNNING':
            break
        time.sleep(1)



req_time = time.time()
create_instance(vm_config['name'], vm_config['zone'], vm_config['machine_type'], vm_config['vm_image'])
wait_until_running(vm_config['name'], vm_config['zone'])
ip = get_instance_ip(vm_config['name'], vm_config['zone'])
print(ip)




# Code to post the request to the VM instance using bash

bash_command = "curl -X POST -H \"Content-Type: application/json\" -d '{\"data\":[5.1, 3.5, 1.4, 0.2]}' http://"+ip+":5000/predict"

out = ""
while(out==""):
    # Execute the command until it succeeds
    # Do not print anything if not connected
    time.sleep(5)
    process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    out = output.decode('utf-8')
    

# Get the output and error (if any)


print(output.decode('utf-8'))
res_time = time.time()
print("Cold response time: ", res_time - req_time)
print()
print()


# Stop the VM instance
print("Stopping the VM instance\n\n")
stop_instance(vm_config['name'], vm_config['zone'])
time.sleep(90)

# Start the VM instance
print("Starting the VM instance")
req_time2 = time.time()
start_instance(vm_config['name'], vm_config['zone'])
wait_until_running(vm_config['name'], vm_config['zone'])
print("VM instance running")
ip = get_instance_ip(vm_config['name'], vm_config['zone'])
print(ip)
bash_command = "curl -X POST -H \"Content-Type: application/json\" -d '{\"data\":[5.1, 3.5, 1.4, 0.2]}' http://"+ip+":5000/predict"
out = ""
while(out==""):
    # Execute the command until it succeeds
    # Do not print anything if not connected
    time.sleep(5)
    process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    out = output.decode('utf-8')

print(output.decode('utf-8'))
res_time2 = time.time()
print("Warm response time: ", res_time2 - req_time2)

print()
print()
# Wait for 30 sec
time.sleep(30)

req_time3 = time.time()
process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, error = process.communicate()
print(output.decode('utf-8'))
res_time3 = time.time()
print("Running response time: ", res_time3 - req_time3)

# Delete the VM instance
print("\n\nDeleting the VM instance")
delete_instance(vm_config['name'], vm_config['zone'])
