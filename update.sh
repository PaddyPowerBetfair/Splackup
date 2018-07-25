eval `ssh-agent -s`
ssh-add git_dsa
cd splunk-config
rm -rf *
python ../splackup.py
git add *
git commit -m "backup on `date` from `hostname`"
git push
