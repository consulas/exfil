# Create a COM object to interact with the system's input/output
$wshell = New-Object -ComObject wscript.shell;

# Activate the VS Code window by its title
$wshell.AppActivate('Visual Studio Code')

# Wait for 5 seconds
# Use this time to click into the hex file
Start-Sleep -Seconds 5

# Infinite loop to send Page Down keystroke every 1/10
while ($true) {
    # Sleep for 100ms
    Start-Sleep -Milliseconds 250

    # Send the Page Down keystroke
    $wshell.SendKeys('{PGDN}')
}
