# pynagfreeswitch
a basic nagios script to check a FreeSWITCH instance

# Ex:
```
pynagfreeswitch.py -t -w 10 -c 20 ==> OK - Total calls count is 0
pynagfreeswitch.py -g gateway1 -G failedcallsout -w 10 -c 20 ==> OK - gateway1 failedcallsout is 2
pynagfreeswitch.py -g GWSCR1 -G pingtime -w 0.20 -c 0.56 ==> WARNING - GWSCR1 pingtime is 0.55
pynagfreeswitch.py -g GWSCR1 -G status -S up ==> OK - GWSCR1 status is up
pynagfreeswitch.py -g GWSCR1 -G state -S noreg ==> OK - GWSCR1 state is noreg
```
