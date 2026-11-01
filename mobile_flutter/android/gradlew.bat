@echo off
setlocal
set TASK_APP_DIR=%~dp0
if defined JAVA_HOME (set "TASK_JAVA=%JAVA_HOME%\bin\java.exe") else (set "TASK_JAVA=java.exe")
"%TASK_JAVA%" -classpath "%TASK_APP_DIR%gradle\wrapper\gradle-wrapper.jar" org.gradle.wrapper.GradleWrapperMain %*
exit /b %ERRORLEVEL%
