admin_roles = [
    "admin",
    "Manager",
]

request_types = [
    "Unpaid",
    "Vacation",
]

ROLES = [
    ("MGR", "Manager"),
    ("CK", "Cook"),
    ("SVR", "Server"),
]

def default_week():
    return {
        str(day): {"start": "07:00", "end": "22:00"} 
        for day in range(7)
    }

