# podcast-summarization-app

# Backend - src

A FastAPI based application that provides a platform for users to search and fetch podcast information from a S3 bucket, and store the requested links in a database.

## Features

- Fetches podcast data by name.
- Handles AWS S3 bucket operations for storing and retrieving podcasts.
- Allows users to register requested podcast links in a SQLite database.
- Provides a simple frontend for user interaction.

## Note

For the Minimum Viable Product (MVP), the login and sign up features are currently not functional. They are placeholders for future development.

## Installation

To run this application, follow the steps below:

1. Clone this repository:
   ```
   git clone https://github.com/patrick-nanys/podcast-summarization-app.git
   ```
2. Navigate to the repository directory:
   ```
   cd podcast-summarization-app/src
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   uvicorn main:app --reload
   ```
   
## Usage

- Home (`/`) - It serves the home page of the application.
- Registration (`/register`) - The endpoint to register a new user (under construction).
- Sign In (`/signin`) - The endpoint to authenticate a user (under construction).
- Browse (`/browse/`) - It serves the browse page of the application where users can submit YouTube links to be stored in the database. On POST request, it handles the link submission.
- Podcast (`/podcast/`) - Fetches podcast data based on the name from S3 bucket.

## Configuration

You will need to provide AWS configuration details (Region, Key ID, Access Key, and S3 Bucket name) for the application to interact with AWS S3. These configurations should be stored in a `variables.ini` file located in the parent directory.

Example configuration:

```ini
[AWS]
region = your_aws_region
aws_access_key_id = your_access_key_id
aws_secret_access_key = your_secret_access_key
bucket = your_bucket_name
```

## Database Schema

The application uses a SQLite database to store user requested links. The `Podcast` model includes:

- `id`: An auto-incremented integer serving as the primary key.
- `link`: A string field for storing the podcast link.

## Dependencies

The main dependencies for this application are:

- FastAPI: For creating the web application and APIs.
- SQLAlchemy: For interacting with the SQLite database.
- Boto3: For interacting with AWS S3.
- FastAPI Templating: For handling HTML responses with Jinja2 templates.

# Frontend - frontend



# License

This project is licensed under the terms of the MIT license.
