#!/usr/bin/env python3
"""Create an ExpenseMate user from the command line.

Usage (from Mate/ directory, with venv active):
  python create_user.py --username admin --email admin@example.com --password 'Secret123'
  python create_user.py  # interactive prompts
"""

import argparse
import getpass
import sys

from app import create_app
from models.extensions import db
from models.mate import User


def create_user(email, password, username):
    app = create_app()
    with app.app_context():
        db.create_all()

        if User.query.filter_by(email=email).first():
            print(f"Error: a user with email '{email}' already exists.")
            return False

        if User.query.filter_by(username=username).first():
            print(f"Error: a user with username '{username}' already exists.")
            return False

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"User created successfully: {username} <{email}>")
        return True


def main():
    parser = argparse.ArgumentParser(description="Create an ExpenseMate user")
    parser.add_argument("--username", "-u", help="Username")
    parser.add_argument("--email", "-e", help="Email address")
    parser.add_argument("--password", "-p", help="Password (prompted if omitted)")
    args = parser.parse_args()

    username = args.username or input("Username: ").strip()
    email = args.email or input("Email: ").strip()
    password = args.password
    if not password:
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Error: passwords do not match.")
            sys.exit(1)

    if not username or not email or not password:
        print("Error: username, email, and password are required.")
        sys.exit(1)

    if len(password) < 6:
        print("Error: password must be at least 6 characters.")
        sys.exit(1)

    ok = create_user(email=email, password=password, username=username)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
