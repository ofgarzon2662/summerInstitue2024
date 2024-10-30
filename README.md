# summerInstitute2024
This repository provides detailed documentation for a hypothetical project demonstrating GitHub functionalities. It includes examples of repository management, branching, and collaboration workflows, making it an excellent resource for developers and students exploring GitHub's features in a practical context.

## Run Recetario Flask App

1. Clone this repo to your local PC.
2. Navigate to the root directory of the project using the command line.
3. Ensure you have `pip` installed. If not, install it on your PC.
4. Install `pipenv` via the command line: `$ pip install pipenv`
5. Create a virtual environment with `pipenv` using Python 3.9.18: `$ pipenv --python 3.9.18`
6. Install the dependencies provided in this repo: `$ pipenv install -r requirements.txt`
7. Activate the virtual environment with `pipenv`: `$ pipenv shell`
8. Run the app: `$ flask run`. This command starts the Flask development server. By default, it will run on `http://127.0.0.1:5000/`. You can specify a different host and port if necessary: `$ flask run --host=0.0.0.0 --port=8000`

## Run Unit Test Suite

1. Once the Flask app is up and running, open a new terminal window.
2. In the root directory of the project, run: `$ python -m unittest discover -s tests`. This will run the entire unit test suite in this project.
3. You can also run each unit test file separately: `$ python -m unittest tests.test_chef`

