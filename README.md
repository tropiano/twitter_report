# How to run

First, activate the virtual environment

```
conda activate twitter_report
```

Then, run the following from the root of the project

```
gunicorn --bind 0.0.0.0:8000 twitter_report.wsgi
```

Then navigate to http://localhost:8000/users/

# How to debug

To check the crontab logs navigate to `/tmp/cronlog.txt`.
