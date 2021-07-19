# Remove Jira Users From Groups

This utility Python script can help to bulk-remove Jira users exported from Jira using the myUserManagerForJira Plug-in app, from specific Jira user groups - **jira-users** and **jira-servicedesk-users**.

---
## 1. Pre-requisites

This script is tested with Python 3.95 on Windows 10, and uses the **Requests** python module.

### 1.1. Install Python

Please install the latest version of Python 3 as follows:

- In your browser, go to https://www.python.org/downloads/
- Hover on the *Downloads* menu, hover on *Windows*, then click on the *Python 3.x* download button.
- Follow prompts to complete installation 
- Check from Windows command line:
	```PowerShell
	> py -3 --version
	Python 3.9.5
	```

### 1.2. Install Requests Python Module

The **requests** Python module helps simplify executing HTTP Client tasks in Python, to install this module:

- From the Windows command line: 
	```PowerShell
	> py -3 -m install requests
	```

### 1.3. Deploy Script

- Get a copy of the `removeJiraUsersFromGroup.py` Python script.
- Create a working folder and place the script in there.

---
## 2. Run Update Process

### 2.1. Extract Jira Users

This script will only work with users in a CSV file exported by the *myUserManagerForJira* Plug-in app in Jira, at least in current layout of its CSV Export file.

- Make sure you have the **myUserManagerForJira** Plug-in installed and activated.
- Go to ***User Management*** tab in the Jira dashboard.
- Under *My User Manager* side menu section, click on ***Filter Users***.
- Enter the following *Search* criteria:
	- *Last login since (in days)* - enter the desired idle aging number of days, enter `90` to include users that has not logged-in in the last 3 months.
	- *In Groups* - enter `jira-users, jira-servicedesk-users`
	- *User Status* - select `Idle`, then also select `Never logged in`.
	- Leave other Search fields as blanks.
- Click on the ***Search*** button.  
	- This can take a few seconds or minutes to run.
	- Watch for the *Showing users 1 to 10 of n* text on dashboard, it's complete when n changes to a new value.
	- Do visual validation on the number of canditate users, and some sample users to make sure you have the right set of target users.
- Click on ***Export to CSV*** just above the graphic section on the same page.
- Save the CSV file on the work folder you placed the Python script earlier.
	The CSV file should have the following format:
	```PowerShell
	> Get-Content jirastg_idleusers_20210623.csv -Head 5
	fullname,username,email,status,lastLogin,groups,directory
	"Valentin, Paul","100026433","paul.valentin@nbcuni.com","Never logged in","","jira-users","Active Directory server",
	"Kochugova, Oksana","101019913","OKochugova@cnbc.com","Idle","02.10.2020 05:34:27 - since 265 days","jira-users","Active Directory server",
	"AMANI, Steve","121005472","steve.amani@nbcuni.com","Idle","31.12.2018 18:57:17 - since 905 days","jira-users","Active Directory server",
	"Hill, Richard","127000187","richard.hill@nbcuni.com","Idle","06.08.2019 06:34:24 - since 688 days","jira-users","Active Directory server",
	```

### 2.2. Run Script

Before running the script, make sure that your Jira user/SSO has Jira Admin permissions, you will be prompted to enter that username and password.

- In the command line, go to your working folder.

- Check to make sure you have your script and input file ready.
	```PowerShell
	> cd C:\jirawork

	C:\jirawork> dir

	Mode                LastWriteTime         Length Name
	----                -------------         ------ ----
	-a---l        6/28/2021   8:26 AM         427268 jirastg_idleusers_20210623.csv
	-a---l        6/28/2021   8:33 AM           4204 removeJiraUsersFromGroup.py
	```

- Now run the script:

	Please note that the script will give you a chance to process input records in batches, you can even process just a couple of records first to validate before running bigger groups of records. Also, the script generates a log file, everything that is printed on the console except for the user prompts, is also written to the log file.

	To run the script, enter the following from the command line:
	```PowerShell
	C:\jirawork> py -3 removeJiraUsersFromGroup.py '{csv_filename}'
	```
	Follow the prompts shown as follows:
	- Jira hostname - for Staging, enter `jirastg.inbcu.com`
		```PowerShell
		ASKING:  Please enter the Jira hostname: jirastg.inbcu.com
		```
	- Jira Admin credentials - enter your SSO and password
		```PowerShell
		ASKING:  Please enter your Jira Admin user: 987654321
			Please enter password:
		```
	- Records to process - enter the number of input records to process, you might want to start with a very small number.
		```PowerShell
		ASKING:  How many rows do you want to process next, 3017 remaining? Enter 0 to quit: 3

		RUNNING:  Processing next 3 rows out of 3017 remaining...
			Column header row:
				- IGNORED
			Jira user 100026433 paul.valentin@nbcuni.com (Never logged in):
				- user 100026433 successfully removed from Jira group jira-users.
			Jira user 101019913 OKochugova@cnbc.com (Never logged inIdle for last 265 days):
				- user 101019913 successfully removed from Jira group jira-users.
		```
	- (NEXT) Records to process - you will be prompted again after the number of records is processed, you might want to consider processing in groups of 100-500 input records, it could take about 1 min to process a group of 100 records. If you want to discontinue, just enter `0` at this prompt. 
		```PowerShell
		ASKING:  How many rows do you want to process next, 3014 remaining? Enter 0 to quit: 0

		INTERRUPTED:  Process aborted, 3014 rows remain unprocessed.
		```

- Log File
	Every time you run the script, a new log file is created where all logs and errors are written. In the same working directory, look for a files that are named like `removeJiraUsersFromGroup_D20210625_T184913.log`


## 3. Source Code

- The following is the current source code for the Python script:

	`removeJiraUsersFromGroup.py`:
	```python
	# Remove Jira users from jira-users and jira-servicedesk-users group with CSV SSO list
	#   CSV file must be in the format exported by the myUserManagerForJira plug-in app
	# To run from Windows command line:
	#   > py -3 removeJiraUsersFromGroup.py '{input-csv-filename}'

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
	outfile = open(f"removeJiraUsersFromGroup_{date_time}.log", "a")

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
	```