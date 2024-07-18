
@echo off
echo Disconnecting old connections...
adb disconnect

echo Setting up connected device...
adb tcpip 5555

echo Waiting for device to initialize...
timeout /t 3 /nobreak >nul

echo Retrieving device IP address...
FOR /F "tokens=2" %%G IN ('adb shell ip addr show wlan0 ^| findstr "inet "') DO set ipfull=%%G
FOR /F "tokens=1 delims=/" %%G in ("%ipfull%") DO set ip=%%G

echo Connecting to device with IP %ip%...
adb connect %ip%

rem Restart ADB server
echo Restarting ADB server...
adb kill-server
adb start-server

rem Set the IP address of your Android device
set DEVICE_IP=192.168.0.105

rem Set the port number for ADB
set ADB_PORT=5555

rem Connect to the Android device over Wi-Fi
echo Connecting to device %DEVICE_IP%:%ADB_PORT%...
adb connect %DEVICE_IP%:%ADB_PORT%

echo Done.
