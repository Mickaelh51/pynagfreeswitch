#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# date: 14/01/2019
# username: mickaelh51
# name: HUBERT Mickael
# description: a basic nagios script for FreeSWITCH.
# licence: MIT
# github page: https://github.com/Mickaelh51/pynagfreeswitch

'''
Ex:
pynagfreeswitch.py -t -w 10 -c 20 ==> OK - Total calls count is 0
pynagfreeswitch.py -g gateway1 -G failedcallsout -w 10 -c 20 ==> OK - gateway1 failedcallsout is 2
pynagfreeswitch.py -g GWSCR1 -G pingtime -w 0.20 -c 0.56 ==> WARNING - GWSCR1 pingtime is 0.55
pynagfreeswitch.py -g GWSCR1 -G status -S up ==> OK - GWSCR1 status is up
pynagfreeswitch.py -g GWSCR1 -G state -S noreg ==> OK - GWSCR1 state is noreg
'''

import sys
import ESL
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--auth', dest='auth', default='ClueCon', help='ESL password')
parser.add_argument('-s', '--server', dest='server', default='127.0.0.1', help='FreeSWITCH server IP address')
parser.add_argument('-p', '--port', dest='port', default='8021', help='FreeSWITCH server event socket port')
parser.add_argument('-w', '--warning', dest='warning', help='threshold that generates a Nagios warning')
parser.add_argument('-c', '--critical', dest='critical', help='threshold that generates a Nagios critical warning')
parser.add_argument('-g', '--gateway', dest='gateway', help='select gateway')
parser.add_argument('-G', '--gatewaycheck', dest='gatewaycheck', help='type of check (failedcallsout / status / state / ...)')
parser.add_argument('-t', '--totalcallscount', action='store_true' , help='total calls count')
parser.add_argument('-S', '--stringok', dest='stringok' , help='if this string is found = OK')

options = parser.parse_args()

con = ESL.ESLconnection(options.server, options.port, options.auth)

if not con.connected():
	print ('UKNOWN - Not Connected to ' + options.server)
	sys.exit(3)
else:
	uuid = con.api("create_uuid").getBody()

calls_count_command = 'show calls count'
gateway_status_command = 'sofia status gateway '
#show_registration_command = 'show registrations'

'''
return dict
{
	'context': 'internal',
	'profile': 'internal',
	....
	'pingstate': '1/1/1',
	'failedcallsout': '2',
	'callsin': '0',
	'expires': '3600',
	'pingfreq': '25'
	...
}
'''
def parse_gateway_status(body, key):
	try:
		data = dict(line.split() for line in body.lower().splitlines() if line and '===' not in line)
		return data[key]
	except:
		return None

def parse_calls_count(body):
	try:
		data = dict(line.split() for line in body.lower().splitlines() if line)
		return dict(map(reversed, data.items()))['total.']
	except:
		return None

def send_api_command(con, command, gateway):
	e = con.api(command + gateway)
	if e:
		return e.getBody()

def gateway_count_check(calls_count, warning, critical, human):
	if not options.warning and not options.critical:
		print ('UKNOWN - Warning / Critical options missing')
		sys.exit(3)

	if calls_count < warning:
		print ("OK - %s is %s" % (human, calls_count))
		sys.exit(0)
	elif warning <= calls_count < critical:
		print ("WARNING - %s is %s" % (human, calls_count))
		sys.exit(1)
	elif critical < calls_count:
		print ("CRITICAL - %s is %s" % (human, calls_count))
		sys.exit(2)
	else:
		print ("UKNOWN - %s error" % human)
		sys.exit(3)

def stringok_check(result, stringok, human):
	if result == stringok:
		print ("OK - %s is %s" % (human, result))
		sys.exit(0)
	else:
		print ("CRITICAL - %s is %s" % (human, result))
		sys.exit(2)

# Run commands
if options.totalcallscount and options.warning and options.critical:
	total_calls_count = int(parse_calls_count(send_api_command(con, calls_count_command, '')))
	gateway_count_check(total_calls_count, int(options.warning), int(options.critical), 'Total calls count')

elif options.gateway and options.gatewaycheck:
	if 'calls' in options.gatewaycheck or 'pingtime' in options.gatewaycheck:
		try:
			gateway_counter = parse_gateway_status(send_api_command(con, gateway_status_command, options.gateway), options.gatewaycheck)
		except:
			raise
			print ('UKNOWN - gateway: ' + options.gateway + ' | gateway check: ' + options.gatewaycheck)
			sys.exit(3)

		if 'calls' in options.gatewaycheck and options.warning and options.critical and gateway_counter:
			gateway_count_check(int(gateway_counter), int(options.warning), int(options.critical), options.gateway + ' ' + options.gatewaycheck)
		elif 'pingtime' in options.gatewaycheck:
			gateway_count_check(float(gateway_counter), float(options.warning), float(options.critical), options.gateway + ' ' + options.gatewaycheck)
		else:
			print ('UKNOWN - No warning or critical or gateway found')
			sys.exit(3)

	elif options.stringok:
		try:
			findresult = parse_gateway_status(send_api_command(con, gateway_status_command, options.gateway), options.gatewaycheck)
		except:
			print ('UKNOWN - gateway: ' + options.gateway + ' | gateway check: ' + options.gatewaycheck)
			sys.exit(3)

		stringok_check(findresult, options.stringok, options.gateway + ' ' + options.gatewaycheck)

	else:
		print ('UKNOWN - No correct gateway check option found')
		sys.exit(3)
else:
	print ('UKNOWN - No correct options found')
	sys.exit(3)
