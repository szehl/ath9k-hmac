# ATH9K HTDMA Hybrid TDMA/CSMA MAC 
```
+-----------+------------------------------------+
|           |                                    | Python HMAC Wrapper enables
|  User     |   HMAC Python Wrapper              | easy integration in python scripts
|  Space    |                                    | starts / stops / updates HMAC
|           |                                    | user-space daemon and schedule
|           +---------------+--------------------+ via ZMQ IPC
|                           |                    |
|                           | ZeroMQ             |
|                           |                    |
|                           |                    |  
|           +---------------v--------------------+  
|           |                                    | HMAC User Space Daemon  
|           |   HMAC User-Space Daemon           | schedules Software Queues  
|           |                                    | by sending Netlink Commands  
|           |                                    | to wake/sleep specific TIDs  
+-----------+---------------+--------------------+ of a Link identied through  
                            |                      MAC address  
                            |  Netlink  
                            |  
+-----------+------------------------------------+
|           |               |                    |
|  Kernel   |     cfg80211  |                    |
|  Space    |               |                    |
|           |               |                    |
|           +------------------------------------+
|           |               |                    |
|           |               |                    |
|           |     mac80211  |                    |
|           |               |                    |
|           +------------------------------------+
|           |               | MAC ao:f1:...      | ATH9k Traffic Identifier
|           |               +--+--+--+--+        | Software Queues
|           |     ath9k     |  |  |  |  |...     | HMAC pauses/unpauses Queues
|           |               |0 |1 |2 |3 |        | 7 Queues (TIDs per Link)
+-----------+---------------------------+--------+
```


## HOW TO INSTALL ATH9K HTDMA on Ubuntu Linux in 3 steps: 
### Download HMAC sources:
```
cd ~; mkdir hmac; cd hmac; git clone https://github.com/szehl/ath9k-hmac.git; 
```
### Install 3.12 kernel:
```
chmod +x ath9k-hmac/install_3.12_kernel.sh; ath9k-hmac/install_3.12_kernel.sh
```
Now reboot machine and choose 3.12 kernel during boot in the grub menu.

### Install HMAC driver

```
cd ~/hmac/ath9k-hmac/backports-3.12.8-1; make defconfig-ath9k; make -j4; sudo make install
```
Now again reboot your machine and choose 3.12 kernel during boot in the grub menu.
After Reboot the ATH9k-HMAC should be installed, you can check by typing
```
dmesg | grep TID
```
If the output is something like:
```
[    3.648915] ath: TID SLEEPING MODE ENABLED
```
Everything went well.

## How to install HMAC on other Linux distributions and Kernels:

Go to  https://www.kernel.org/pub/linux/kernel/projects/backports/stable
and look for the backports version that fits for your kernel, download and unpack  it.
```
e.g.
cd /tmp/
mkdir backports
cd backports
wget https://www.kernel.org/pub/linux/kernel/projects/backports/stable/v3.12.8/backports-3.12.8-1.tar.gz
tar -xzf backports-3.12.8-1.tar.gz
```
Download ATH9k-HMAC Patch for your kernel (hopefully we have the correct one for you, otherwise you have to adjust the patch on your own or switch to another kernel), apply patch to your backports source.
```
cd /tmp/
https://github.com/szehl/ath9k-hmac.git
cd backports/backports-3.12.8-1/
patch -t -p3 < ../../patch/ath9k-hmac/ath9k-hmac-backports-3.12.8-1.patch
```
Build and install the ATH9k-HMAC driver.
```
cd /tmp/backports/backports-3.12.8-1/
make defconfig-ath9k
make -j4
sudo make install
```
After Reboot the ATH9k-HMAC should be installed, you can check by typing
```
dmesg | grep TID
```
If the output is something like:
```
[    3.648915] ath: TID SLEEPING MODE ENABLED
```
Everything went well.

## HOW TO USE ATH9k HMAC
First you have to compile the hmac_userspace_daemon.
If you installed the ATH9k HMAC driver with the 3 step manual, you can simply use:
```
cd ~/hmac/ath9k-hmac/hmac_userspace_daemon; make;
```
Otherwise make sure that the file hmac_userspace_daemon/hybrid_tdma_csma_mac.c includes the correct nl80211.h you used during building the ATH9k HTDMA driver.


We are now able to give the HMAC a first try without the Python wrapper. Just execute the following line in the hmac_userspace_daemon folder (replace wlan0 with your ATH9k WiFi interface, take sure it is up and rfkill is disabled (e.g. sudo rfkill unblock all)):
```
sudo ./hmac_userspace_daemon -i wlan0 -f 20000 -n 10 -c 1,b8:a3:86:96:96:8a,1#2,b8:a3:86:96:96:8a,1#3,b8:a3:86:96:96:8a,1#4,b8:a3:86:96:96:8a,1#6,ec:1f:72:82:09:56,1#7,ec:1f:72:82:09:56,1#8,ec:1f:72:82:09:56,1#9,ec:1f:72:82:09:56,1
```
If no error is shown and the daemon just prints out the current slot size, we are fine, the HMAC is working.


The HMAC user-space deaemon is using the following configuration parameters:
```
sudo ./hmac_userspace_daemon 
-i wlan0                     # ATH9k WiFi Interface on which HMAC schedule should be applied
-f 20000                     # Size of each slot in micro seconds
-n 10                        # Number of Slots
-c                           # Schedule, format: "Slotnumber","MAC Address of Destination","TID Bitmap"#
                             #e.g.:
1,b8:a3:86:96:96:8a,1#2,ec:1f:72:82:09:56,1#3,b8:a3:86:96:96:8a,1#4,b8:a3:86:96:96:8a,1#6,ec:1f:72:82:09:56,1#7,ec:1f:72:82:09:56,1#8,ec:1f:72:82:09:56,1#9,ec:1f:72:82:09:56,1
```
The example uses the following configuration: Interface: wlan0, Size of each Slot: 20ms, Number of Slots: 10 (SuperSlot = 200ms), Scheduler Konfiguration: first slot, Link with STA b8:a3:86:96:96:8a, TID MAP: 0b0000001 means TID 1 (Best Effort), '#' is used as seperator, second slot: Link with STA ec:1f:72:82:09:56, TID TID MAP: 0b0000001 means TID 1 (Best Effort), ... etc.
