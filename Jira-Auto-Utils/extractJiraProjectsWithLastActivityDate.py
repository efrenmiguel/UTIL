# 

import sys
import csv
from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

#--------------------------------------------

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
				lastupddate = issue.get("fields").get("updated")
			(errorsev, errormsg) = (0, '')
		if errorsev > 0:
			errormsg = "No issues found for project, will assign a blank date."
	except requests.exceptions.HTTPError as errhttp:
		if response.status_code == 400:
			(errorsev, errormsg) = (1, f"STATUS 400 - some problems with the JQL - {jql}.")
		else:
			(errorsev, errormsg) = (2, errhttp)
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as errother:
		(errorsev, errormsg) = (2, errother)
	return (errorsev, errormsg, lastupddate)

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
		(errorsev, errormsg) = (2, errhttp)
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as errother:
		(errorsev, errormsg) = (2, errother)
	return (errorsev, errormsg, projects)


#--------------------------------------------

# receive/set params

# ask me for jira host and my creds
jirahostname = input("\nASKING:  Please enter the Jira hostname: ")
myjirauser = input("\nASKING:  Please enter your Jira Admin user: ")
myjirapwd = getpass("\tPlease enter password: ")

# create and open csv file
date_time = datetime.now().strftime('D%Y%m%d_T%H%M%S')
csvfilename = f"extractJiraProjects_{date_time}.csv"
with open(csvfilename, 'w', newline='') as csvfile:
	csvdata = csv.writer(csvfile, delimiter=",", quotechar="\"")
	
	(errsev, errmsg, allprojects) = getProjects()
	if errsev == 0:

		csvdata.writerow(['projectKey','projectName','projectType','category','leadSSO','leadName','leadStatus','lastIssueUpdate'])

		for index,project in enumerate(allprojects):
			if index > 10:
				exit(1)
			print(f"Processing project {project.get('key')} - {project.get('name')}...")

			lead = project.get("lead")
			category = project.get("projectCategory")

			(errsev, errmsg, lastactdate) = getProjectLastActivity(project.get("key"))
			if errsev == 0:
				lastissueupdate = lastactdate.split("T")[0]
			elif errsev == 2:
				print(F"\t{errmsg}")
			else:
				lastissueupdate = None

			csvrow = []
			csvrow.append(project.get("key"))
			csvrow.append(project.get("name"))
			csvrow.append(project.get("projectTypeKey"))
			if category != None:
				csvrow.append(category.get("name"))
			else:
				csvrow.append(None)
			csvrow.append(lead.get("name"))
			csvrow.append(lead.get("displayName"))
			csvrow.append(lead.get("active"))
			csvrow.append(lastissueupdate)
			
			csvdata.writerow(csvrow)

			print(f"\tProject {project.get('key')} written to CSV file.")

	else:
		print(f"\t{errmsg}")

	csvfile.close()

exit(0)
