# Remove Jira users from jira-users and jira-servicedesk-users group with CSV SSO list
#   CSV file must be in the format exported by the myUserManagerForJira plug-in app
# To run from Windows command line:
#   > py -3 remove-jira-user-from-group.py '{input-csv-filename}'

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
# targetgroups = ["jira-users", "jira-servicedesk-users"]
# targetstatus = ["Never logged in", "Idle", "Inactive"]

# create and open log file
date_time = datetime.now().strftime('D%Y%m%d_T%H%M%S')
outfile = open(f"revokeUserJiraLicense_{date_time}.log", "a")

# ask me for jira host and my creds
jirahostname = input("\nASKING:  Please enter the Jira hostname: ")
myjirauser = input("\nASKING:  Please enter your Jira Admin user: ")
myjirapwd = getpass("\tPlease enter password: ")
csvfilename = input("\nASKING:  Please enter your Users CSV filename \n(Note that CSV data should usernames in column 1 and no column headers): ")
revokesoftlic = input("\nASKING:  Do you want to revoke Jira \"Software\" licenses for these users?: ")
if revokesoftlic in ['yes', 'Yes', 'YES']:
	revokejsdlic = "yes"
	confirmrevoke = input("\nASKING:  Are you sure you want to remove these users from \n\tthe jira-users and jira-servicedesk-users groups?: ")
	if not confirmrevoke in ['yes', 'Yes', 'YES']:
		printout(f"\nINTERRUPTED:  Please make up your mind, process aborted.\n")
		exit(1)
else:
	revokejsdlic = input("\nASKING:  Do you want to revoke only \"Jira Service Desk\" licenses for these users?: ")
	if revokejsdlic in ['yes', 'Yes', 'YES']:
		confirmrevoke = input("\nASKING:  Are you sure you want to remove these users from \n\tthe jira-servicedesk-users group?: ")
		if not confirmrevoke in ['yes', 'Yes', 'YES']:
			printout(f"\nINTERRUPTED:  Please make up your mind, process aborted.\n")
			exit(1)

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

		username = csvrow[0]
		if revokejsdlic in ['yes', 'Yes', 'YES']:
				# execute method to remove user from jira-servicedesk-users group
				groupname = "jira-servicedesk-users"
				(errsev, errmsg) = removeuserfromgroup(username,groupname)
				if errsev == 0:
					printout(f"\t\t- user {username} successfully removed from Jira group {groupname}.")
				else:
					printout(f"\t\t- user {username} NOT removed from Jira group {groupname} due to error.")
					printout(f"\t\t\t{errmsg}")
					if errsev > 1:
						printout(f"\nINTERRUPTED:  Process aborted due to hard failure, {(totrows-csvidx)} rows remain unprocessed.\n")
						exit(1)

		if revokesoftlic in ['yes', 'Yes', 'YES']:
				# execute method to remove user from jira-servicedesk-users group
				groupname = "jira-users"
				(errsev, errmsg) = removeuserfromgroup(username,groupname)
				if errsev == 0:
					printout(f"\t\t- user {username} successfully removed from Jira group {groupname}.")
				else:
					printout(f"\t\t- user {username} NOT removed from Jira group {groupname} due to error.")
					printout(f"\t\t\t{errmsg}")
					if errsev > 1:
						printout(f"\nINTERRUPTED:  Process aborted due to hard failure, {(totrows-csvidx)} rows remain unprocessed.\n")
						exit(1)

		nextrowcount -= 1
	
	csvfile.close()

printout(f"\nDONE:  Finished processing {(totrows)} total rows.\n")
outfile.close()
exit(0)
