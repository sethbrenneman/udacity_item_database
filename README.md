#Item Catalog Project

##Introduction

As a part of the Udacity Full Stack Nanodegree program, this project is meant to demonstrate knowledge of:

+ CRUD Database operations using Python's sqlalchemy package
+ Webpage routing and rendering using Python's Flask package
+ Authentication and Authorization using 3rd party login systems
+ API endpoints

##Functionality

+ Root page displays a list of movie categories and movie names
+ Anyone can navigate to specific movie pages to see their description
+ Users are able to create new movies for the database, and edit/delete movies that they have created
+ Non-registered users, or users that don't have permission to edit/delete movies do not see links to create/update/delete
+ Additionally, the backend protects these operations from attempts to access them from outside of the browser

##Requirements

+ Python version 2.7.12
+ A modern browser and internet connection to log in using a google ID

##Usage

The database and webserver for this project are run on a virtual machine on your local computer.  In order to run the project successfully you will need to

+ [Set up and install VirtualBox and Vagrant](https://classroom.udacity.com/nanodegrees/nd004/parts/8d3e23e1-9ab6-47eb-b4f3-d5dc7ef27bf0/modules/bc51d967-cb21-46f4-90ea-caf73439dc59/lessons/5475ecd6-cfdb-4418-85a2-f2583074c08d/concepts/14c72fe3-e3fe-4959-9c4b-467cf5b7c3a0)

+ Clone this repo to vagrant's shared folder

+ ssh into your virtual machine and navigate to the contents of this project

+ if the database has not been initialize, run `python populate_itemsdb.py` from your terminal

+ next, start the server with `python views.py` from your terminal

+ in your browser, navigate to localhost:8000

##Troubleshooting
Two specific problems I had were:

+ Initially my vagrant machine was not forwarding port 8000, so my browser could not send or receive requests from my virtual machine.  [Consult Vagrant's Documentation](https://www.vagrantup.com/docs/networking/forwarded_ports.html) on how to modify your vagrant configuration file if you have this problem

+ My vagrant machine's DNS server was not correctly configured.  Because of this, my app was unable to access any 3rd party site (without knowing the actual IP address).  I changed the IP address in the `/etc/resolv.conf` file to 8.8.8.8 for domain requests to correctly resolve.