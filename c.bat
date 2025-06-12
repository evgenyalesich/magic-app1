@echo off
setlocal

REM Проверка наличия папки .git
if not exist ".git" (
    echo Ошибка: Не найден Git-репозиторий в текущей папке
    exit /b 1
)

REM Проверка параметра
if "%~1"=="" (
    echo Использование: %~nx0 "Сообщение коммита"
    echo Пример: %~nx0 "Рефакторинг модуля API"
    exit /b 1
)

REM Основной блок
git add . && git commit -m "%~1" && git push origin main

endlocal
