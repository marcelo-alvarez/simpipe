# simpipe
N-body simulation pipeine

## running at S3DF or Sherlock
```
# Example to run a simulation at S3DF or Sherlock

% cd $HOME
% git clone https://github.com/marcelo-alvarez/simpipe.git
% source simpipe/scripts/load-env.sh
% export EMAIL=your_email_address
% python simpipe/py/makesim.py --N 1024 --Npm 2048 --boxsize 200 --Ntasks 96
```
