# Deploy to Heroku

## Introduction

1. Link Existing app to Heroku
```bash
heroku git:remote -a agrimarketwatch
```

2. Verify existing remote
```bash
git remote -v
```

3. Force Installation of app
```bash
git push -f heroku master
```

4. View Logs to Ensure app installation success
```bash
heroku logs --tail
```

