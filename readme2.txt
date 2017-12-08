Hey fellow competitors!

Just wanted to let you know that I’ve uploaded the final state of the tournament machine to github, so you can re-watch the replays, try out the surprize maps, and poke at your competitors executables to your heart’s content!

https://github.com/coastwise/tron-engine

I also added any individual bot’s log files I found on a separate branch called “logs”. Let me know if you think I may have missed something. Minh still has the machine for a bit before he’s going to return it to IT and it will be wiped clean.

I havn’t updated the readme file yet, but I’ve added some windows scripts to run stuff. Here’s a brief rundown:

smackdown.bat will re-run the tournament. It is configured using smackdown_bots.txt and smackdown_maps.txt. A full output of the results gets written to tournaments/smackdown/result.txt, but unfortunately I wasn’t able to upload the one from the official tournament as it got overwritten with the final run on quadrant.

To view the replays, you need to run a CGI server. Double click the replayserver.bat to spin one up. Then you can access the replays here: http://localhost:8000/cgi-bin/tourney.py?name=smackdown

The maps used for the tournament were as follows:
Round robin: Smackdown.txt
Round robin tie breaker: u.txt (modified from original map)
Finals: toronto.txt (modified from original map)
