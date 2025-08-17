

1. PyInstaller Build Command for macOS with App Icon
```
# from project root:
cd backend

pyinstaller \
  --onefile \
  --windowed \
  --name "RI Tracker" \
  --icon=icon.icns \
  --hidden-import=AppKit \
  --hidden-import=objc \
  --hidden-import=PyObjCTools \
  --hidden-import=PyObjCTools.AppHelper \
  --add-data=dist:dist \
  main.py

# go back to root (optional) when done
cd ..
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

hiddenimports=['AppKit', 'PyObjCTools', 'PyObjCTools.AppHelper', 'objc'],