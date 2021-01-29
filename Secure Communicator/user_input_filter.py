import re


def check_email(email):
    mail_re = "^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+"
    email_valid = re.match(mail_re, email)
    return email_valid


def check_pass(password):
    if len(password) == 0:
        return 0.0

    if re.match(r"^[0-9]*$", password):
        charsetBonus = 0.8
    elif re.match(r"^[a-z]*$", password):
        charsetBonus = 1.0
    elif re.match(r"^[a-z0-9]*$", password):
        charsetBonus = 1.2
    elif re.match(r"^[a-zA-Z]*$", password):
        charsetBonus = 1.3
    elif re.match(r"^[a-z\-_!?]*$", password):
        charsetBonus = 1.3
    elif re.match(r"^[a-zA-Z0-9]*$", password):
        charsetBonus = 1.5
    else:
        charsetBonus = 1.8
    if charsetBonus > 1.3:
        return True
