#this is not mean to be run locally
#
echo Check if TTY
if [ "`tty`" != "not a tty" ]; then
  echo "YOU SHOULD NOT RUN THIS IN INTERACTIVE, IT DELETES YOUR LOCAL FILES"
else

ls -lR .
echo "ENV..................................."
env 
echo "VOMS"
voms-proxy-info -all
echo "CMSSW BASE, python path, pwd"
echo $CMSSW_BASE 
echo $PYTHON_PATH
echo $PWD 

# Is this garbage necessary?
mkdir hide
mv $CMSSW_BASE/lib/ hide
mv $CMSSW_BASE/src/ hide
#mv $CMSSW_BASE/module/ hide
mv $CMSSW_BASE/python/ hide
mv lib $CMSSW_BASE/lib
mv src $CMSSW_BASE/src
#mv module $CMSSW_BASE/module
mv python $CMSSW_BASE/python

echo "lling CMSSW python dir before compiling:"
ls -lRth $CMSSW_BASE/python

cd $CMSSW_BASE/src
cmsenv
scram b -j8
cd -

echo "lling CMSSW python dir after compiling:"
ls -lRth $CMSSW_BASE/python

echo Found Proxy in: $X509_USER_PROXY
echo "asdf"
python -c "import sys; print sys.path"
ls -lrth
python crab_meat.py "$@"
fi