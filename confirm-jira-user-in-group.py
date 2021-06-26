# Confirm Jira users in jira-users and jira-servicedesk-users group with CSV SSO list
#   CSV file must be in the format exported by the myUserManagerForJira plug-in app

import sys
import csv
from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

#--------------------------------------------

def confirmuseringroup(username, groupname):
	try:  # call rest api
		response = requests.get(f"https://{jirahostname}/rest/api/latest/user", 
			params={'username':username,'expand':'groups'}, auth=HTTPBasicAuth(myjirauser, myjirapwd))
		response.raise_for_status()
		# Code here will only run if the request is successful
		errorsev = 1
		for group in response.json()["groups"]["items"]:  # for each group assigned to user
			if (group["name"] == groupname):  # check if target group name, if yes turn-off error
				(errorsev, errormsg) = (0, '')
		if errorsev > 0:  # target group not one of groups assigned to user
			errormsg = f"User {username} is not a member of Jira group {groupname}."
	except requests.exceptions.HTTPError as errhttp:
		if response.status_code == 401:
			(errorsev, errormsg) = (2, f"STATUS 401 - Cannot authenticate user {myjirauser}.")
		elif response.status_code == 404:
			(errorsev, errormsg) = (1, f"STATUS 404 - User {username} not found in Jira.")
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
outfile = open(f"confirm_groupuser_{date_time}.log", "a")

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
			if csvrow[3] == "Idle":
				loginstatus += csvrow[3] + " for last " + csvrow[4].split(" - since ")[1]
			else:
				loginstatus = csvrow[3]
			printout( f"\tJira user {csvrow[1]} {csvrow[2]} ({loginstatus}):" )
			for groupname in csvrow[5].split(','):  # for each group listed in col-6 data
				if groupname in targetgroups:
					(errsev, errmsg) = confirmuseringroup(username=csvrow[1], groupname=groupname)
					if errsev == 0:
						printout(f"\t\t- user {csvrow[1]} confirmed to have membership in Jira group {groupname}.")
					else:
						printout(f"\t\t- cannot confirm user {csvrow[1]} membership in Jira group {groupname} due to error.")
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
