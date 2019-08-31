# Connecting Raspbian Buster with eduroam

The WiFi connection to eduroam can be realized by the wpa_supplicant program.
The wpa_supplicant.conf has to to be edited accordingly and then moved to /etc/wpa_supplicant.

## Problem

The wifi connection to eduroam is realized by WPA2 Enterprise.
As of August 2019 the firmware of the Broadcom Chip inside Raspberry Pi 3+ and the Linux driver nl80211  have a incompatibility that prevents any connection.
[https://www.raspberrypi.org/forums/viewtopic.php?t=247310](Discussion in the Raspberry Pi forum.)

## Solution

Alternatively, the driver wext has to be loaded by adding the line
`env wpa_supplicant_driver=wext`
to the configuration of the dhcp daemon /etc/dhcpcd.conf.

Do not try to solve this issue by editing /etc/networks/interfaces, since this causes issues with the WiFi widget.

