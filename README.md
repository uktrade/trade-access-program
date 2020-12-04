[![CircleCI](https://circleci.com/gh/uktrade/trade-access-program/tree/master.svg?style=shield)](https://circleci.com/gh/uktrade/trade-access-program/tree/master)

# trade-access-program
This repo houses the tradeshow access program (TAP) services. 

There are 2 services in this project. Each service serves a slightly different purpose but both are build with the Django framework. 

- frontend
  - serves the govuk styled grant application form.
  - communicates with the backoffice via json REST APIs. 
- backoffice
  - serves some dynamic content for the frontend services via json REST APIs.
  - stores the state of grant applications. 
  - serves the grant management portal for the internal teams (DIT/TAP)

## Installation

### Requirements
 - [docker](https://hub.docker.com/editions/community/docker-ce-desktop-mac)
 - [docker-compose](https://hub.docker.com/editions/community/docker-ce-desktop-mac)

### Build the project
```
make build
```
_The first time you run `make build` a templated `.env` file will be created in every service directory 
(`./frontend`, `./backoffice`). Please update these files with any secrets required to make these services run correctly._

### Run all services 
```
make up
```

#### Browse at:
- Grant application site: http://localhost:8000
- Frontend admin site: http://localhost:8000/admin/
- Grant management site: http://localhost:8001
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

### Elevate user permissions
_Note: development only_

In order to view grant applications in the [grant management site](http://localhost:8001/workflow) you will need to 
give your user superuser permissions.

To do this first log into the [grant management site](http://localhost:8001/workflow)
using your single sign on (SSO) gov account. This will create your user record. Then you 
can run the elevate command to grant your user the right permissions. 
```
cd backoffice
make elevate
```

In production `make elevate` will **not** work (controlled by the setting `CAN_ELEVATE_SSO_USER_PERMISSIONS`) therefore
permissions for each user need to be granted correctly via the backoffice Django admin site at: `/admin`
To do this do this following:
 - Ask the grant administrator to login to the system (using DIT SSO).
 - A superuser (likely a developer) will then need go to the backoffice Django admin site and:
    - set the `is_staff` flag for that new user account.
    - assign the relevant `viewflow` permissions to the new user account. 

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
To run all services in the background do
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

## CI/CD
We run the build, test suite and linting on each pushed commit to github. These are run through [CircleCI](https://app.circleci.com/pipelines/github/uktrade/trade-access-program).

### Pull requests
Pull requests in github cannot be merged until the CircleCI jobs report a successful result.

### Build Artifacts
Build artifacts are stored against each build in CircleCI. These artifacts include:
 - Frontend test coverage
 - Backend test coverage
 - Backend ERD diagram for that commit (using `python manage.py graph_models`) 
 
## Branching strategy
 - master branch => production environment
 - staging branch => staging environment
 - develop branch => develop environment
 - feature branches => **no environment**
 
Feature branches should branch off of develop and be merged back into develop (ideally with 
minimal single purpose commits).

## Deployment
The project has 4 environments. All environments sit behind the DIT vpn with the exception of `frontend-uat` (this exception is to allow non DIT staff to access this site, e.e. the main TAP team).

Each environment is deployed from its corresponding github branch. The deploy is executed automatically by [Jenkins](https://jenkins.ci.uktrade.digital/view/Trade%20Access%20Program/) once a commit or push is made to that github branch. This is done using a polling job in Jenkins (set up and managed by the Webops team).    

Deployemnts are handled by Jenkins and are not related the the CircleCI builds that get run on each Pull request.

#### Develop
- Develop is automatically deployed from the **develop** branch.
- https://trade-access-program-frontend-dev.london.cloudapps.digital/
- https://trade-access-program-backoffice-dev.london.cloudapps.digital/

#### Staging
- Staging is automatically deployed from the **staging** branch
- https://trade-access-program-frontend-staging.london.cloudapps.digital/
- https://trade-access-program-backoffice-staging.london.cloudapps.digital/
    
#### UAT 
- UAT is automatically deployed from the **uat** branch
- https://trade-access-program-frontend-uat.london.cloudapps.digital/
- https://trade-access-program-backoffice-uat.london.cloudapps.digital/
    
#### Production 
- Does not exist... yet...
 