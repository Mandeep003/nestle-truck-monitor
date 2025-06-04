def get_user_role(password):
    if password == "scm2025":
        return "SCM"
    elif password == "1234":
        return "Parking"
    else:
        return None
