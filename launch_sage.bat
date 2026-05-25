@echo off
title SAGE Active Defense Bootstrapper
color 0A

echo ==========================================================
echo        SHIELD ACTIVATING: SAGE ACTIVE DEFENSE
echo ==========================================================
echo.
echo [1] Booting Real-Time FIM Kernel Hooks...
start "SAGE FIM Engine" cmd /k "python fim.py"

timeout /t 2 /nobreak > NUL

echo [2] Launching Local SOC Dashboard UI...
start "SAGE Dashboard" cmd /k "streamlit run dashboard.py"

echo.
echo ==========================================================
echo  ALL SYSTEMS ONLINE. YOU MAY CLOSE THIS LAUNCHER.
echo ==========================================================
pause