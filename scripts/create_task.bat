@echo off
schtasks /Create /TN "MetaAds-DailyCollect" /TR "\"C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe\" \"C:\Users\user\Desktop\AIOS META\meta-ads-intelligence\scripts\daily_collect.py\"" /SC DAILY /ST 07:00 /F
if %errorlevel%==0 (
    echo Tarefa criada com sucesso! Coleta diaria as 07:00.
) else (
    echo ERRO ao criar tarefa.
)
pause
