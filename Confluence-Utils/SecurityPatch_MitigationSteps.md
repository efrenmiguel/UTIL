# Mitigation

If you are unable to upgrade Confluence immediately, then as a temporary workaround, you can mitigate the issue by running the script below for the Operating System that Confluence is hosted on.

Important: If you run Confluence in a cluster, you will need to repeat this process on each node. You don't need to shut down the whole cluster. 

### 1. Shut down Confluence. 
	 
	
### 2. Download the cve-2021-26084-update.sh to the Confluence Linux Server.

### 3. Edit the cve-2021-26084-update.sh file and set INSTALLATION_DIRECTORY to your Confluence installation directory 

- For example: 

	INSTALLATION_DIRECTORY=/opt/atlassian/confluence
	
	Save the file.
	
### 4. Give the script execute permission.

- Run the command:
	```batch
		chmod 700 cve-2021-26084-update.sh
	```
	
### 5. Change to the Linux user that owns the files in the Confluence Installation directory, for example:
	
	$ ls -l /opt/atlassian/confluence | grep bin
	drwxr-xr-x 3 root root 4096 Aug 18 17:07 bin
 
	In this first example, we change to the 'root' user to run the workaround script:
	
	$ sudo su root
	
	
	
$ ls -l /opt/atlassian/confluence | grep bin
drwxr-xr-x 3 confluence confluence 4096 Aug 18 17:07 bin
# In this second example, we need to change to the 'confluence' user 
# to run the workaround script
$ sudo su confluence
	
	
	
	
Run the workaround script.

	
	
$ ./cve-2021-26084-update.sh
	
	
	
	
The expected output should confirm up to five files updated and end with:

	
	
Update completed!
	
	
The number of files updated will differ, depending on your Confluence version.
	 
	
	
	
Restart Confluence.
	


Remember, If you run Confluence in a cluster, make sure you run this script on all of your nodes.