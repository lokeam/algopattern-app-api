# Algorithm Pattern API
Fully-functioning backend REST API that forms the features for an data structures and algorithms pattern app. Allows users to document the various underlying patterns behind data structure and algorithm questions used in software engineering technical assessments as well as computer science fundamental university courses.

Powered by Python, Django, Docker and PostreSQL.

## Key Features
* Backend codebase and database for an app
* API Endpoints for managing users, algo patterns and classification tags, image uploads and filtering
* User Authentication
* Browsable Admin interface allowing users to both see all endpoints and make test requests
* Python Django codebase served via Docker containers and tested within automated CI/CD Github Action workflow

## How To Use
In order to run this application, you'll need the following:
- Git
- Docker

### Installation and Setup
```bash
# Clone the repo
$  git  clone  git@github.com:lokeam/algopattern-app-api.git

# Navigate to the eslab directory
$  cd  algo-pattern-app-api

# Build the Docker container
$  docker-compose up

# Open your browser of choice, go to http://127.0.0.0.0:8000/
```

### Other commands
```bash
# Stop your Docker container
`ctrl + c`

# Run unit tests locally
docker-compose run --rm app sh -c "python manage.py test"

# Make DB Migrations
docker-compose run --rm app sh -c "python manage.py makemigrations"

# Manually run linter
docker-compose run --rm app sh -c "python manage.py makemigrations"
```

## Acknowledgements
This app is based on information covered within the [Grokking the Coding Interview: Patterns for Coding Questions](https://www.educative.io/courses/grokking-coding-interview-patterns-java) course on [educative.io](https://www.educative.io/) and Fahim ul Haq's [14 Patterns to Ace Any Coding Interview Question](https://hackernoon.com/14-patterns-to-ace-any-coding-interview-question-c5bb3357f6ed) article on [Hackernoon](https://hackernoon.com/).

## License
This project is licensed under the terms of the MIT license.