# SDE2 - Round 2 - Rohit Bhagat (10th November 2023)

### Setup Docker
https://docs.docker.com/desktop/ </br>
https://docs.docker.com/compose/install/

### Copy the environment file and enter the values to be used:
```
cd setup
cp .env.example .env
```

### Run the docker images
```
docker-compose up --build
``` 

## Problem Statement
At Mindtickle, a client has requested a custom report that lists all active users on the platform and the number of daily lessons they have completed in the last 30 days. Your task is to create a Python script to generate this report and save it in an AWS S3 Bucket.

The data for this report is spread across two different databases: PostgreSQL and MySQL. You are not required to create the database, but you have access to the docker-compose file which will create the sample databases for you.

Criteria:
1. Understanding of the problem.
2. Correctness and efficiency of the solution
3. Clarity of the code written.

**Note:**
- Follow all the best practices you would follow for a production grade code.


# Report Generator


### Project Structure

- main.py
- config.py
- log.conf
- .env

- database
    - __init__.py
    - connections.py
    - models.py
    - create_reports_generated.sql

- exceptions
    - __int__.py
    - report_gen_exceptions.py

- report
    - tests
        - __init__.py
        - test_customer_x_queries.py
        - test_customer_x_report.py
    - __init__.py  (calls all the logic and services)
    - customer_x_report.py  (report specific logic here)
    - report_types.py  (Enum with all valid report types)

- services
    - tests
        - __init__.py
        - test_aws_s3.py
    - __init__.py
    - aws_s3.py
    - save_report_details.py

----
### How to run

- `git clone` the code.
- `pip install -r requirements.txt` to install all the pip requirements (tested on python version 3.11 and 3.10). pyOpenSSL and cryptography can create version conflicts. Upgrade the pyOpenSSL to the latest version, that will solve it.
- Set up the correct credentials in the `.env` file.
- Assuming the `mindtickle_users` and `lesson_completed` tables are already active, you will need to create another table in the Postgres DB `reports_generated` to save the data for the reports being generated. Included in the code is a `create_reports_generated.sql` to be able to create the needed table.
- Now we should be able to run the code simply using `python main.py {report_type}`.
- Currently the report type is the test report that I asked to create, but the project has been designed to accept argument for the report type that needs to be generated.
- Even if run without any argument, like `python main.py` it will generate the default test report.

----

### Documentation

All the code functions include docstrings, so documentation for all the code can be generated very easily. I personally would've used `sphinx` to generate the docs for the project. I have included a `env.template` file for the required config.

----

### Validations implemented

- All the credentials in .env are parsed using `Pydantic Settings`. This should take care of basic type checking that the passed credentials are of valid type, including extra validations for PostgreSQL and MySQL URIs.
- All Exceptions raised because of bad configuration / credentials / parameters have been handled specifically.

----

### Notes for the Evaluator

- I have tried to optimize the Data fetching and processing code.
    - The function fetches `active users` in chunks (batches).
    - Lesson completed are pulled for this chunk of users.
    - Some dataframe columns are type converted to 'int8' to save memory instead of the default 'int64'.

- The only personal machine that I have currently is a loaner from a friend, and runs windows, which has been a huge pain for me to set things up to code properly. Setting up docker and docker-compose was a task, as it requries Windows Subsystem for Linux to be installed. Which itself was a task, as it kept failing for a network problem. Which after quite a bit of head banging turned out to be because of my internet provider Jio Fiber, which for some reason blocks access to `raw.github.com`. So I decided install both the databased locally on my system directly, which I did and set it up for testing the code. I did later clear my head and install the docker desktop for windows.

- I was not sure about my local machine, so I did spin up an instance of `S3` and `EC2` to properly test the code. The instances are still active, and I will keep them that way for the next few days.

- All of the code has been tested being deployed on actual EC2 ubuntu 22.04 instance and a live S3 instance.

- I am aware that using `IAM role` for aws authentication from code is a much better practice, but like I've already mentioned, I was on windows machine and did not want to kill more time trying set things up for AWS config. As for the code, change for IAM role based auth can be easily handled by simply not passing in the aws_secret_access_key and key_id when creating a client. Rest will work as it is, so a 2 line change should suffice.

- I also wanted to set up pre commit git hooks for `black` and `pylint`, but again, I have no idea how I would go about that in windows.