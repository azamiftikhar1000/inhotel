# # Pydantic imports
# from pydantic import EmailStr

# # application import
# from src.auth.models import RefreshToken, User
# from sqlalchemy.orm import Session


# class UserRepo:
#     def __init__(self, db: Session) -> None:
#         self.db = db

#     def base_query(self):
#         # Base Query for DB calls
#         return self.db.query(User)

#     def get_user(self, email: EmailStr):
#         # get user by email
#         return self.base_query().filter(User.email.icontains(email)).first()

#     def create(self, user_create: any) -> User:
#         # create a new user
#         new_user = User(**user_create.dict())
#         new_user.is_premium = False
#         self.db.add(new_user)
#         self.db.commit()
#         self.db.refresh(new_user)
#         return new_user

#     def delete(self, user: User) -> bool:
#         # delete user
#         resp = False

#         self.db.delete(user)
#         self.db.commit()

#         quick_check = self.base_query().filter(User.email == user.email).first()
#         if not quick_check:
#             resp = True
#         return resp

#     def update(self, user: User):
#         # update user
#         updated_user = user
#         self.db.commit()
#         self.db.refresh(updated_user)
#         return updated_user


# # Instatiating the Classes.

# user_repo = UserRepo
