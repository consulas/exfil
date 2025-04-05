from flask import Flask, request
import os
import ssl
import argparse

# Initialize Flask app
app = Flask(__name__)

# Directory where the uploaded files will be saved
UPLOAD_FOLDER = './temp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['POST'])
def receive_file():
    # Check if a file is part of the request
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    
    # Get the original file name and save it in the temp folder
    if file:
        file_name = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        file.save(file_path)
        return f"File saved at {file_path}", 200
    else:
        return "No file selected", 400


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="File upload server with HTTPS")
    parser.add_argument('--certfile', default='./temp/cert.pem', help="Path to the SSL certificate file.")
    parser.add_argument('--keyfile', default='./temp/key.pem', help="Path to the SSL key file.")
    parser.add_argument('--host', default='0.0.0.0', help="Host to bind the server.")
    parser.add_argument('--port', type=int, default=443, help="Port to bind the server.")
    args = parser.parse_args()

    # Setup SSL context with the provided certificate and key
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=args.certfile, keyfile=args.keyfile)
    
    # Run the app with SSL enabled, using arguments for host and port
    app.run(host=args.host, port=args.port, ssl_context=context)
