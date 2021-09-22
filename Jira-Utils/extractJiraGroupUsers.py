# Extract Jira Group Users and output to CSV file
# To run from Windows command line:
#   > py -3 extractJiraGroupUsers.py

import sys
import csv
from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

#--------------------------------------------

def getGroupUsers(groupname,batchsize,batchstart):
	userbatch = {}
	try:  # call rest api
		response = requests.get(f"https://{jirahostname}/rest/api/latest/group/member", 
			params={'groupname':groupname, 'includeInactiveUsers':'true', 'maxResults':batchsize, 'startAt':batchstart}, 
			auth=HTTPBasicAuth(myjirauser, myjirapwd))
		response.raise_for_status()
		# Code here will only run if the request is successful
		userbatch = response.json()
		(errorsev, errormsg) = (0, '')
	except requests.exceptions.HTTPError as errhttp:
		(errorsev, errormsg) = (1, errhttp)
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as errother:
		(errorsev, errormsg) = (2, errother)
	return (errorsev, errormsg, userbatch)

#--------------------------------------------

# receive/set params

# sef defaults
batchsize = 50

# ask me for jira host and my creds
jirahostname = input("\nASKING:  Please enter the Jira hostname: ")
myjirauser = input("\nASKING:  Please enter your Jira Admin user: ")
myjirapwd = getpass("\tPlease enter password: ")
groupname = input("\nASKING:  Please enter Jira group name: ")

# create and open csv file
date_time = datetime.now().strftime('D%Y%m%d_T%H%M%S')
csvfilename = f"JiraGroupUsers_{groupname.replace(' ','').replace('-','')}_{date_time}.csv"
with open(csvfilename, 'w', newline='') as csvfile:
	csvdata = csv.writer(csvfile, delimiter=",", quotechar="\"")

	# create CSV row with column header cells in the same order as actual data row cells that will be created further below
	csvdata.writerow(['groupName','userKey','userName','displayName','emailAddress','isActive'])

	# extract all Jira Group users
	print(f"\nRUNNING:  Extracting all {groupname} group users...")
	batchstart = 0
	lastbatch = False
	while not(lastbatch):

		# extract users
		print(f"\nRUNNING:  Extracting batch of {batchsize}:{batchstart} users:\n")
		(errsev, errmsg, userbatch) = getGroupUsers(groupname,batchsize,batchstart)
		if errsev > 0:
			print(f"\t\t{errmsg}")
			print(f"\nINTERRUPTED:  Process aborted due to hard failure.")
			exit(1)

		users = userbatch.get('values')
		if users:
			# process users
			print(f"\nRUNNING:  Processing batch of users:\n")
			for idx1,user in enumerate(users):
				print(f"\tProcessing user {user.get('name')} - {user.get('displayName')}...")

				# create CSV row with cells in the same order as column headers created earlier
				csvrow = []
				csvrow.append(groupname)
				csvrow.append(user.get('key'))
				csvrow.append(f"{user.get('name')}")
				csvrow.append(user.get('displayName'))
				csvrow.append(user.get('emailAddress'))
				csvrow.append(user.get('active'))
				csvdata.writerow(csvrow)

		lastbatch = userbatch.get('isLast')
		batchstart += batchsize

	csvfile.close()

exit(0)


