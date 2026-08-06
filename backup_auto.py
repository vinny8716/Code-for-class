import paramiko
import subprocess
from pathlib import Path
from contextlib import redirect_stdout
i = 0

#ssh config
hostname = ['10.10.10.10', '10.10.10.20']
username = 'ubuntu'
password = 'ubuntu'
command = 'cat /etc/bind/named.conf.options'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
folders = ['Server-1', 'Server-2']
target_dir = Path(f"/home/Student/Desktop/DNS-backup/{folders[i]}")
file = 'record-config.txt'
file_path = target_dir / file

while i < len(hostname):
    try:
        print(f'Connecting to {hostname}...')
        ssh.connect(hostname = hostname[i], username = username, password = password)

        stdin, stdout, stderr = ssh.exec_command(command)

        print('\n--- Command Output ---')
        print(stdout.read().decode())
        error_output = stderr.read().decode()
        with open(file_path, 'w') as f:
            with redirect_stdout(f):
                f.write(stdout.read().decode())
        if error_output:
            print(f'Error: {error_output}')

    finally:
        ssh.close()
        print('connection closed')

    i = i + 1
