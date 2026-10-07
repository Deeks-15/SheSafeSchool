[app]
title = SheSafe@School
package.name = shesafeschool
package.domain = org.shesafe
source.dir = .
source.include_exts = py,png,jpg,json,txt
source.exclude_dirs = .git,.github,__pycache__,tests
version = 2.0.1
requirements = python3==3.12.11,hostpython3==3.12.11,kivy==2.3.1,fastapi==0.99.1,pydantic==1.10.13,uvicorn==0.22.0,h11==0.14.0
orientation = portrait
fullscreen = 0
icon.filename = assets/icon.png
presplash.filename = assets/icon.png
android.permissions = INTERNET
android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
p4a.bootstrap = sdl2
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
