# Extract Jira projects, and include Project lead user info
#   as well as Project Last Issue Update date, and creates CSV file
# To run from Windows command line:
#   > py -3 extractJiraProjectsWithLastActivityDate.py

import sys
import csv
from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

#--------------------------------------------

def getPermissionSchemes():
	schemes = {}
	try:  # call rest api
		response = requests.get(f"https://{jirahostname}/rest/api/latest/permissionscheme",
			params={'expand':'projectRole'}, auth=HTTPBasicAuth(myjirauser, myjirapwd))
		response.raise_for_status()
		# Code here will only run if the request is successful
		schemes = response.json()
		(errorsev, errormsg) = (0, '')
	except requests.exceptions.HTTPError as errhttp:
		(errorsev, errormsg) = (1, errhttp)
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as errother:
		(errorsev, errormsg) = (2, errother)
	return (errorsev, errormsg, schemes)

#--------------------------------------------

# receive/set params

# ask me for jira host and my creds
jirahostname = input("\nASKING:  Please enter the Jira hostname: ")
myjirauser = input("\nASKING:  Please enter your Jira Admin user: ")
myjirapwd = getpass("\tPlease enter password: ")
outputdir = input("\nASKING:  Please enter the directory for the output CSV file: ")

# create and open csv file
date_time = datetime.now().strftime('D%Y%m%d_T%H%M%S')
if outputdir:
	csvfilename = f"{outputdir}/JiraPermissionSchemeRoles_{date_time}.csv"
else:
	csvfilename = f"JiraPermissionSchemeRoles_{date_time}.csv"
with open(csvfilename, "w", encoding="utf-8", newline="") as csvfile:
	csvdata = csv.writer(csvfile, delimiter=",", quotechar="\"")

	# extract all Jira projects
	print(F"\nRUNNING:  Extracting all Permission Scheme Roles...")
	(errsev, errmsg, schemedata) = getPermissionSchemes()
	if errsev == 0:

		# create CSV row with column header cells in the same order as actual data row cells that will be created further below
		csvdata.writerow(['permSchemeId','permSchemeName','permSchemeDesc','permId','permission','permHolderType','projectRoleId','projectRoleName','projectRoleDesc'])

		# process extracted projects
		print(F"\nRUNNING:  Processing extracted Permission Scheme Roles:\n")
		schemes = schemedata.get("permissionSchemes")
		for index1,scheme in enumerate(schemes):

			print(f"\tProcessing Permission Scheme {scheme.get('name')} - {scheme.get('description')}...")
			permissions = scheme.get('permissions')
			for index2,permission in enumerate(permissions):

				# create CSV row with cells in the same order as column headers created earlier
				csvrow = []
				csvrow.append(scheme.get("id"))
				csvrow.append(scheme.get("name"))
				csvrow.append(scheme.get("description"))

				csvrow.append(permission.get("id"))
				csvrow.append(permission.get("permission"))

				holder = permission.get("holder")
				csvrow.append(holder.get("type"))

				if holder.get('type') == "projectRole":
					role = holder.get('projectRole')
					csvrow.append(role.get("id"))
					csvrow.append(role.get("name"))
					csvrow.append(role.get("description"))
				else:
					csvrow.append(None)
					csvrow.append(None)
					csvrow.append(None)

				csvdata.writerow(csvrow)

	else:
		print(f"\t{errmsg}")
		print(F"\nINTERRUPTED:  Process aborted due to hard failure.")

	csvfile.close()

exit(0)

