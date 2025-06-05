def get_user_role(password):
    if password == "scm123":
        return "SCM"
    elif password == "123":
        return "Parking"
    elif password == "gate123":
        return "Gate"
    else:
        return None
print(get_user_role("gate123"))
