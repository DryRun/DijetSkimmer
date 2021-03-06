import os
from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config, getUsernameFromSiteDB

config = Configuration()
job_name = "DijetSkim_DATASET_YEAR_VERSION"

config.section_("General")
config.General.requestName = job_name
config.General.transferLogs = False
config.section_("JobType")
config.JobType.pluginName = 'Analysis'

# Setup the custom executable
config.JobType.psetName = os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/skim/PSet.py') # CRAB modifies this file to contain the input files and lumis
config.JobType.scriptExe = os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/skim/crab_shell.sh') # CRAB then calls scriptExe jobId <scriptArgs>
config.JobType.scriptArgs = []
config.JobType.inputFiles = [
	os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/skim/crab_meat.py'), 
	os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/NanoAODTools/scripts/haddnano.py'), #hadd nano will not be needed once nano tools are in cmssw
	os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/skim/skim_branches_data.txt'),
	os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/skim/skim_branches_mc.txt'),
	os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/skim/skim_branches.txt'),
	#os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/skim/FrameworkJobReport.xml'),
	]
config.JobType.outputFiles = ["nanoskim.root", "hists.root"]
config.JobType.sendPythonFolder	 = True
config.JobType.allowUndistributedCMSSW = True
config.section_("Data")
#config.Data.inputDBS = 'phys03'
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
#config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 4
#config.Data.totalUnits = 4
config.JobType.allowUndistributedCMSSW = True
config.Data.outLFNDirBase = '/store/user/{}/DijetNanoSkim/VERSION/YEAR/'.format(getUsernameFromSiteDB())
config.Data.publication = False
config.Data.outputDatasetTag = "DATASET"
#config.Data.ignoreLocality = True

config.section_("Site")
config.Site.storageSite = "T3_US_Brown"
