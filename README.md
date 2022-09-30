# led_display
# https://www.youtube.com/watch?v=_a1n5R9T6qw
# Downloads news headlines from links in rss.py and displays on a hacked info globe.
# Raspberry Pi Zero is used with a wired ethernet connection.
# Most of the existing circuit and logic in inflo globe was removed. 
# Only circuit required to do wireles power transfer to rotating display board was retrained.
# One of the GPIOs on Raspberry Pi was used to drive an IR led to send IR code to rotating board
# Should install pigpiod and run it in background
# Also includes a tiny http_server to send custom messages to infloglobe from any device on network.
