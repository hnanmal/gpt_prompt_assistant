@echo off
chcp 65001 >nul
setlocal

echo ===========================================
echo  Ollama 모델 데이터를 D 드라이브로 이전합니다
echo  기존의 %%USERPROFILE%%\.ollama → D:\ollama
echo ===========================================
echo.

:: Ollama 종료
echo 🛑 Ollama 프로세스를 종료합니다...
taskkill /f /im ollama.exe >nul 2>&1

:: 기존 폴더 또는 심볼릭 링크 제거
echo 🔄 기존 .ollama 폴더 또는 링크 제거 중...
rmdir /s /q "%USERPROFILE%\.ollama" 2>nul

:: 대상 폴더 생성
echo 📁 D:\ollama 디렉토리를 생성합니다...
mkdir D:\ollama >nul 2>&1

:: 심볼릭 링크 생성
echo 🔗 심볼릭 링크를 생성합니다...
mklink /D "%USERPROFILE%\.ollama" "D:\ollama"

echo.
echo ✅ 심볼릭 링크 생성 완료!
echo    실제 모델 파일은 D:\ollama 에 저장됩니다.
echo.

pause
