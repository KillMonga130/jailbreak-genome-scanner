@echo off
REM SSH Tunnel Starter for Windows
REM This script starts an SSH tunnel to forward port 8000 from Lambda instance to localhost

echo Starting SSH tunnel for Lambda Cloud instance...
echo.

python scripts\ssh_tunnel_helper.py --ip 150.136.146.143 --key moses.pem

pause

