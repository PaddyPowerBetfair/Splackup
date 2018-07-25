eval `ssh-agent -s`
ssh-add git_dsa
rm -rf splunk-config
git clone git@mygit.company.com:team-sre/splunk-config.git
cd splunk-config
python ../splackup.py
git add *
git commit -m "backup on `date` from `hostname`"
git push
