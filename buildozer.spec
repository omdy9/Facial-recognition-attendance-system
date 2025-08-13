[app]

# (str) Title of your application
title = Face Attendance App

# (str) Package name
package.name = faceattendanceapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# Add any additional requirements like opencv, face_recognition, or other libraries you might need
requirements = python3,kivy,opencv-python,face_recognition

# (str) Custom source folders for requirements
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application (you can add a presplash image here if needed)
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
orientation = portrait

# (list) Android specific settings

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (bool) Enable Android auto backup feature (Android API >=23)
android.allow_backup = True

# (list) Permissions required by your app
android.permissions = android.permission.CAMERA, android.permission.ACCESS_FINE_LOCATION

# (list) Android architecture to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enable AndroidX support (if using any AndroidX packages)
# android.enable_androidx = True

# (bool) If True, automatically accept SDK license agreements
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) Path to a custom whitelist file
android.whitelist_src = %(source.dir)s/whitelist.txt

# (str) Full name including package path of the Java class that implements Python Activity
# android.activity_class_name = org.kivy.android.PythonActivity

# (bool) If True, skip byte compile for .py files
android.no-byte-compile-python = False

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (list) Additional Android libraries to include
# android.add_libs_armeabi = libs/android/*.so

# (list) Path to a custom backup rules XML file
# android.backup_rules = %(source.dir)s/data/backup_rules.xml

# iOS specific settings
# ios.kivy_ios_url = https://github.com/kivy/kivy-ios
# ios.kivy_ios_branch = master

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin

# (str) Path to the Android SDK
android.sdk_path = C:\Users\abc\AppData\Local\Android\Sdk

# (str) Path to the Android NDK
android.ndk_path = C:\Users\abc\AppData\Local\Android\Sdk\ndk\29.0.13113456
