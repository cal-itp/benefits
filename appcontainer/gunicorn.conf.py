"""
The Gunicorn configuration file
More information: https://docs.gunicorn.org/en/stable/settings.html
"""

import multiprocessing

# the unix socket defined in nginx.conf
bind = "unix:/home/calitp/app/run/gunicorn.sock"

# Recommend (2 x $num_cores) + 1 as the number of workers to start off with
workers = multiprocessing.cpu_count() * 2 + 1

# send logs to stdout and stderr
accesslog = "-"
errorlog = "-"

# Preloading can save some RAM resources as well as speed up server boot times,
# at the cost of not being able to reload app code by restarting workers
# (in an ECS Fargate environment, this isn't possible anyway)
preload_app = True
