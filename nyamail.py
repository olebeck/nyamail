import mysql.connector
import argparse

import dotenv, os
dotenv.load_dotenv("mail.env")

def connect_db():
    host = os.getenv("SQL_HOST")
    user = os.getenv("SQL_USER")
    password = os.getenv("SQL_PASSWORD")
    database = os.getenv("SQL_DATABASE")
    db = mysql.connector.connect(host=host, user=user, password=password, database=database)
    return db

import getpass
def input_password():
    password = getpass.getpass(prompt="Please enter your password: ")
    password2 = getpass.getpass(prompt="Confirm Password: ")
    if password != password2:
        print("doesnt match")
        raise Exception("Unmatched password")
    return password


def get_users(db):
    cursor = db.cursor()
    cursor.execute("SELECT email FROM virtual_users;")
    for email in cursor:
        yield email[0]
    cursor.close()

def add_user(db, email, password):
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO virtual_users
        (domain_id, password , email)
        VALUES
        ('1', ENCRYPT(%s, CONCAT('\$6\$', SUBSTRING(SHA(RAND()), -16))), %s);
    """, (password, email))
    db.commit()
    cursor.close()

def change_password(db, email, password):
    cursor = db.cursor()
    cursor.execute("""
        UPDATE virtual_users
        (password)
        VALUES
        (ENCRYPT(%s, CONCAT('\$6\$', SUBSTRING(SHA(RAND()), -16))))
        WHERE email = %s;
    """, (password, email))
    db.commit()
    cursor.close()

def user_subcommand(args, db):
    if args.action == "list":
        print("Users:")
        for user in get_users(db):
            print("\t"+user)
        print()
        return
    elif args.action == "add":
        password = input_password()
        add_user(db, args.email, password)
    elif args.action == "change-password":
        password = input_password()
        add_user(db, args.email, password)

def main():
    p = argparse.ArgumentParser()
    subparsers = p.add_subparsers(title="Subcommand", dest="subcommand", required=True)
    user_p = subparsers.add_parser("user")
    user_p_actions = user_p.add_subparsers(dest="action", required=True)
    user_p_actions.add_parser("list")
    
    add_p = user_p_actions.add_parser("add")
    add_p.add_argument("email")

    change_password_p = user_p_actions.add_parser("change-password")
    change_password_p.add_argument("email")

    args = p.parse_args()
    print(args)

    db = connect_db()

    if args.subcommand == "user":
        user_subcommand(args, db)



if __name__ == "__main__":
    main()
