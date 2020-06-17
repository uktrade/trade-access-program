# trade-access-program
A repo to house the trade access program (TAP) service

## Install

### Requirements
 - docker
 - docker-compose 
 
### Set up

To run the project in the foreground
```
docker-compose up web
```

## Development

### Debugging
Run run with port access (i.e. to open a debugger on breakpoints)
```
docker-compose up -d db
docker-compose run --service-ports web
```

### Testing
To run tests you can use Pytest  
```
pytest
```
or the Django test command
```
python manage.py test
```

### Linting
To run the linter
```
flake8 .
```