

1. PyInstaller Build Command for macOS with App Icon
```
pyinstaller \
  --onefile \
  --windowed \
  --name "RI Tracker" \
  --icon=icon.icns \
  --add-data=dist:dist \
  main.py

```

2. Copy
```

mkdir -p dmg-build/RITemp
cp -R dist/RI\ Tracker.app dmg-build/RITemp/

```

3. Build
```aiignore

create-dmg \
  --volname "RI Tracker" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "RI Tracker.app" 150 190 \
  --app-drop-link 450 190 \
  "RI_Tracker.dmg" \
  "dmg-build/RITemp"



  --background "dmg-build/background/bg.png" \
```

