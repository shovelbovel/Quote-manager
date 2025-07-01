-- Database setup script for Service Quote Management System
-- Run this script in your MySQL database (XAMPP) to set up the required database structure

/*
  This script will:
  1. Create the database if it doesn't exist
  2. Configure character set and collation
  3. Create a user with appropriate permissions (optional)
*/

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS devis_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Use the database
USE devis_db;

-- Optional: Create a dedicated user for the application
-- In production, use a more secure password
CREATE USER IF NOT EXISTS 'devis_user'@'localhost' IDENTIFIED BY 'devis_password';
GRANT ALL PRIVILEGES ON devis_db.* TO 'devis_user'@'localhost';
FLUSH PRIVILEGES;

-- Note: The tables will be created by Django's migration system
-- This script just ensures the database exists with proper encoding
-- For the project to use this database, configure the settings.py file as follows:
/*
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'devis_db',
        'USER': 'devis_user',  # or 'root' if using the default XAMPP user
        'PASSWORD': 'devis_password',  # or '' if using the default XAMPP user with no password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
*/

-- When running with Django migrations, the necessary tables will be created automatically
-- You can run migrations with:
-- python manage.py migrate