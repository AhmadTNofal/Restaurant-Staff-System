import tkinter as tk
import mysql.connector

# Connect to the database
db = mysql.connector.connect(
    host="mysqldevoyard.mysql.database.azure.com",
    user="admintest",
    password="P@ssw0rd",
    database="group1_asd"
)
#invalid credentials screen

window = tk.Tk()

def invalid_screen():
    # Create a new window for displaying invalid credentials message
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
    # Create a new window for HR director options
    hr_options_window = tk.Toplevel(window)
    hr_options_window.title("HR Director branches")
    hr_options_window.geometry("400x300")
    
    # Retrieve branch data from the database
    cursor = db.cursor(buffered=True)
    branch_query = "SELECT City, Postcode FROM Branch"
    cursor.execute(branch_query)
    branch_results = cursor.fetchall()

    # Create a list of branch names in the format "City, Postcode"
    branch_names = [f"{city}, {postcode}" for city, postcode in branch_results]

    # Create the dropdown list
    selected_branch = tk.StringVar(hr_options_window)
    selected_branch.set(branch_names[0])  # Set the default selected branch

    # Function to update the dropdown list based on user input
    def update_dropdown(*args):
        search_term = selected_branch.get()
        filtered_branches = [branch for branch in branch_names if search_term.lower() in branch.lower()]
        branch_dropdown['menu'].delete(0, 'end')
        for branch in filtered_branches:
            branch_dropdown['menu'].add_command(label=branch, command=tk._setit(selected_branch, branch))

    # Create the dropdown list with autocomplete feature
    branch_dropdown = tk.OptionMenu(hr_options_window, selected_branch, *branch_names, command=update_dropdown)
    branch_dropdown.pack()

    # Select branch button
    select_branch_button = tk.Button(hr_options_window, text="Select Branch", command=lambda: print(selected_branch.get()))
    select_branch_button.pack()

    # Run the HR options window
    hr_options_window.mainloop()
    
# Create the login screen
def login_screen():
    def login():
        email = username_entry.get()
        password = password_entry.get()

        # Start with checking the Account table for email and password
        cursor = db.cursor(buffered=True)
        account_query = "SELECT Role FROM Account WHERE Email = %s AND Password = %s"
        cursor.execute(account_query, (email, password))
        account_result = cursor.fetchone()

        if account_result:
            # Role found in the Account table
            role = account_result[0]
            print(f"Login successful! Role: {role}")
            
            # Redirect or load the interface based on the role
            if role == 'Director':
                open_hr_options_window()
            # elif role == 'Staff':
            #     # Load Staff interface
            # elif role == 'Customer':
            #     # Load Customer interface
            # Add your role-based redirection or interface loading code here
        else:
            # Invalid credentials
            print("Invalid email or password")
            
            # create a invalid credentials screen
            invalid_screen()

    # Create the login window
    
    window.title("Login")
    window.geometry("350x220")

    # Username label and text entry
    username_label = tk.Label(window, text="Email:")
    username_label.pack()
    username_entry = tk.Entry(window, width=30)
    username_entry.pack()

    # Password label and text entry
    password_label = tk.Label(window, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(window, show="*", width=30)
    password_entry.pack()

    # Login button
    login_button = tk.Button(window, text="Login", command=login)
    login_button.pack()

    # Run the login window
    window.mainloop()

# Run the login screen
login_screen()
