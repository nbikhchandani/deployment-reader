import os
import re
import sys
import glob
import collections
import csv

class DeploymentStatsReader:
	def __init__(self):
		self.summaryFileNameStartPattern = "WadiSummaryFile-Current*"
		self.blacklistSet = {"StartTime"}
		self.deploymentActivities = ["DeployFilesToStorage", "DeployDatabase", "DeployDatabaseBootStrap", "ProvisionRegions" , "DeployMetadataService", "DeployInfraService", "DeployInfraDatabase"]
		self.allActivitiesAvg = []
		
	def readStats(self, buildPath):
		file = glob.glob(buildPath)
		result = False
		activities = collections.OrderedDict()
		if file:
			result = True
			print "Reading File:" , file
			fileReader = open(file[0], 'rb').read()
			fileText = fileReader.decode('utf-16')
			fileText = fileText.encode('ascii', 'ignore')
			for line in fileText.splitlines():
				for activity in self.deploymentActivities:
					if activity in line:
						if "Succeeded" in line:
							value = re.findall(r'<font color="red">(.*?)</font>', line)
							values = []
							if activities.has_key(activity):
								values = activities[activity]
							values.append(value[0])
							activities[activity] = values
		else:
			result = False
		return activities

	def getAverages(self, activities):
		activitiesAvg = collections.OrderedDict()
		for i, (key, value) in enumerate(activities.iteritems()):
			sum = 0.0
			for val in value:
				sum += float(val)
			activitiesAvg[key] = sum/len(value)
		print "Activities Average: " , activitiesAvg
		if activitiesAvg:
			self.allActivitiesAvg.append(activitiesAvg)

	def writeToFile(self):
		print "All activities averages: ", self.allActivitiesAvg 
		with open('spreadsheet.csv', 'w') as outfile:
			fp = csv.DictWriter(outfile, self.allActivitiesAvg[0].keys())
			fp.writeheader()
			fp.writerows(self.allActivitiesAvg)
		

def get_immediate_subdirectories(a_dir):
  return [name for name in os.listdir(a_dir)
    if os.path.isdir(os.path.join(a_dir, name))]

buildPath = "//BLD-FS-HD-M1-01/TFS/HDI/HDI-Curr-BuildAndDeploy/"
get_immediate_subdirectories(buildPath)
i=0
deploymentStatsReader = DeploymentStatsReader()
for subdir in get_immediate_subdirectories(buildPath):
	if i==25:
		break
	i+=1
	dir = os.path.join(buildPath, subdir)
	#fullBuildPath = dir + "/" + deploymentStatsReader.summaryFileNameStartPattern
	fullBuildPath = os.path.join(dir, deploymentStatsReader.summaryFileNameStartPattern)
	#fullBuildPath = "//BLD-FS-HD-M1-01/TFS/HDI/HDI-Curr-BuildAndDeploy/20160505.3/WadiSummaryFile-Current*"
	print "fullbuildpath", fullBuildPath
	activityValues = deploymentStatsReader.readStats(fullBuildPath)
	print "Activity Values", activityValues
	if activityValues is not None:
		deploymentStatsReader.getAverages(activityValues)
deploymentStatsReader.writeToFile()
