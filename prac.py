def validate_password(password, confirmation):

    
    if password != confirmation: 
        return "Passwords do not match"
    
    if len(password) < 8:
        return "Password must be at least 8 characters"
    
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number"
    
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter"
    
    if not any(char.islower() for char in password):
        return "Password must contain at least one lowercase letter"

    return True
    

print(validate_password("december1","december1"))
