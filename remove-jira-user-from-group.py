# Remove Jira users from jira-users and jira-servicedesk-users group with CSV SSO list
#   CSV file must be in the format exported by the myUserManagerForJira plug-in app

import sys
import csv
from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

#--------------------------------------------

def removeuserfromgroup(username, groupname):
	try:  # call rest api
		response = requests.delete(f"https://{jirahostname}/rest/api/latest/group/user", 
			params={'groupname':groupname, 'username':username}, auth=HTTPBasicAuth(myjirauser, myjirapwd))
		response.raise_for_status()
		# Code here will only run if the request is successful
		(errorsev, errormsg) = (0, '')
	except requests.exceptions.HTTPError as errhttp:
		if response.status_code == 400:
			(errorsev, errormsg) = (1, f"STATUS 400 - User {username} does not belong to group {groupname}.")
		elif response.status_code == 401:
			(errorsev, errormsg) = (2, f"STATUS 401 - Cannot authenticate user {myjirauser}.")
		elif response.status_code == 403:
			(errorsev, errormsg) = (2, f"STATUS 403 - User {myjirauser} does not have administrator permissions.")
		elif response.status_code == 404:
			(errorsev, errormsg) = (1, f"STATUS 404 - User {username} or group {groupname} not found in Jira.")
		else:
			(errorsev, errormsg) = (2, errhttp)
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as errother:
		(errorsev, errormsg) = (2, errother)
	return (errorsev, errormsg)

def printout(printtext):
	print(printtext)  # write to console
	outfile.write(printtext+"\n")  # write to log file
	return

#--------------------------------------------

# receive/set params
csvfilename = sys.argv[1]
targetgroups = ["jira-users", "jira-servicedesk-users"]

# ask me for jira host and my creds
jirahostname = input("\nASKING:  Please enter the Jira hostname: ")
myjirauser = input("\nASKING:  Please enter your Jira Admin user: ")
myjirapwd = getpass("\tPlease enter password: ")

# create and open log file
date_time = datetime.now().strftime('D%Y%m%d_T%H%M%S')
outfile = open(f"remove_groupuser_{date_time}.log", "a")

# process csv file 
with open(csvfilename, newline='') as csvfile:
	csvdata = csv.reader(csvfile, delimiter=",", quotechar="\"")
	totrows = sum(1 for row in csvdata)
	csvfile.seek(0)  # reset csvfile pointer
	nextrowcount = 0
	for csvidx, csvrow in enumerate(csvdata):
		if nextrowcount <= 0:
			# ask me how many rows to process next
			nextrowcount = int(input(f"\nASKING:  How many rows do you want to process next, {(totrows-csvidx)} remaining? Enter 0 to quit: "))
			if nextrowcount == 0:
				printout(f"\nINTERRUPTED:  Process aborted, {(totrows-csvidx)} rows remain unprocessed.\n")
				exit(1)
			else:
				printout(f"\nRUNNING:  Processing next {min(nextrowcount,(totrows-csvidx))} rows out of {(totrows-csvidx)} remaining...")
		if csvrow[1] != "username":   # process non-header row
			loginstatus = csvrow[3]
			if loginstatus == "Idle":
				loginstatus += " for last " + csvrow[4].split(" - since ")[1]
			printout( f"\tJira user {csvrow[1]} {csvrow[2]} ({loginstatus}):" )
			for groupname in csvrow[5].split(','):  # for each group listed in col-6 data
				if groupname in targetgroups:
					(errsev, errmsg) = removeuserfromgroup(username=csvrow[1], groupname=groupname)
					if errsev == 0:
						printout(f"\t\t- user {csvrow[1]} successfully removed from Jira group {groupname}.")
					else:
						printout(f"\t\t- user {csvrow[1]} NOT removed from Jira group {groupname} due to error.")
						printout(f"\t\t\t{errmsg}")
						if errsev >= 2:
							printout(f"\nINTERRUPTED:  Process aborted due to hard failure, {(totrows-csvidx)} rows remain unprocessed.\n")
							exit(1)
		else:
			printout( f"\tColumn header row:\n\t\t- IGNORED" )
		nextrowcount -= 1
	csvfile.close()

printout(f"\nDONE:  Finished processing {(totrows)} total rows.\n")
outfile.close()
exit(0)
