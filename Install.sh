# ---------------------------------------------------------------------------- #
# Installation script to setup the environment for py7slib                     #
# Author: Felipe Torres González (ftorres<AT>sevensols.com)                    #
# Date: 2016-02-03                                                             #
# ---------------------------------------------------------------------------- #
#!/bin/bash
echo "\033[1mConfiguring py7slib environment...\033[0m"
arch=$(uname -m)
ln bin/eb-discover_$arch bin/eb-discover 2> /dev/null
ln lib/libetherbone.so.1.0_$arch lib/libetherbone.so.1 2> /dev/null
ln lib/libetherbone.so.1 lib/libetherbone.so 2> /dev/null
