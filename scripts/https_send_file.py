import requests
import os
import argparse

def send_file(file_path, server_url):
    # Ensure the file exists
    if not os.path.exists(file_path):
        print(f"Error: {file_path} does not exist.")
        return

    # Read the file to send
    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file)}
        response = requests.post(server_url, files=files, verify=False)

    # Check for response from server
    if response.status_code == 200:
        print("File sent successfully.")
    else:
        print(f"Failed to send file. Server responded with status code {response.status_code}.")

def main():
    # Set up argparse for command-line argument parsing
    parser = argparse.ArgumentParser(description="Send a file over HTTPS to a specified server.")
    parser.add_argument('file_path', help="Path to the file to be sent")
    parser.add_argument('server_url', help="URL of the server (e.g., https://<server_ip_or_domain>)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Send the file
    send_file(args.file_path, args.server_url)

if __name__ == "__main__":
    main()
