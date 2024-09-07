@echo off
REM Start labrad.bat minimized
start /min cmd.exe /k call C:\scalabrad-0.8.3\bin\labrad.bat

REM Define a list of Python scripts to run
set scripts=(
	serial_server.py 
	gpib_server.py 
	gpib_device_manager.py 
	dac_adc.py 
	sr860.py 
	SR830.py 
	ESP302.py 
	Lakeshore350.py 
	K2400_fromGP.py 
	K2450_fromGP.py 
	data_vault.py 
	dataVaultLivePlotter.py
)

REM Loop through each script and start it minimized with a timeout
for %%s in (%scripts%) do (
    REM Wait for 1 seconds before starting the next script
    TIMEOUT 1 /NOBREAK
    REM Start the Python script minimized
    start /min python C:\Software\afyservers-py3-master\%%s
)

REM Pause the script to keep the command window open
pause
