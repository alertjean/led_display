led_display https://www.youtube.com/watch?v=_a1n5R9T6qw
1. Hacked infoglobe to display news headlines.
2. Downloads news headlines from links in rss.py and displays on a hacked info globe.
3. Raspberry Pi Zero is used with a wired ethernet connection.
4. Most of the existing circuit and logic in inflo globe was removed. 
5. Only circuit required to do wireles power transfer to rotating display board was retrained.
6. One of the GPIOs on Raspberry Pi was used to drive an IR led to send IR code to rotating board
7. Should install pigpiod and run it in background
8. Also includes a tiny http_server to send custom messages to infloglobe from any device on network.
