#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$TASK_ROOT"
python3 tests/validate_profiles.py
dotnet run --project tests/Bridge.Tests/Bridge.Tests.csproj -c Release -- tests/results/bridge-tests.json
if command -v flutter >/dev/null 2>&1; then
  cd mobile_flutter
  flutter pub get
  flutter analyze
  flutter test
else
  echo 'Flutter SDK unavailable. Mobile analyzer, tests and builds were NOT executed.' >&2
fi
