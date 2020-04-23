import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
os.environ["DATABASE_URL"] = "postgres://ikpgjnrchcdhau:5d7d9d70298a6c5a5abfc86cb165a6f81368d73e31ee97aa53a60c8eaa868f88@ec2-52-87-58-157.compute-1.amazonaws.com:5432/d8a0ob5ogiao3q"
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year":year})
        # print(f"Added book having ISBN {isbn}, Title {title}, Author {author} and Year {year}.")
    db.commit()

if __name__ == "__main__":
    main()