from network_devices_list import network_devices
import datetime
import paramiko

Timestamp = datetime.datetime.now()
for device in network_devices:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(f'{device['Device Address']}', username='ubuntu', password='ubuntu')

        stdin, stout, stderr = ssh.exec_command('systemctl is-active resolvectl')

        status = stdout.read().decode('utf-8').strip()
        if status == 'active':
            with open(log_file.txt, 'a') as f:
                f.write(f'{device["Device Name"]}' + 'DNS service is functioning correctly' + f'{Timestamp}' + '\n')
        else:
            print(f'{device["Device Name"]} DNS service is down!')
    except Exception as e:
        print(f'Connection failed: {e}')
    finally:
        ssh.close()
