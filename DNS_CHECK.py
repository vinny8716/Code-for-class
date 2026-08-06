import subprocess
from email.message import EmailMessage
import datetime
from network_devices_list import network_devices
import paramiko
import requests
import smtplib
i = 0
#config
ip_list = ['10.10.10.200', '10.10.10.210', '10.10.10.10', '10.10.10.20', '192.168.10.102', '192.168.20.102', '192.168.30.101', '192.168.10.101', '10.10.10.1', '10.10.10.100', '192.168.20.210', '192.168.30.210']
device_name = network_devices[i]['Device Name']
cmd = 'cat /etc/resolv.conf'
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
epassword = ''
receiver = 'Stakeholders@mailhog.com'
Timestamp = datetime.datetime.now()
msg = EmailMessage()
msg['Subject'] = f'DNS Configuration Alert: {network_devices[i]['Device Name']} {ip_list[i]})'
msg['From'] = sender
msg['To'] = receiver

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
    "title": f"{network_devices[i]['Device Name']} is down!"
    }


while i < len(network_devices):
    try:
        client.connect(hostname = ip_list[i], username = username, password = password, timeout = 10)
        stdin, stdout, stderr = client.exec_command(cmd)
        temp_readout = stdout.read().decode()
        if '203.0.113.10' in temp_readout:
            bad_DNS.append(network_devices[i]['Device Address'])
            print(f'{ip_list[i]} DNS settings are wrong, email sent!')
            msg.set_content('Dear Network Administrator,\n'
                '\n'
                'This is an automated alert that the DNS configuration for the following device has been altered from the expected settings:\n'
                '\n'
                f'Device Name: {network_devices[i]['Device Name']}\n'
                f'IP Address: {ip_list[i]}\n'
                'Detected DNS Setting:\n'
                f'{temp_readout}\n'
                'Expected DNS Setting: 10.10.10.10 or 10.10.10.20 or loopback address\n'
                f'Time Detected: {Timestamp}\n'
                '\n'
                'The system will attempt to automatically correct this configuration.\n'
                '\n'
                'Best regards,\n'
                'Network Monitoring System\n')

            try:
                with smtplib.SMTP(stmp_s, port) as s:
                    s.login(sender, epassword)
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
            print(f'{ip_list[i]} is all good!')
    except Exception as e:
        print(f'Connection failed to {network_devices[i]['Device Name']}: {e}')
    finally:
        client.close()
    i = i + 1
