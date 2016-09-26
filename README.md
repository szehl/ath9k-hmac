# ATH9K HTDMA Hybrid TDMA/CSMA MAC #

## HOW TO INSTALL ATH9K  HTDMA ##
### Download the appropriate backports version for your kernel ### 
```
uname -r
```
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
git clone XXXXX
cd backports/backports-3.12.8-1/
patch -t -p3 < ../../XXXXX/patch-hmac.patch
```
Build and install the ATH9k-HMAC driver.
```
cd /tmp/backports/backports-3.12.8-1/
make defconfig-ath9k
make -j4
```
