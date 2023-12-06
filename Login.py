import tkinter as tk
import tkinter.font as tkFont
import mysql.connector

# Initialize the main window
window = tk.Tk()

# Create font styles after initializing the main window
fontStyle = tkFont.Font(family="Arial", size=12)
buttonStyle = {"font": fontStyle, "bg": "blue", "fg": "white"}
labelStyle = {"font": fontStyle, "fg": "black"}
entryStyle = {"font": fontStyle, "fg": "black", "bd": 2}

# Connect to the database
db = mysql.connector.connect(
    host="mysqldevoyard.mysql.database.azure.com",
    user="admintest",
    password="P@ssw0rd",
    database="group1_asd"
)

def invalid_screen():
    #Create a new window for displaying invalid credentials message
    invalid_window = tk.Tk()
    invalid_window.title("Invalid Credentials")
    invalid_window.geometry("250x100")

    # Message label
    invalid_label = tk.Label(invalid_window, text="Invalid Credentials. Please try again.", fg="red")
    invalid_label.pack(pady=10)

    # OK button to close the window
    ok_button = tk.Button(invalid_window, text="OK", command=invalid_window.destroy)
    ok_button.pack()

    # Run the invalid credentials window
    invalid_window.mainloop()

def open_hr_options_window():
    hr_options_window = tk.Toplevel(window)
    hr_options_window.title("HR Director branches")
    hr_options_window.geometry("400x300")
    
    cursor = db.cursor(buffered=True)
    branch_query = "SELECT City, Postcode FROM Branch"
    cursor.execute(branch_query)
    branch_results = cursor.fetchall()

    branch_names = [f"{city}, {postcode}" for city, postcode in branch_results]

    selected_branch = tk.StringVar(hr_options_window)
    selected_branch.set(branch_names[0])

    def update_dropdown(*args):
        search_term = selected_branch.get()
        filtered_branches = [branch for branch in branch_names if search_term.lower() in branch.lower()]
        branch_dropdown['menu'].delete(0, 'end')
        for branch in filtered_branches:
            branch_dropdown['menu'].add_command(label=branch, command=tk._setit(selected_branch, branch))

    branch_dropdown = tk.OptionMenu(hr_options_window, selected_branch, *branch_names, command=update_dropdown)
    branch_dropdown.pack(pady=10)

    select_branch_button = tk.Button(hr_options_window, text="Select Branch", command=lambda: print(selected_branch.get()), **buttonStyle)
    select_branch_button.pack(pady=10)

    hr_options_window.mainloop()
    
def login_screen():
    def login():
        email = username_entry.get()
        password = password_entry.get()

        cursor = db.cursor(buffered=True)
        account_query = "SELECT Role FROM Account WHERE Email = %s AND Password = %s"
        cursor.execute(account_query, (email, password))
        account_result = cursor.fetchone()

        if account_result:
            role = account_result[0]
            print(f"Login successful! Role: {role}")
            if role == 'Director':
                open_hr_options_window()
        else:
            print("Invalid email or password")
            invalid_screen()

    window.title("Login")
    window.geometry("350x220")

    username_label = tk.Label(window, text="Email:", **labelStyle)
    username_label.pack(pady=5)
    username_entry = tk.Entry(window, width=30, **entryStyle)
    username_entry.pack(pady=5)

    password_label = tk.Label(window, text="Password:", **labelStyle)
    password_label.pack(pady=5)
    password_entry = tk.Entry(window, show="*", width=30, **entryStyle)
    password_entry.pack(pady=5)

    login_button = tk.Button(window, text="Login", command=login, **buttonStyle)
    login_button.pack(pady=10)

    window.mainloop()

login_screen()

