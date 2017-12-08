if not exist "tournaments\smackdown" mkdir tournaments\smackdown
python engines\tournament.py -vv --rounds 3 --replay games/smackdown smackdown_bots.txt smackdown_maps.txt > tournaments\smackdown\result.txt 2>&1
