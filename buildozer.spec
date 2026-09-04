[app]

title = AI Trader
version = 0.1

package.name = aitrader
package.domain = org.aitrader

source.dir = .
source.exclude_exts = spec
source.include_exts = py,png,jpg,kv,atlas

requirements = python3,kivy,websocket-client

orientation = portrait

android.permissions = INTERNET

android.api = 33
android.minapi = 24
android.sdk = 33
android.ndk = 25b

android.build_mode = debug
