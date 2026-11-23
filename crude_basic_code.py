# 1. CRESTE (POST) = data add karna
def post(self):
    arg = user_args.parse_args() # it take data from input ad store in args
    user = UserModel(
        name = args["name"],
        email = args["email"]
    )
    db.session.add(user)
    db.session.commit()
    return user , 201

#2 READ (GET) = show all the users
def get(self):
    return UserModel.query.all()

#3 UPDATE (PATCH)
def patch(self , id):
    args = user_args.parse_args()
    user = UserModel.query.filter_by(id=id).first()
    user.name = args["name"]
    user.email = args["email"]
    db.session.commit()
    return user
#DELETE 
def delete(self , id):
    user = UserModel.queryfilter_by(id-id).first()
    db.session.delete(user)
    db.session.commit()
    return {} , 200




    