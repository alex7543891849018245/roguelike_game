[app]

# (str) Название приложения
title = Roguelike Adventure

# (str) Имя пакета
package.name = roguelike

# (str) Домен приложения
package.domain = org.alexstudiocode.roguelike

# (str) Основной файл Python
source.dir = .

# (list) Расширения файлов для включения в APK
source.include_exts = py,png,jpg,jpeg,kv,ttf,wav,mp3,ogg,txt,md

# (str) Версия приложения
version = 0.1.3

# (str) Код версии (целое число, должно увеличиваться)
version.code = 1

# (list) Требования (только нужное)
requirements = python3,kivy==2.2.1,pyjnius,android

# (str) Ориентация экрана
orientation = landscape

# (bool) Полноэкранный режим
fullscreen = 1

# (list) Разрешения для Android
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# (str) Категория приложения в Google Play
android.category = GAME

# (bool) Включить поддержку Java 8
android.javac = 1.8

# (bool) Включить кэширование для быстрой пересборки
android.accept_sdk_license = True
android.ndk_accept_license = True

# (int) Минимальная версия Android
android.minapi = 21

# (int) Целевая версия Android SDK
android.api = 33

# (str) Версия SDK (обычно совпадает с api)
android.sdk = 33

# (str) Версия NDK (стабильная версия, работает без патчей)
android.ndk = 23b

# (str) Версия build-tools (важно для избежания проблем)
android.build_tools = 33.0.0

# (str) Архитектуры - ТОЛЬКО arm64-v8a для ускорения в 2 раза
android.archs = arm64-v8a

# (bool) Включить поддержку AndroidX
android.use_androidx = True

# (bool) Включить прозрачный фон для заставки
android.transparent_presplash = True

# (str) Цвет заставки
presplash_color = #000000

# (bool) Для отладки - показывать логи Python
android.logcat_filters = *:S python:D

[buildozer]

# (int) Уровень логирования (1=предупреждения, 2=инфо, 3=отладка)
log_level = 2

# (bool) Предупреждать, если запускать от root
warn_on_root = 1

# (str) Папка для выходных файлов
bin_dir = ./bin
