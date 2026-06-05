from datetime import datetime

users = {
    "admin": ("123", True),
    "user": ("111", False)
}

posts = []

username = input("Username: ")
password = input("Password: ")

if username not in users or users[username][0] != password:
    print("Wrong login")
    exit()

print("Login success!")

while True:
    print("\n1. Create Post")
    print("2. View Posts")
    print("3. Search by Username (staff only)")
    print("4. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        title = input("Title: ")
        desc = input("Description: ")
        date = datetime.now()

        posts.append([username, title, desc, date])
        print("Post added!")

    elif choice == "2":
        for p in posts:
            print("\nUser:", p[0])
            print("Title:", p[1])
            print("Date:", p[3])
            print("Desc:", p[2])

    elif choice == "3":
        if not users[username][1]:
            print("Only staff allowed!")
        else:
            name = input("Enter username: ")
            for p in posts:
                if p[0] == name:
                    print("\nTitle:", p[1])
                    print("Desc:", p[2])

    elif choice == "4":
        break

    else:
        print("Invalid choice")