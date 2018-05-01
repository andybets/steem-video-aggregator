# Steem Video Aggregator

Development on this project is currently suspended due to the uncertainty/risk of running a site based on this code under UK jurisdiction.

## How to Run (for development)

1. Install docker and docker-compose

2. Create the credentials.env file like the template, and replace credentials/settings with those your require

3. Update docker-compose.yml to provide a volume for the database

4. Build and run the Docker containers

- % docker-compose build
- % docker-compose build
- % docker-compose up -d

5. Browse to http://localhost:81


## To Use with SSL (or on non-localhost domain)

1. Use LetsEncrypt and Certbot to add fullchain.pem and privkey.pem files to project root directory

2. Edit mysettings-ssl.conf to uncomment certificate lines and change server_name to your domain


## Database Schema Migrations
Execute from within running web container...

- % flask db init - Adds a database migrations folder to your application.
- % flask db migrate - Makes a migration script.
- % flask db upgrade - Applies outstanding migrations to the database.

See https://flask-migrate.readthedocs.io for more info.
