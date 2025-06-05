def get_user_role(password):
    if password == "master123":
        return "MasterUser"
    elif password == "scm123":
        return "SCM"
    elif password == "gate123":
        return "Gate"
    elif password == "parking123":
        return "Parking"
    else:
        return None
