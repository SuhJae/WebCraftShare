# Web Student Service Documentation

This service allows pre-configured students to log in, upload their web project files (HTML, CSS, JS, etc.), and get a link that they can share.

## Table of Contents

- [File Structure](#file-structure)
- [Installation and Setup](#installation-and-setup)
- [Endpoints](#endpoints)
- [Using the Service](#using-the-service)

## File Structure

```text
├── app.py # Flask application
│
├── static/ # Static files such as JS, CSS, etc.
│ ├── css/
│ │ └── styles.css # Styles for your web pages
│ │
│ └── js/
│ └── scripts.js # Any additional JS scripts if needed
│
├── templates/ # HTML templates for Flask
│ ├── base.html # Base template with common layout
│ ├── login.html # Login page template
│ ├── home.html # Homepage showing list of projects
│ ├── upload.html # Page to upload files
│ └── project_view.html # Template to display individual projects
│
└── uploaded_files/ # Folder where uploaded files will be stored
├── user1/ # Folder for a specific user
│ ├── project1/ # A specific project of the user
│ └── project2/
│
├── user2/
└── ...
```

## Installation and Setup

1. Install the required Python packages:

```bash
pip install Flask Flask-Login Flask-Uploads
