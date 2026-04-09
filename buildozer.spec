[app]

title = Daken Radar
package.name = dakenradar
package.domain = org.daken
source.dir = .
version = 3.0
version.code = 3
requirements = python3,kivy
orientation = landscape
fullscreen = 1

android.skip_setup_check = True

osx.python_version = 3
osx.kivy_version = 2.1.0

android.permissions = SYSTEM_ALERT_WINDOW, FOREGROUND_SERVICE
android.api = 30
android.minapi = 21
android.gradle_dependencies = com.android.support:support-annotations:28.0.0
android.add_activity = org.kivy.android.PythonActivity
android.whitelist = True

[buildozer]

log_level = 2
warn_on_root = 1

build_dir = .buildozer
dist_dir = bin

android.accept_sdk_license = True
android.ndk = 23b
android.sdk = 30
android.archs = arm64-v8a
