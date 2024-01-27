# Backend-Development
## Description
This Flask-based web application provides a platform for music streaming or information services. It integrates with Spotify for music data and offers features like user authentication, and interactions with tracks, albums, and artists.
## Features
* User Authentication: Secure login using JWT.
* Music Database: Models for Users, Tracks, Albums, and Artists.
* User Interactions: Functionalities for liking tracks and artists, rating tracks and adding friends.
* Recommendations: Recommending tracks based on genre, top rated track or friends activity
* Spotify Integration: Connects with Spotify for music data.
* Database Management: Using SQLAlchemy with Flask.
## Installation
### Prerequisites
* Python 3.x
* pip (Python package manager)
### Setup
* Clone the Repository
* Install Dependencies
* Configure Environment Variables
## Usage
### Running the Application
* Start the server using the command "flask run"
* The server will initiate on a designated port "http://localhost:5000", ready to handle requests
### Key Functionalities
#### HTTP Request Handling:
* The Flask framework is used to set up routes and handle HTTP requests and responses.
#### Database Operations:
* The script includes functionality to connect to a SQLite database using SQLAlchemy.
* It defines models and relationships, facilitating CRUD (Create, Read, Update, Delete) operations on the database.
#### Environment Configuration:
* Utilizes the 'dotenv' package for loading environment variables, enhancing security and flexibility in different deployment scenarios.
## Contributing
Contributions are welcome. Please adhere to coding standards and guidelines when submitting pull requests.

