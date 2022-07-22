# ---------------------------------------------------------------------------- #
# Installation script to setup the environment for py7slib                     #
# Author: Felipe Torres González (ftorres<AT>sevensols.com)                    #
# Date: 2016-02-03                                                             #
# ---------------------------------------------------------------------------- #
#!/bin/bash
echo "Configuring py7slib environment..."
arch=$(uname -m)
ln -fv bin/eb-discover_$arch bin/eb-discover
#ln lib/libetherbone.so.1.0_$arch lib/libetherbone.so.1
#ln lib/libetherbone.so.1 lib/libetherbone.so
ln -fv lib/libetherbone.so_$arch lib/libetherbone.so
