$env:DJANGO_DEBUG = "1"
$env:MONGO_DB_NAME = "asfoaustech"
Set-Location -LiteralPath $PSScriptRoot
& "C:\Users\user\AppData\Local\Python\bin\python.exe" manage.py runserver 8000
