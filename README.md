# Ny_News_Project

## Presentation

This repository contains all the necessary files to run the app we've developed during our Data Engineering Bootcamp for the NY News project. 

The main goal of this project was to create a dashboard that would display all sorts of information scraped from 3 New York Times APIs: Books API, Article Search API, and Time Wire API.

Our application is structured as follows:

-A MongoDB database to store our data.

-An ETL process to load data from the three NY Times APIs into the database.

-A streaming ETL process.

-An API.

-A dashboard to display the various data retrieved from our API.

## Installation
To run our application, you'll need to do the following steps:

-Download the repository docker_projet.

-Create an account on the New York Times dev platform and get API keys for Books API, Article Search API, and Time Wire API.

-Modify the configuration.ini files to add your API key

-Modify the docker-compose.yml file. There is an environment variable for each container of our application which takes the IP address of your machine as a string. You need to modify the value and input your IP address.

-Once it's done, you need to navigate into the docker_projet directory and execute the bash command:

```
bash setup.sh
```
This will execute all the commands needed to start the application. This operation can take several minutes.

The API should then be available at http://localhost:10002

The dashboard should then be available at http://localhost:10003

## Remarks

You will notice a file "finish.txt" after the first execution of the docker-compose file. This is a flag that is used to execute the scripts of the streaming ETL, API, and dashboard after the ETL process is finished.

## Debug
You need to execute the command "bash setup.sh" every time you want to start the application.

If you encounter any issues when trying to launch the application again, you can delete the directory "projet_data" that was created during the first execution of docker-compose.yml.
