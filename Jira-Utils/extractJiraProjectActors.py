# Extract Jira project actors and output to CSV file
# To run from Windows command line:
#   > py -3 extractJiraProjectActors.py

import sys
import csv
from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

#--------------------------------------------

def getProjects():
	projects = {}
	try:  # call rest api
		response = requests.get(f"https://{jirahostname}/rest/api/latest/project", 
			params={'includeArchived':'false'}, auth=HTTPBasicAuth(myjirauser, myjirapwd))
		response.raise_for_status()
		# Code here will only run if the request is successful
		projects = response.json()
		(errorsev, errormsg) = (0, '')
	except requests.exceptions.HTTPError as errhttp:
		(errorsev, errormsg) = (1, errhttp)
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as errother:
		(errorsev, errormsg) = (2, errother)
	return (errorsev, errormsg, projects)

def getProjectRoles(projkey):
	projroles = {}
	try:  # call rest api
		response = requests.get(f"https://{jirahostname}/rest/api/latest/project/{projkey}/role", 
			auth=HTTPBasicAuth(myjirauser, myjirapwd))
		response.raise_for_status()
		# Code here will only run if the request is successful
		projroles = response.json()
		(errorsev, errormsg) = (0, '')
	except requests.exceptions.HTTPError as errhttp:
		(errorsev, errormsg) = (1, errhttp)
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as errother:
		(errorsev, errormsg) = (2, errother)
	return (errorsev, errormsg, projroles)

def getProjectRoleData(projroleurl):
	roledata = {}
	try:  # call rest api
		response = requests.get(projroleurl, 
			auth=HTTPBasicAuth(myjirauser, myjirapwd))
		response.raise_for_status()
		# Code here will only run if the request is successful
		roledata = response.json()
		(errorsev, errormsg) = (0, '')
	except requests.exceptions.HTTPError as errhttp:
		(errorsev, errormsg) = (1, errhttp)
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as errother:
		(errorsev, errormsg) = (2, errother)
	return (errorsev, errormsg, roledata)


#--------------------------------------------

# receive/set params

# ask me for jira host and my creds
jirahostname = input("\nASKING:  Please enter the Jira hostname: ")
myjirauser = input("\nASKING:  Please enter your Jira Admin user: ")
myjirapwd = getpass("\tPlease enter password: ")
startingprojkey = input("\nASKING:  Please enter the starting Project Key (leave empty otherwise): ")
outputdir = input("\nASKING:  Please enter the directory for the output CSV file: ")

# create and open csv file
date_time = datetime.now().strftime('D%Y%m%d_T%H%M%S')
if outputdir:
	csvfilename = f"{outputdir}/JiraProjectActors_{date_time}.csv"
else:
	csvfilename = f"JiraProjectActors_{date_time}.csv"
with open(csvfilename, "w", encoding="utf-8", newline="") as csvfile:
	csvdata = csv.writer(csvfile, delimiter=",", quotechar="\"")

	# extract all Jira projects
	print(F"\nRUNNING:  Extracting all projects...")
	(errsev, errmsg, allprojects) = getProjects()
	if errsev == 0:

		# create CSV row with column header cells in the same order as actual data row cells that will be created further below
		csvdata.writerow(['projectKey','roleId','roleName','actorName','actorDisplayName'])

		# process extracted projects
		print(F"\nRUNNING:  Processing extracted projects:\n")
		ignoreproject = True
		for idx1,project in enumerate(allprojects):
			print(f"\tProcessing project {project.get('key')} - {project.get('name')}...")

			if not(ignoreproject) or not(startingprojkey) or project.get('key') == startingprojkey:
				ignoreproject = False

				# get project roles
				(errsev, errmsg, projroles) = getProjectRoles(project.get("key"))
				if errsev > 0:
					print(F"\t\t{errmsg}")
					if errsev > 1:
						print(F"\nINTERRUPTED:  Process aborted due to hard failure.")
						exit(1)

				# process extracted project roles
				print(F"\n\t\tRUNNING:  Processing extracted project roles:\n")
				for rolekey in projroles:
					print(f"\t\tProcessing role {rolekey} - {projroles.get(rolekey)}...")

					# get role
					(errsev, errmsg, roledata) = getProjectRoleData(projroles.get(rolekey))
					if errsev > 0:
						print(F"\t\t{errmsg}")
						if errsev > 1:
							print(f"\nINTERRUPTED:  Process aborted due to hard failure.")
							exit(1)

					# process extracted project role actors
					roleactors = roledata.get('actors')
					print(F"\n\t\t\tRUNNING:  Processing extracted project role actors:\n")
					for idx2,actor in enumerate(roleactors):
						print(f"\t\t\tProcessing actor ({actor.get('name')}) {actor.get('displayName')}...")

						# create CSV row with cells in the same order as column headers created earlier
						csvrow = []
						csvrow.append(project.get('key'))
						csvrow.append(roledata.get('id'))
						csvrow.append(roledata.get('name'))
						csvrow.append(actor.get('name'))
						csvrow.append(actor.get('displayName'))
						csvdata.writerow(csvrow)

			else:
				print(f"\tIgnoring project {project.get('key')} - {project.get('name')}...")

	else:
		print(f"\t{errmsg}")
		print(f"\nINTERRUPTED:  Process aborted due to hard failure.")

	csvfile.close()

exit(0)


