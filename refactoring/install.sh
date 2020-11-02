#!/bin/bash
echo "installing... ctail to /usr/local/bin/"
cd /usr/local/bin/
rm -f ctail ctail.py
wget https://raw.githubusercontent.com/castisdev/ctail/master/ctail.py --no-check-certificate
chmod +x ctail.py
mv ctail.py ctail
echo "...done."
