@echo off
REM Specify the path to the Python executable
set PYTHON_PATH=C:\Python39\python.exe

REM Start labrad.bat minimized
start cmd.exe /k call C:\scalabrad-0.8.3\bin\labrad.bat

REM Define a list of Python scripts to run
set scripts=serial_server.py gpib_server.py gpib_device_manager.py dac_adc.py sr860.py sr830.py ESP302.py Lakeshore350.py Keithley_2400.py Keithley_2450.py data_vault.py dataVaultLivePlotter.py

REM Loop through each script and start it minimized with a timeout
for %%s in (%scripts%) do (
    REM Wait for 1 seconds before starting the next script
    TIMEOUT 1 /NOBREAK
    REM Start the Python script minimized
    start %PYTHON_PATH% C:\Software\afyservers-py3-master\%%s
)

REM Pause the script to keep the command window open
pause