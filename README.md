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

