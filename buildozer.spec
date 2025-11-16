[app]
title = Ninja Proxy
package.name = ninjaproxy
package.domain = org.hacker

source.dir = .
source.include_exts = py,png,jpg,html

version = 1.0
requirements = python3,kivy,requests

[buildozer]
log_level = 2

[app]
presplash.color = #000000
icon = assets/ninja-star.png

[android]
api = 33
ndk = 25b
min_sdk = 21
