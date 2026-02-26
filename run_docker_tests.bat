@echo off
echo =========================================
echo   Запуск тестов в Docker-контейнерах
echo =========================================

REM Очистка старых отчетов
if exist allure-results rmdir /s /q allure-results
if exist allure-report rmdir /s /q allure-report
mkdir allure-results
mkdir allure-report

REM Запуск тестов
docker-compose up --build test-runner

echo =========================================
echo   Тесты завершены
echo =========================================
pause