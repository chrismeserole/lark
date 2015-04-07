import subprocess
from larklib import Site

# get config settings
site = Site().config_vars

# set s3cmd call
s3call = "s3cmd sync %s/  %s/ --delete-removed" % ( site.output_path, site.s3_bucket )

# run s3cmd call
print subprocess.Popen( s3call, shell=True, stdout=subprocess.PIPE).stdout.read()
