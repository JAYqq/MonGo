from app import db
from app.models import User
def test():
    users=User.query.all()
    for user in users:
        print(user.username)
if __name__ == "__main__":
    test()