# config.py

def get_user_role(password):
    if password == "scm2025":
        return "SCM"
    elif password == "viewonly":
        return "Viewer"
    else:
        return None
