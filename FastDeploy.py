import paramiko
import os

def ssh_execute_and_fetch_file(ip, command, ssh_key_path, local_save_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the remote server using the SSH key
    client.connect(ip, username="root", key_filename=ssh_key_path)

    # Execute the command and store the output
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()

    # Save the command output to a local file
    with open(os.path.join(local_save_path, f"{ip}_output.txt"), "w") as f:
        f.write(output)
        if error:
            f.write("\nERRORS:\n")
            f.write(error)

    # Fetch the client.json file
    sftp = client.open_sftp()
    remote_file_path = '/FastReality/client.json'
    sftp.get(remote_file_path, os.path.join(local_save_path, f"{ip}.json"))
    
    sftp.close()
    client.close()

if __name__ == "__main__":
    
    IPs = ["1.1.1.1", "1.2.3.4"] 
    
    command = "sudo curl -s https://raw.githubusercontent.com/taesiri/FastReality/master/Reality.sh | bash"
    ssh_key_path = "~/.ssh/id_rsa"  # Replace with your ssh key path
    local_save_path = "./"  # Replace with desired local save path

    for ip in IPs:
        ssh_execute_and_fetch_file(ip, command, ssh_key_path, local_save_path)
