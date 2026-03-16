[app]
title = Roguelike Adventure
package.name = roguelike
package.domain = org.alexstudiocode.roguelike
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,ttf,wav,mp3,ogg,txt
version = 0.1.3
requirements = python3,kivy==2.2.1,pyjnius,android
orientation = landscape
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin

[android]
api = 33
minapi = 21
ndk = 25b  # Явно указываем версию NDK
sdk = 33
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET
android.accept_sdk_license = True
ndk_accept_license = True
