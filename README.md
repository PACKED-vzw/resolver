Resolver
========

## Requirements
- MySQL server
- Python2
- virtualenv for Python

All requirements can easily be installed using your package manager of choice on Linux (OS X users may find relief in [Homebrew](http://brew.sh)).

## Installation

1. Clone the repository
2. Create a new virtual environment in the project directory (e.g. `$~ virtualenv venv`) and activate it (e.g. `$~ . venv/bin/activate`)
3. Install the required Python packages by executing `$~ pip install flask mysql-python sqlalchemy`
4. Change the settings in `resolver/config.py`
5. Initialize the database by running `$~ python initialize.py`

You should now be able to run the application using `$~ python runserver.py`. For production environments, it is advisable to use [Supervisor](http://supervisord.org/) to manage the application, and [Gunicorn](http://gunicorn.org/) or similar as server in combination with nginx or Apache.
