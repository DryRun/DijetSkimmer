import os
import sys
from CRABClient.UserUtilities import config, ClientException, getUsernameFromCRIC
from PhysicsTools.DijetSkimmer.skim_version import skim_version
#from input_crab_data import dataset_files
import yaml
import datetime
from fnmatch import fnmatch
from argparse import ArgumentParser

#production_tag = datetime.datetime.now().strftime("%Y%b%d") # -%H-%M #datetime.date.today().strftime('%Y%b%d-%H%M')
production_tag = skim_version
#production_tag = "2020Dec15"

if __name__ == '__main__':

    from CRABAPI.RawCommand import crabCommand
    from CRABClient.ClientExceptions import ClientException
    from httplib import HTTPException
    from multiprocessing import Process

    def submit(config):
            try:
                crabCommand('submit', config=config)
            except HTTPException as hte:
                print "Failed submitting task: %s" % (hte.headers)
                print hte
            except ClientException as cle:
                print "Failed submitting task: %s" % (cle)

    parser = ArgumentParser()
    parser.add_argument('-y', '--yaml', default = 'samples_data.yaml', help = 'File with dataset descriptions')
    args = parser.parse_args()

    with open(args.yaml) as f:
        doc = yaml.load(f) # Parse YAML file
        defaults = doc['defaults'] if 'defaults' in doc else {}
        isMC = defaults.get("isMC")
        
        # loop over samples
        #for sample, info in doc['samples'].iteritems():
        for sample in sorted(doc["samples"].keys()):
            info = doc["samples"][sample]
            print("\n\n*** Sample {} ***".format(sample))
            year = info["year"]

            #for name, dataset in info['datasets'].iteritems():            
            for name in sorted(info["datasets"].keys()):
                dataset = info["datasets"][name]
                print("Submitting {}".format(name))

                reco_version = info.get("reco_version",
                                        defaults.get("reco_version", None))
                if reco_version == "UL":
                    production_tag = "{}_UL".format(skim_version)
                else:
                    production_tag = skim_version

                this_config = config()

                this_config.section_('General')
                this_config.General.transferOutputs = True
                this_config.General.transferLogs = True
                this_config.General.workArea = 'DijetSkim/{}/{}'.format(production_tag, year)
                this_config.General.requestName = "DijetSkim_{}".format(name)


                this_config.section_('JobType')
                this_config.JobType.pluginName = 'Analysis'
                this_config.JobType.psetName = os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/production/PSet.py') # CRAB modifies this file to contain the input files and lumis
                this_config.JobType.scriptExe = os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/production/crab_shell.sh') # CRAB then calls scriptExe jobId <scriptArgs>
                this_config.JobType.inputFiles = [
                    os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/production/crab_meat.py'), 
                    os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/NanoAODTools/scripts/haddnano.py'), #hadd nano will not be needed once nano tools are in cmssw
                    os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/production/skim_branches_data.txt'),
                    os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/production/skim_branches_mc.txt'),
                    os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/production/skim_branches.txt'),
                    #os.path.expandvars('$CMSSW_BASE/src/PhysicsTools/DijetSkimmer/production/FrameworkJobReport.xml'),
                    ]
                this_config.JobType.scriptArgs = ["--source={}".format("mc" if isMC else "data"), 
                                             "--year={}".format(info["year"])]
                if not isMC:
                    if "JetHT" in sample:
                        this_config.JobType.scriptArgs.append("--dataset=JetHT")
                    elif "SingleMuon" in sample:
                        this_config.JobType.scriptArgs.append("--dataset=SingleMuon")
                    else:
                        raise ValueError("I don't know what dataset (JetHT or SingleMuon) corresponds to the specified sample: {}".format(sample))
                this_config.JobType.maxJobRuntimeMin = 2750
                this_config.JobType.outputFiles = ["nanoskim.root", "hists.root"]
                #this_config.JobType.outputFiles = ['_'.join(['DijetSkim', 'mc' if isMC else 'data', production_tag])+'.root']
                this_config.JobType.sendPythonFolder  = True
                this_config.JobType.allowUndistributedCMSSW = True
                globaltag = info.get(
                        'globaltag',
                        defaults.get('globaltag', None)
                )
                
                this_config.JobType.pyCfgParams = [
                        'isMC=%s' % isMC, 'reportEvery=1000',
                        'tag=%s' % production_tag,
                        'globalTag=%s' % globaltag,
                ]


                this_config.section_('User')
                this_config.section_('Site')
                this_config.Site.storageSite = 'T3_US_Brown'


                this_config.section_('Data')
                this_config.Data.publication = False
                this_config.Data.outLFNDirBase = '/store/user/{username}/DijetSkim/{production_tag}/{sample}'.format(
                                                    username=getUsernameFromCRIC(), 
                                                    production_tag=production_tag,
                                                    sample=sample)
                this_config.Data.outputDatasetTag = name
                # Outputs land at /store/user/dryu/DijetSkim/vX_Y_Z/sample/subsample
                this_config.Data.inputDBS = 'global'
                this_config.Data.inputDataset = dataset
                splitting_mode = info.get(
                    "splitting", 
                    defaults.get("splitting", "Automatic")
                    )
                if not splitting_mode in ["Automatic", "FileBased", "LumiBased"]:
                    raise ValueError("Unrecognized splitting mode: {}".format(splitting_mode))
                this_config.Data.splitting = splitting_mode

                if not isMC:
                        this_config.Data.lumiMask = info.get(
                                'lumimask', 
                                defaults.get('lumimask', None)
                        )
                else:
                        this_config.Data.lumiMask = ''

                unitsPerJob = info.get("unitsPerJob", defaults.get("unitsPerJob", None))
                if unitsPerJob is not None:
                    this_config.Data.unitsPerJob = unitsPerJob

                totalUnits = info.get("totalUnits", defaults.get("totalUnits", None))
                if totalUnits is not None:
                    this_config.Data.totalUnits = totalUnits

                allowInvalid = info.get("allowInvalid", False)
                if allowInvalid:
                  config.Data.allowNonValidInputDataset = True
                
                print this_config
                #p = Process(target=submit, args=(this_config,))
                #p.start()
                #p.join()
                submit(this_config)
            print("*** Done with Sample {} ***\n\n".format(sample))

