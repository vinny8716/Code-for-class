import paramiko
import subprocess
i = 0

#ssh config
hostname = ['10.10.10.10', '10.10.10.20']
username = 'ubuntu'
password = 'ubuntu'
command = 'cat /etc/bind/named.conf.options'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
temp_output = ''
folders = ['Server-1', 'Server-2']
cmd = f'echo {temp_output} > /home/student/Desktop/DNS-Backup/{folders[i]}'

while i < len(hostname):
    try:
        print(f'Connecting to {hostname}...')
        ssh.connect(hostname = hostname, username = username, password = password)

        stdin, stdout, stderr = ssh.exec_command(command)

        print('\n--- Command Output ---')
        print(stdout.read().decode())
        temp_output = stdout.read().decode()
        error_output = stderr.read().decode()
        if error_output:
            print(f'Error: {error_output}')

    finally:
        ssh.close()
        print('connection closed')
    subprocess.run(cmd)
    i = i + 1