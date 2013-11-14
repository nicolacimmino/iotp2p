#!/bin/bash
# iotp2p modules installer  provides path configuration to use iotp2p python modules.
#   Copyright (C) 2013 Nicola Cimmino
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.

banner='\e[0;37m\e[0;44m'
endbanner='\e[0m'


echo
echo -e "${banner}**************************************************${endbanner}"
echo -e "${banner}* iotp2p Python Modules Installation.            *${endbanner}"
echo -e "${banner}**************************************************${endbanner}"
echo
echo We need to add $PWD to PYTOHNPATH
echo This allows our scripts to find the iotp2p python modules
echo "Do you want to proceed?"
select yn in "Yes" "No";
do
    case $yn in
        "Yes")
	  break
	  ;;
        "No")
	  echo "PYTOHNPATH not modified"
          return 0
          ;;
    esac
done
export PYTHONPATH="$PWD:$PYTHONPATH"
echo PYTHONPATH modified.
echo "If you have issues with liberaries not being found ensure you run this scricpt as: source ./install.sh"
echo "This setting is not permanent, run this script again when you reopen the shell."


