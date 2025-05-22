import json
from werkzeug.security import generate_password_hash

def update_passwords():
    # Read current users
    with open('app/auth/users.json', 'r') as f:
        users = json.load(f)
    
    # Update passwords with hashed versions
    for username, user_data in users.items():
        plain_password = user_data['password']
        hashed_password = generate_password_hash(plain_password)
        user_data['password'] = hashed_password
    
    # Write back updated users
    with open('app/auth/users.json', 'w') as f:
        json.dump(users, f, indent=4)

if __name__ == '__main__':
    update_passwords()
    print("Passwords have been updated with secure hashes.") 