import subprocess
import ipaddress
from network_devices_list import network_devices
import smtplib
from email.message import EmailMessage
import requests
import datetime
i = 0

#email config
stmp_s = 'smtp.d522.wgu.internal'
port = 1025
sender = 'ITDesk@mailhog.com'
password = ''
receiver = 'Stakeholders@mailhog.com'

#ticket config
token = 'vGkbXkGLqQSo7YLflp9DutuG8st4xdPPF7wnTcwB0FE'
url = 'http://helpdesk.d522.wgu.internal:5000/api/tickets'
headers = {'Authorization': f'Bearer {token}',
           'Content-Type': 'application/json'
           }
payload = {
    "assigned_to": "John Pork",
    "description": "Host is down, get the host up and running at the earliest convenience",
    "priority": "high",
    "requester_email": "ITDesk@mailhog.com",
    "status": "open",
    "title": f"{network_devices[i]['Device Address']} is down!"
}




#pinging ip and auto ticket/email
valid_ip = []
bad_ips = []
for device in network_devices:
    try :
        ipaddress.ip_address(device['Device Address'])
        valid_ip.append(device['Device Address'])
    except ValueError:
        pass
while i < len(valid_ip):
    host = valid_ip[i]
    command = ['ping', '-c', '1', host]
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode == 0:
        print(host, 'Ping Successful')
    else:
        print(valid_ip[i], 'Ping Failed, sending email and creating ticket!')
        Device_name = network_devices[i]['Device_name']
        Timestamp = datetime.datetime.now()
        msg = EmailMessage()
        msg['Subject'] = f'Network Device Unavailable: {Device_name} ({host})'
        msg['From'] = sender
        msg['To'] = receiver
        msg.set_content('Dear Network Administrator,'
                        ''
                        'This is an automated notification that the following network device is currently unavailable:'
                        ''
                        f'Device Name: {Device_name}'
                        f'IP Address: {host}'
                        f'Last Checked: {Timestamp}'
                        ''
                        'Please investigate this issue at your earliest convenience.'
                        ''
                        'Best regards,  '
                        'Network Monitoring System'
                        '')
        try:
            with smtplib.SMTP(stmp_s, port) as s:
                s.login(sender, password)
                s.send_message(msg)
            print("email sent!")
        except Exception as e:
            print(f'ERROR: {e}')

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 201:
            print("Ticket created")
            print(response.json)
            print(f'Status Code: {response.status_code}')
        else:
            print('something went wrong')
            print(f'Status Code: {response.status_code}')
    i = i + 1
