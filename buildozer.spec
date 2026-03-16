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
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET
android.minapi = 21
android.api = 33
android.ndk = 25b
android.build_tools = 33.0.0
android.archs = arm64-v8a
android.accept_sdk_license = True
android.ndk_accept_license = True

[buildozer]
log_level = 2
bin_dir = ./bin
