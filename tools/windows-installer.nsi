Unicode true
!include "MUI2.nsh"
!include "x64.nsh"
!ifndef APPDIR
  !error "Pass APPDIR containing the published self-contained Windows build"
!endif
!ifndef OUTPUT
  !define OUTPUT "SIM_CONTROL_STUDIO_0.4.0_Setup_x64.exe"
!endif
Name "SIM CONTROL STUDIO 0.4.0"
OutFile "${OUTPUT}"
InstallDir "$LOCALAPPDATA\Programs\SimControlStudio"
InstallDirRegKey HKCU "Software\SimControlStudio" "InstallDir"
RequestExecutionLevel user
SetCompressor /SOLID lzma
VIProductVersion "0.4.0.0"
VIAddVersionKey /LANG=1038 "ProductName" "SIM CONTROL STUDIO"
VIAddVersionKey /LANG=1038 "FileDescription" "SIM CONTROL STUDIO Windows Bridge telepítő"
VIAddVersionKey /LANG=1038 "FileVersion" "0.4.0.0"
VIAddVersionKey /LANG=1038 "LegalCopyright" "SIM CONTROL STUDIO"
!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\SimControlStudio.Bridge.exe"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Hungarian"
Function .onInit
  ${IfNot} ${RunningX64}
    MessageBox MB_OK "64 bites Windows szükséges."
    Abort
  ${EndIf}
FunctionEnd
Section "Windows Bridge"
  ; A running (tray) Bridge keeps its files open: close it first so files can be replaced.
  nsExec::Exec 'taskkill /IM SimControlStudio.Bridge.exe'
  Pop $0
  Sleep 1500
  nsExec::Exec 'taskkill /F /IM SimControlStudio.Bridge.exe'
  Pop $0
  Sleep 500
  SetOutPath "$INSTDIR"
  ; Debug symbols are not needed by users and are the files most often held open.
  Delete "$INSTDIR\*.pdb"
  File /r /x *.pdb "${APPDIR}\*"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\SimControlStudio" "InstallDir" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SimControlStudio" "DisplayName" "SIM CONTROL STUDIO 0.4.0"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SimControlStudio" "DisplayVersion" "0.4.0"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SimControlStudio" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SimControlStudio" "InstallLocation" "$INSTDIR"
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SimControlStudio" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SimControlStudio" "NoRepair" 1
  CreateDirectory "$SMPROGRAMS\SIM CONTROL STUDIO"
  CreateShortcut "$SMPROGRAMS\SIM CONTROL STUDIO\PC Bridge.lnk" "$INSTDIR\SimControlStudio.Bridge.exe"
  CreateShortcut "$SMPROGRAMS\SIM CONTROL STUDIO\Eltávolítás.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd
Section "Uninstall"
  Delete "$SMPROGRAMS\SIM CONTROL STUDIO\PC Bridge.lnk"
  Delete "$SMPROGRAMS\SIM CONTROL STUDIO\Eltávolítás.lnk"
  RMDir "$SMPROGRAMS\SIM CONTROL STUDIO"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SimControlStudio"
  DeleteRegKey HKCU "Software\SimControlStudio"
  ; Pairing, certificate and personal settings in LocalAppData/SimControlStudio remain.
SectionEnd
