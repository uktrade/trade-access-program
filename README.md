[![CircleCI](https://circleci.com/gh/uktrade/trade-access-program/tree/master.svg?style=shield)](https://circleci.com/gh/uktrade/trade-access-program/tree/master)

# trade-access-program
TAP is an initiative to provide small grants to SME businesses and sole traders to help them start or grow their 
exports.  

This repo houses the Tradeshow Access Program (TAP) services.  

## Architecture 
There are 2 services in this project. Each service serves a slightly different purpose but both are build with the 
Django framework. 

See the **[ADR on service architecture](docs/adr/0006-split-service-into-two.md)** for more details about this decision. 

- frontend
  - serves the govuk styled grant application form.
  - communicates with the backoffice via json REST APIs. 
- backoffice
  - serves some dynamic content for the frontend services via json REST APIs.
  - stores the state of grant applications. 
  - serves the grant management portal for the internal users (DIT/TAP)

## Installation (docker)

### Requirements
 - [docker](https://hub.docker.com/editions/community/docker-ce-desktop-mac)
 - [docker-compose](https://hub.docker.com/editions/community/docker-ce-desktop-mac)

### Build the project
```
make build
```
_The first time you run `make build` a templated `.env` file will be created in every service directory 
(`./frontend`, `./backoffice`). Please update these files with any secrets required to make these services run correctly._

Populate the following environment variables in the relevant `.env` files:

#### Backoffice .env 
location: `./backoffice/.env`

| Variable name              | Required      | Description                               |
| -------------------------- | ------------- | ----------------------------------------- |
| `DEBUG`                    | Yes           | Django DEBUG setting                      |
| `DJANGO_SETTINGS_MODULE`   | Yes           | location of Django settings module        |
| `POSTGRES_DB`              | Yes           | backoffice db name                        |
| `POSTGRES_USER`            | Yes           | backoffice db user                        |
| `POSTGRES_PASSWORD`        | Yes           | backoffice db password                    |
| `POSTGRES_HOST`            | Yes           | backoffice db hostname                    |
| `POSTGRES_PORT`            | Yes           | backoffice db port                        |
| `AUTHBROKER_URL`           | Yes           | URL for SSO service                       |
| `AUTHBROKER_CLIENT_ID`     | Yes           | SSO service client id                     |
| `AUTHBROKER_CLIENT_SECRET` | Yes           | SSO service client secret                 |
| `SECRET_KEY`               | Yes           | Unique Django secret key                  |
| `DNB_SERVICE_URL`          | Yes           | URL for DNB service                       |
| `DNB_SERVICE_TOKEN`        | Yes           | API token for DNB service                 |
| `NOTIFY_API_KEY`           | Yes           | API token for gov.notify service          |
| `COMPANIES_HOUSE_URL`      | Yes           | URL for companies house service           |
| `COMPANIES_HOUSE_API_KEY`  | Yes           | API token for companies house service     |

#### frontend .env 
location: `./frontend/.env`

| Variable name             | Required      | Description                         |
| ------------------------- | ------------- | ----------------------------------- |
| `DEBUG`                   | Yes           | Django DEBUG setting                |
| `DJANGO_SETTINGS_MODULE`  | Yes           | location of Django settings module  |
| `POSTGRES_DB`             | Yes           | frontend db name                    |
| `POSTGRES_USER`           | Yes           | frontend db user                    |
| `POSTGRES_PASSWORD`       | Yes           | frontend db password                |
| `POSTGRES_HOST`           | Yes           | frontend db hostname                |
| `POSTGRES_PORT`           | Yes           | frontend db port                    |
| `SECRET_KEY`              | Yes           | Unique Django secret key            |
| `BACKOFFICE_API_URL`      | Yes           | URL for backoffice service          |


### Run all services
```
make up
```

#### Browse at:
- Grant application site: http://localhost:8000
- Frontend admin site: http://localhost:8000/admin/
- Grant management site: http://localhost:8001
- Backoffice admin site: http://localhost:8001/admin/

## Development (docker)
The project has been created in an attempt to be OS agnostic. All functionality _should_ be available via docker 
and docker-compose entry points.

### Debugging
#### Run with port access.
This will allow you to drop into a debug breakpoint with: `pdb`, `ipdb` or similar.

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

## Development (native)
If you are going to be working on this project for an extended period of time it might be useful to set up a native 
development environment. This can be useful when using an IDE. This will of course vary from machine to machine depending on your native local environment 
but this section covers some basics about what tech the project uses. This section is relevant to all services in 
the project (`./frontend` and `./backoffice`).

### Python setup
To develop the project natively the suggestion would be to set up a virtualenv for each service directory 
(`./frontend` and `./backoffice`) using whichever virtualenv tech you are familiar with (pyenv, pyenv-virtualenv, 
virtualenvwrapper, virtualenv).

The project uses the pip-tools system to manage python dependencies. So once you have setup your virtualenv and
activated it you can install all dependencies into it by running:
```
cd <service-dir>
make pip-compile-and-sync-dev
```

### node setup
The easiest way to install the necessary node libraries is to use the main root docker build. This will install 
`node_modules` into all the relevant service directories.
```
make build
```
This will create a `./<service-dir>/node_modules` folder in each of the service directories. 

## Testing
The project uses `pytest` to run the test suite and generate test coverage. Dummy environment values are required in 
the `.env` files in order for the tests to run. 
 - command to run all test suites `make test`
    - command to run only frontend test suite `make test-frontend` or `cd frontend && make test`
    - command to run only backoffice test suite `make test-backoffice` or `cd backoffice && make test`
 - config `./<service-dir>/setup.cfg`
 - coverage reporting output `./<service-dir>/reports/coverage` 

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
 - feature branches => **no environment**
 - develop branch   => develop environment
 - staging branch   => staging environment
 - uat branch       => uat environment
 - master branch    => production environment
 
Feature branches should branch off of develop and be merged back into develop (ideally with 
minimal single purpose commits).

## Deployment
Deployments are handled automatically by Jenkins and are not related the the CircleCI builds that get run on each 
pull request.

The project has 4 environments. All environments sit behind the DIT vpn with the exception of `frontend-uat` 
(this exception is to allow non DIT staff to access this site, e.e. the main TAP team).

Each environment is deployed from its corresponding github branch. The deploy is executed automatically by 
[Jenkins](https://jenkins.ci.uktrade.digital/view/Trade%20Access%20Program/) once a commit or push is made to that 
github branch. This is done via a polling job in Jenkins (set up and managed by the Webops team).    

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
 