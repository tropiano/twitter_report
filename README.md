# How to run

Run the following from the root of the project

```
gunicorn --bind 0.0.0.0:8000 twitter_report.wsgi
```

Then navigate to http://localhost:8000/users/
