# RI-Tracker-Lite

Commands:

```
venv\Scripts\activate       // Windows
source venv/bin/activate        // Mac or Linux


python -m pip install pyinstaller==5.13.0

pip install -r requirements.txt

pyinstaller --onefile --noconsole --icon=icon.ico --add-data "dist;dist" main.py

pyinstaller main.spec       // No
```


# Mac

```shell

pyinstaller --onefile --noconsole --icon=icon.ico --windowed --name "RI Tracker" --add-data=dist:dist main.py

[Output]
dist/RI Tracker      ← Executable (or .app if bundled)

[Run it]
./dist/RI\ Tracker

```

```shell
mkdir -p installer/RITemp
cp dist/RI\ Tracker installer/RITemp/


mkdir installer/background
cp my_background.png installer/background/


brew install create-dmg

create-dmg \
  --volname "RI Tracker" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "RI Tracker" 150 150 \
  --hide-extension "RI Tracker" \
  --app-drop-link 450 150 \
  --background "installer/background/logo.png" \
  "RI_Tracker.dmg" \
  "installer/RITemp"

[Output]
RI_Tracker.dmg  ✅ ready to share

pyinstaller --onefile --noconsole --add-data "dist:dist" main.py
```



## Logo --> .icns
```shell
# Create iconset
mkdir icon.iconset
sips -z 16 16     logo.png --out icon.iconset/icon_16x16.png
sips -z 32 32     logo.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     logo.png --out icon.iconset/icon_32x32.png
sips -z 64 64     logo.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   logo.png --out icon.iconset/icon_128x128.png
sips -z 256 256   logo.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   logo.png --out icon.iconset/icon_256x256.png
sips -z 512 512   logo.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   logo.png --out icon.iconset/icon_512x512.png
cp logo.png       icon.iconset/icon_512x512@2x.png

iconutil -c icns icon.iconset

```




