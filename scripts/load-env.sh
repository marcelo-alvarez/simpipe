hostname=$(hostname)
if [ ${hostname:0:2} == "sh" ] ; then
    export simpipesys=sherlock
    export simpipedir=/oak/stanford/orgs/kipac/simpipe
elif [ ${hostname:0:3} == "sdf" ] ; then
    export simpipesys=s3df
    export simpipedir=/sdf/group/kipac/simpipe
fi
source $simpipedir/load-env.sh