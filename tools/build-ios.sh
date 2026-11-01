#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)
if [ "$(uname -s)" != Darwin ]; then
  echo 'iOS build requires macOS and Xcode.' >&2
  exit 1
fi
cd "$TASK_ROOT/mobile_flutter"
flutter pub get
flutter analyze --no-fatal-infos
flutter test
if [ "${SIMCONTROL_IOS_NO_CODESIGN:-0}" = 1 ]; then
  flutter build ios --release --no-codesign
else
  flutter build ipa --release
  mkdir -p "$TASK_ROOT/releases/iOS"
  cp build/ios/ipa/*.ipa "$TASK_ROOT/releases/iOS/"
fi
