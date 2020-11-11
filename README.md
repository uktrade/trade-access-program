[![CircleCI](https://circleci.com/gh/uktrade/trade-access-program/tree/master.svg?style=shield)](https://circleci.com/gh/uktrade/trade-access-program/tree/master)

# trade-access-program
This repo houses the tradeshow access program (TAP) service

## Installation

### Requirements
 - [docker](https://hub.docker.com/editions/community/docker-ce-desktop-mac)
 - [docker-compose](https://hub.docker.com/editions/community/docker-ce-desktop-mac)

### Build the project
```
make build
```

### Run all services 
```
make up
```

#### Browse at:
- Grant application site: http://localhost:8000
- Frontend admin site: http://localhost:8000/admin/
- Grant management site: http://localhost:8001/workflow/
- Backoffice admin site: http://localhost:8001/admin/

## Development
Development has been done to attempt to be OS agnostic. All functionality _should_ be 
available via docker and docker-compose entry points.

### Debugging
#### Run with port access.
This allows you to drop into a debug breakpoint with: `pdb`, `ipdb` or similar

##### Backoffice
```
make run-background-services
make run-backoffice-debug
```   

##### Frontend
```
make run-background-services
make run-frontend-debug
```   

#### Elevate user permissions
In order to view grant applications in the [grant management site](http://localhost.com/workflow) you will need to 
give your user the right permissions. 

To do this first log into the [grant management site](http://localhost.com/workflow) 
using your single sign on (SSO) gov account. This will create your user record. Then you 
can run the elevate command to grant your user the right permissions. 
```
cd backoffice
make elevate
```

### Seed database
You can seed the database with some dummy data using:
```
cd backoffice
make seed-db
``` 

This will add a few dummy grant applications to your database which will be viewable in the
[grant management site](http://localhost.com/workflow). 

_Note: Make sure you have given your user permissions to view new grant applications by following 
the steps in the [Elevate user permissions](#elevate-user-permissions) section_  

### Run detached
```
docker-compose up -d
```

## Testing
The project uses `pytest` to run the test suite and generate test coverage.
 - command `make test`
 - config `./setup.cfg`
 - coverage reporting output `./reports/coverage` 

## Linting
The project uses flake8 for linting.
 - command `make lint`
 - config `./setup.cfg`
 
## Branching strategy
 - master branch => production environment
 - staging branch => staging environment
 - develop branch => develop environment
 - feature branches => **no environment**
 
Feature branches should branch off of develop and be merged back into develop (ideally with 
minimal single purpose commits).
 
## Deployment
The project has 4 environments:

#### develop
- Develop is automatically deployed from the **develop** branch.
- http://trade-access-program-dev.london.cloudapps.digital/

#### staging
- Staging is automatically deployed from the **staging** branch
- http://trade-access-program-staging.london.cloudapps.digital/
    
#### uat 
- UAT is manually deployed
- http://trade-access-program-uat.london.cloudapps.digital/
    
#### production 
- Production is manually deployed. 
- domain TBD
 