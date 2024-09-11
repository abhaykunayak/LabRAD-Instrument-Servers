@echo off
REM Specify the path to the Python executable
set PYTHON_PATH=C:\Python39\python.exe

REM Specify the directory containing the Python scripts
set SCRIPT_DIR=C:\Users\Marconi\Young Lab Dropbox\Young Group\THz\Scripts\LabRAD-Instrument-Servers

REM Specify the timeout duration (in seconds)
set TIMEOUT_DURATION=1

REM Log file path
set LOG_FILE=%SCRIPT_DIR%\script_log.txt

REM Start labrad.bat minimized
start /min cmd.exe /k call C:\scalabrad-0.8.3\bin\labrad.bat

REM Define a list of Python scripts to run
set scripts=serial_server.py gpib_server.py gpib_device_manager.py dac_adc.py sr860.py sr830.py ESP302.py Lakeshore350.py Keithley_2400.py Keithley_2450.py data_vault.py dataVaultLivePlotter.py

REM Create or clear the log file
echo Script Execution Log > %LOG_FILE%
echo ==================== >> %LOG_FILE%

REM Loop through each script and start it minimized with a timeout
for %%s in (%scripts%) do (
    REM Check if the script exists
    if exist "%SCRIPT_DIR%\%%s" (
        REM Log the start time
        echo Starting %%s at %time% >> %LOG_FILE%
        
        REM Wait for the specified timeout duration before starting the next script
        TIMEOUT %TIMEOUT_DURATION% /NOBREAK
        
        REM Start the Python script minimized
        start /min %PYTHON_PATH% "%SCRIPT_DIR%\%%s"
        
        REM Log the end time
        echo Started %%s at %time% >> %LOG_FILE%
    ) else (
        REM Log the error
        echo ERROR: Script %%s not found at %time% >> %LOG_FILE%
    )
)

REM Pause the script to keep the command window open
pause
