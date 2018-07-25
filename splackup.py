import requests
import xml.dom.minidom
import os
import urllib2
import re

####################################################################################################################
#    Backup Splunk cloud to local disk (then to git ;). Need to ensure the connection details are correct for your 
#    environment - look for the CHANGE HERE tag below. 
#    Copyright (C) 2018 Paddy Power Betfair
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
# 
####################################################################################################################
# 1.0 - Initial release - grant.mitchell@paddypowerbetfair.com
####################################################################################################################
# Want to help us develop best in breed solutions? Check out:
# https://paddypowerbetfair.jobs/jobs/?search=sre
####################################################################################################################



def mkdir(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)

def getLinks(connection,location,done,ignore,kbEntries):
	mkdir(location)
	try:
		page=0
		pageSize=50
		getPage=True
		while getPage:
			params={"count":pageSize,"offset":page*pageSize}
			print "GET: "+connection["baseUrl"]+location+"?"+"count="+str(pageSize)+"&offset="+str(page*pageSize)+" -> Done: "+str(len(done))
			start=connection["session"].get(url=connection["baseUrl"]+location, timeout=60,
											params=params,auth=(connection["user"],connection["passwd"]),verify=False).content
			start=re.sub(r"<updated>.*?<\/updated>","",start) # Cause we're going to git, we remove these as they will change
			start=re.sub(r"<s:key name=\"next_scheduled_time\">.*?</s:key>","",start) # and we want this to be clean.
			if start.startswith("<?xml") and not start.lower()=="internal rest handler error":
				xmlData = xml.dom.minidom.parseString(start)
				if xmlData.getElementsByTagName("opensearch:totalResults"):
					searchSize=int(xmlData.getElementsByTagName("opensearch:totalResults")[0].firstChild.wholeText)
					offset=int(xmlData.getElementsByTagName("opensearch:startIndex")[0].firstChild.wholeText)
				else:
					searchSize=0
					offset=0
				if searchSize==1: # By default we only will save single elements, not lists
					fh=open(location+"/object-"+str(page)+".xml","w")
					fh.write(start)
					fh.close()
				if offset+pageSize>=searchSize:
					getPage=False
				else:
					page=page+1
				for link in xmlData.getElementsByTagName("link"):
					thing=urllib2.unquote(link.getAttribute("href")[1:])
					if link.getAttribute("rel") in ["list","alternate"]:
						inIgnore=False
						for item in ignore:
							if thing.startswith(item):
								inIgnore=True
					else:
						inIgnore=True
					if not thing in done and not inIgnore:
						done.append(thing)
						done=getLinks(connection,thing,done,ignore,kbEntries)
						# Get round annoying splunk bug that doesn't pull it all back :(
						if location=="services/apps/local":
							hack=thing.replace("servicesNS/nobody/system/apps/local/","servicesNS/nobody/")
							for entry in kbEntries:
								want=hack+"/admin"+entry
								if not want in done:
									done.append(want)
									done=getLinks(connection,want,done,ignore,kbEntries)
			else:
				fh=open(location+"/object.txt","w")
				fh.write(start)
				fh.close()
				getPage=False
		return done
	except Exception as e:
		print "oops!"
		print e
		return done

def main():
	# What elements we'll pull back for app elements:
	kbEntries=["/views","/eventtypes","/transforms-extract","/transforms-lookups","/fvtags",
					"/tags","/sourcetypes","/alert_overlay","/workflow-actions",
					"/savedsearch","/props-eval","/props-lookup","/datamodel-files",
					"/props-extract","/nav","/ntags","/datasets","/datamodelpivot",
					"/macros","/fields","/fieldaliases","/lookup-table-files"]
	# What starting points we'll process:
	startingPoints=["/apps/local","/admin"]
	# These are branches of the tree we're not interested in traversing:
	ignoreBranches=["services/admin/file-explorer","services/admin/httpauth-tokens","services/admin/quota-usage","services/admin/introspection",
					"services/admin/distsearch","services/admin/ma-apps","services/admin/sh_sourcetypes_manager",
					"services/admin/sh_indexes_manager","services/admin/directory","services/admin/shclustermemberartifacts",
					"services/admin/search-distributedmetrics"]
	connection={ # CHANGE HERE - Change these values to match your environment.
		"baseUrl": "https://mysplunk.splunkcloud.com:8089/",
		"user": "admin",
		"passwd": "changeme"
	} # CHANGE HERE - Change these values to match your environment.
	session=requests.Session()
	adapt=requests.adapters.HTTPAdapter(max_retries=3)
	session.mount('https://', adapt)
	connection["session"]=session
	done=[]
	for startingPoint in startingPoints:
		mkdir("services"+startingPoint)
		done=getLinks(connection,"services"+startingPoint,done,ignoreBranches,kbEntries)


if __name__ == "__main__":
    main()

