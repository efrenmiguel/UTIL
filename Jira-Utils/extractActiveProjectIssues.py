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

def getProjects():
	projects = {}
	try:  # call rest api
		response = requests.get(f"https://{jirahostname}/rest/api/latest/project", 
			params={'includeArchived':'false', 'expand':'lead'}, auth=HTTPBasicAuth(myjirauser, myjirapwd))
		response.raise_for_status()
		# Code here will only run if the request is successful
		projects = response.json()
		(errorsev, errormsg) = (0, '')
	except requests.exceptions.HTTPError as errhttp:
		(errorsev, errormsg) = (1, errhttp)
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as errother:
		(errorsev, errormsg) = (2, errother)
	return (errorsev, errormsg, projects)

def getProjectLastActivity(projkey):
	lastupddate = ""
	try:  # call rest api
		jql = f"project = {projkey} ORDER BY updated DESC"
		response = requests.get(f"https://{jirahostname}/rest/api/latest/search", 
			params={'jql':jql, 'maxResults':'1', 'fields':'updated'}, auth=HTTPBasicAuth(myjirauser, myjirapwd))
		response.raise_for_status()
		# Code here will only run if the request is successful
		errorsev = 1
		for issue in response.json()["issues"]:
			if "fields" in issue:
				fields = issue.get("fields")
				if "updated" in fields:
					lastupddate = fields.get("updated").split("T")[0]
					(errorsev, errormsg) = (0, '')
		if errorsev > 0:
			(errormsg, lastupddate) = ("No issues found for project, will assign a blank date.","(no issues found)")
	except requests.exceptions.HTTPError as errhttp:
		if response.status_code == 400:
			(errorsev, errormsg, lastupddate) = (1, f"STATUS 400 - JQL or project permission issue.","(no permission)")
		else:
			(errorsev, errormsg) = (2, errhttp)
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as errother:
		(errorsev, errormsg) = (2, errother)
	return (errorsev, errormsg, lastupddate)

def getProjectPermissionScheme(projkey):
	projpermscheme = {}
	try:  # call rest api
		response = requests.get(f"https://{jirahostname}/rest/api/latest/project/{projkey}/permissionscheme", 
			auth=HTTPBasicAuth(myjirauser, myjirapwd))
		response.raise_for_status()
		# Code here will only run if the request is successful
		projpermscheme = response.json()
		(errorsev, errormsg) = (0, '')
	except requests.exceptions.HTTPError as errhttp:
		(errorsev, errormsg) = (1, errhttp)
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as errother:
		(errorsev, errormsg) = (2, errother)
	return (errorsev, errormsg, projpermscheme)

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
	csvfilename = f"{outputdir}/JiraProjects_{date_time}.csv"
else:
	csvfilename = f"JiraProjects_{date_time}.csv"
with open(csvfilename, "w", encoding="utf-8", newline="") as csvfile:
	csvdata = csv.writer(csvfile, delimiter=",", quotechar="\"")

	# extract all Jira projects
	print(F"\nRUNNING:  Extracting all projects...")
	(errsev, errmsg, allprojects) = getProjects()
	if errsev == 0:

		# create CSV row with column header cells in the same order as actual data row cells that will be created further below
		csvdata.writerow(['projectKey','projectName','projectType','category','lastIssueUpdate','leadUserName','permissionScheme'])

		# process extracted projects
		print(F"\nRUNNING:  Processing extracted projects:\n")
		ignoreproject = True
		for index,project in enumerate(allprojects):

			if not(ignoreproject) or not(startingprojkey) or project.get('key') == startingprojkey:
				ignoreproject = False

				print(f"\tProcessing project {project.get('key')} - {project.get('name')}...")

				lead = project.get("lead")
				category = project.get("projectCategory")

				# get project last issue update date
				(errsev, errmsg, lastissueupdate) = getProjectLastActivity(project.get("key"))
				if errsev > 0:
					print(F"\t\t{errmsg}")
					if errsev > 1:
						print(F"\nINTERRUPTED:  Process aborted due to hard failure.")
						exit(1)

				# skip inactive projects (< 1/1/2021)

					# get project permission scheme
					(errsev, errmsg, projpermscheme) = getProjectPermissionScheme(project.get("key"))
					if errsev > 0:
						print(F"\t\t{errmsg}")
						if errsev > 1:
							print(F"\nINTERRUPTED:  Process aborted due to hard failure.")
							exit(1)

					# skip archived projects


						# get project issues
						


				# create CSV row with cells in the same order as column headers created earlier
				csvrow = []
				csvrow.append(project.get("key"))
				csvrow.append(project.get("name"))
				csvrow.append(project.get("projectTypeKey"))
				if category != None:
					csvrow.append(category.get("name"))
				else:
					csvrow.append(None)
				csvrow.append(lastissueupdate)
				csvrow.append(lead.get("name"))
				csvrow.append(projpermscheme.get("name"))
				csvdata.writerow(csvrow)

				print(f"\t\tProject {project.get('key')} written to CSV file.")

			else:
				print(f"\tIgnoring project {project.get('key')} - {project.get('name')}...")

	else:
		print(f"\t{errmsg}")
		print(F"\nINTERRUPTED:  Process aborted due to hard failure.")

	csvfile.close()

exit(0)

