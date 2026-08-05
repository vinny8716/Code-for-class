import subprocess
from email.message import EmailMessage
import datetime
from network_devices_list import network_devices
import paramiko
import requests
i = 0
#config
ip_list = network_devices[i]['Device Address']
device_name = network_devices[i]['Device Name']
cmd = ['cat /etc/resolv.conf']
username = 'ubuntu'
password = 'ubuntu'
temp_readout = ''
bad_DNS = []
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#email config
stmp_s = 'smtp.d522.wgu.internal'
port = 1025
sender = 'ITDesk@mailhog.com'
password = ''
receiver = 'Stakeholders@mailhog.com'
Timestamp = datetime.datetime.now()
msg = EmailMessage()
msg['Subject'] = f'DNS Configuration Alert: {device_name} {ip_list})'
msg['From'] = sender
msg['To'] = receiver
msg.set_content('Dear Network Administrator,\n'
                '\n'
                'This is an automated alert that the DNS configuration for the following device has been altered from the expected settings:\n'
                '\n'
                f'Device Name: {device_name}\n'
                f'IP Address: {ip_list}\n'
                'Detected DNS Setting:\n'
                f'{temp_readout}\n'
                'Expected DNS Setting: 10.10.10.10 or 10.10.10.20 or loopback address\n'
                f'Time Detected: {Timestamp}\n'
                '\n'
                'The system will attempt to automatically correct this configuration.\n'
                '\n'
                'Best regards,\n'
                'Network Monitoring System\n')

#ticket config
token = 'vGkbXkGLqQSo7YLflp9DutuG8st4xdPPF7wnTcwB0FE'
url = 'http://helpdesk.d522.wgu.internal:5000/api/tickets'
headers = {'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
            }
payload = {
    "assigned_to": "John Pork",
    "description": "DNS settings changed!",
    "priority": "high",
    "requester_email": "ITDesk@mailhog.com",
    "status": "closed",
    "title": f"{device_name[i]} is down!"
    }


while i < len(network_devices):
    try:
        client.connect(hostname = ip_list, username = username, password = password, timeout = 10)
        stdin, stdout, stderr = client.exec_command(cmd)
        temp_readout = stdout.read().decode()
        if '203.0.113.10' in temp_readout:
            bad_DNS.append(ip_list[i])
            print(f'{ip_list} DNS settings are wrong, email sent!')
            try:
                with smtplib.SMTP(stmp_s, port) as s:
                    s.login(sender, password)
                    s.send_message(msg)
                print("email sent!")
            except Exception as e:
                print(f'ERROR: {e}')
            command = ("sudo sed -i 's/^#\\?DNS=.*/DNS=10.10.10.10 10.10.10.20/' /etc/systemd/resolved.conf && "
                        "sudo systemctl restart systemd-resolved && "
                        "resolvectl status")

            stdin, stdout, stderr = client.exec_command(command)
            print('DNS settings changed! Status:')
            print(stdout.read().decode())
            print(stderr.read().decode())
            response = requests.post(url, headers=headers, json=payload)
        else:
            print(f'{ip_list} is all good!')
    except Exception as e:
        print(f'Connection failed to {device_name}: {e}')
    finally:
        client.close()
    i = i + 1
