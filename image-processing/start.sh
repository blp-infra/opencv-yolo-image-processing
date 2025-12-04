#!/bin/bash

#!/bin/bash
# Start monitor script in background
# 
#/bin/bash monitor.sh &  # monitor without cronjob


####### writing the cron job #########
# Create cron entry file
# cat <<EOF >/app/mycron
# */2 * * * * /app/cron.sh
# EOF

# # Install the cron file
# crontab /app/mycron

# # Start cron service
# service cron start

# echo "Cron installed and started."
#######################################
# 
#
# 
# start supervisored

