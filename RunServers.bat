@echo off
REM Start labrad.bat
start cmd.exe /k call C:\scalabrad-0.8.3\bin\labrad.bat

REM Define a list of Python scripts to run
set scripts=serial_server.py dac_adc.py gpib_server.py gpib_device_manager.py ESP300.py sr860.py SR830.py data_vault.py Lakeshore350.py K2400_fromGP.py K2450_fromGP.py dataVaultLivePlotter.py

REM Loop through each script and start it with a timeout
for %%s in (%scripts%) do (
    REM Wait for 2 seconds before starting the next script
    TIMEOUT 2 /NOBREAK
    REM Start the Python script
    start python C:\Software\afyservers-py3-master\%%s
)

REM Pause the script to keep the command window open
pause
