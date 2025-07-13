@echo off
setlocal enabledelayedexpansion

REM Проверяем параметр с сообщением коммита
if "%~1"=="" (
    echo Использование: %~nx0 "Сообщение коммита" [remote-URL]
    echo Пример 1 (существующий репозиторий):
    echo   %~nx0 "Обновил документацию"
    echo Пример 2 (новый репозиторий, первый пуш):
    echo   %~nx0 "Первый коммит" https://github.com/evgenyalesich/magic-app1.git
    exit /b 1
)

set COMMIT_MSG=%~1
set REMOTE_URL=%~2

REM 1) Если нет папки .git — инициализируем
if not exist ".git" (
    echo [INFO] Git-репозиторий не найден. Инициализируем...
    git init
    if errorlevel 1 (
        echo Ошибка: не удалось выполнить git init.
        exit /b 1
    )
)

REM 2) Проверяем, настроен ли remote origin
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    REM Если нет, то нужен URL
    if "%REMOTE_URL%"=="" (
        echo Ошибка: удалённый репозиторий (origin) не настроен.
        echo Укажите URL вторым параметром:
        echo   %~nx0 "%COMMIT_MSG%"  https://github.com/evgenyalesich/magic-app1.git

        exit /b 1
    ) else (
        echo [INFO] Добавляем remote origin = %REMOTE_URL%
        git remote add origin %REMOTE_URL%
        if errorlevel 1 (
            echo Ошибка: не удалось добавить remote origin.
            exit /b 1
        )
    )
)

REM 3) Проверяем, есть ли ветка main локально
git show-ref --verify --quiet refs/heads/main
if errorlevel 1 (
    echo [INFO] Создаём и переключаемся на ветку main...
    git checkout -b main
)

REM 4) Добавляем все изменения, коммитим и пушим
echo [INFO] git add .
git add .
if errorlevel 1 (
    echo Ошибка: git add завершился с кодом ошибки.
    exit /b 1
)

echo [INFO] git commit -m "%COMMIT_MSG%"
git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
    echo Ошибка: git commit завершился с кодом ошибки.
    exit /b 1
)

echo [INFO] git push -u origin main
git push -u origin main
if errorlevel 1 (
    echo Ошибка: git push завершился с кодом ошибки.
    exit /b 1
)

echo [OK] Операция завершена успешно.
endlocal
