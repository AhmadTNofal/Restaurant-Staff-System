import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
import mysql.connector
from tkinter import messagebox

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

def select_branch_close():
    window.destroy()

def invalid_screen():

     #Create a new window for displaying invalid credentials message
    invalid_window = tk.Tk()
    invalid_window.title("Invalid Credentials")
    invalid_window.geometry("250x100")
    # Message label
    invalid_label = tk.Label(invalid_window, text="Invalid Credentials. Please try again.", fg="red")
    invalid_label.pack(pady=10)
    # OK button to close the window
    ok_button = tk.Button(invalid_window, text="OK", command=invalid_window.destroy, **buttonStyle)
    ok_button.pack()
    # Run the invalid credentials window
    invalid_window.mainloop()

def add_branch_window(parent_window):
    parent_window.withdraw()

    new_branch_window = tk.Toplevel(window)
    new_branch_window.title("Add New Branch")

    # Entry for City
    tk.Label(new_branch_window, text="City:", **labelStyle).pack(pady=5)
    city_entry = tk.Entry(new_branch_window, **entryStyle)
    city_entry.pack(pady=5)

    # Entry for PostCode
    tk.Label(new_branch_window, text="PostCode:", **labelStyle).pack(pady=5)
    postcode_entry = tk.Entry(new_branch_window, **entryStyle)
    postcode_entry.pack(pady=5)

    # Entry for NumberOfTables
    tk.Label(new_branch_window, text="Number of Tables:", **labelStyle).pack(pady=5)
    num_tables_entry = tk.Entry(new_branch_window, **entryStyle)
    num_tables_entry.pack(pady=5)

    save_button = tk.Button(new_branch_window, text="Save Branch", command=lambda: save_new_branch(city_entry.get(), postcode_entry.get(), num_tables_entry.get(), new_branch_window), **buttonStyle)
    save_button.pack(pady=10)

    back_button = tk.Button(new_branch_window, text="Back", command=lambda: [new_branch_window.destroy(), parent_window.deiconify()], **buttonStyle)
    back_button.pack(pady=10)

def remove_branch(branch_info, parent_window):
    try:
        city, postcode = branch_info.split(", ")
        cursor = db.cursor(buffered=True)

        # First, delete all staff associated with this branch
        delete_staff_query = """
            DELETE FROM Account 
            WHERE BranchID IN (
                SELECT BranchID 
                FROM Branch 
                WHERE City = %s AND PostCode = %s
            )
        """
        cursor.execute(delete_staff_query, (city, postcode))
        
        # Then, delete the branch
        delete_branch_query = "DELETE FROM Branch WHERE City = %s AND PostCode = %s"
        cursor.execute(delete_branch_query, (city, postcode))

        db.commit()
        tk.messagebox.showinfo("Success", f"Branch in {city}, {postcode} and all associated staff successfully removed.")
        parent_window.destroy()
        select_branch()
    except Exception as e:
        tk.messagebox.showerror("Error", str(e))
        db.rollback()

def get_next_branch_id():
    cursor = db.cursor(buffered=True)
    cursor.execute("SELECT * FROM group1_asd.branch ORDER BY CAST(SUBSTRING(BranchID, 2) AS UNSIGNED) DESC;")
    last_branch_id_result = cursor.fetchone()
    if last_branch_id_result:
        last_branch_id = last_branch_id_result[0]  
        last_num = int(last_branch_id[1:])
        new_num = last_num + 1
        return f"B{new_num}"
    else:
        return "B1"

def save_new_branch(city, postcode, num_tables, new_branch_window):
    try:
        new_branch_id = get_next_branch_id()
        num_tables = int(num_tables)
        cursor = db.cursor(buffered=True)
        insert_query = "INSERT INTO Branch (BranchID, City, PostCode, NumberOfTables) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (new_branch_id, city, postcode, num_tables))
        db.commit()
        tk.messagebox.showinfo("Success", f"Branch {new_branch_id} successfully added.")
        new_branch_window.destroy()
        select_branch()
    except ValueError:
        tk.messagebox.showerror("Error", "Number of tables must be an integer.")
    except Exception as e:
        tk.messagebox.showerror("Error", str(e))
        db.rollback()  # Rollback in case of error

def show_staff(selected_branch_info, role, previous_window):
    # Close the previous window (staff roles window)
    previous_window.destroy()

    staff_window = tk.Toplevel(window)
    city, postcode = selected_branch_info.split(", ")
    staff_window.title(f"{role} in {city} - {postcode}")

    cursor = db.cursor(buffered=True)
    staff_query = """
        SELECT AccountID, ForeName, SurName 
        FROM Account 
        JOIN Branch ON Account.BranchID = Branch.BranchID 
        WHERE Branch.City = %s AND Branch.PostCode = %s AND Account.Role = %s
    """
    cursor.execute(staff_query, (city, postcode, role))
    staff_results = cursor.fetchall()

    if staff_results:
        for idx, (account_id, forename, surname) in enumerate(staff_results):
            tk.Label(staff_window, text=f"{account_id}. {forename} {surname}", font=fontStyle).pack(pady=2)
    else:
        tk.Label(staff_window, text=f"No staff found for role '{role}' at {city} - {postcode}.", font=fontStyle).pack(pady=10)

    # Back button to return to the staff roles window
    back_button = tk.Button(staff_window, text="Back", command=lambda: [staff_window.destroy(), open_staff_roles_window(selected_branch_info)], **buttonStyle)
    back_button.pack()

def open_staff_roles_window(selected_branch_info):
    staff_roles_window = tk.Toplevel(window)
    staff_roles_window.title(f"Staff Roles - {selected_branch_info}")

    heading_roles_frame = tk.Frame(staff_roles_window)
    heading_roles_frame.pack(side=tk.TOP, pady=10)

    heading_roles_label = tk.Label(heading_roles_frame, text="Staff Roles", font=('Helvetica', 16, 'bold'))
    heading_roles_label.pack(side=tk.LEFT, padx=10)

    buttons_frame = tk.Frame(staff_roles_window)
    buttons_frame.pack(side=tk.TOP, pady=10)
    back_button = tk.Button(staff_roles_window, text="Back", command=lambda: [staff_roles_window.destroy(), select_branch()], **buttonStyle)
    back_button.pack(side=tk.BOTTOM, pady=10)

    def button_click(role):
        show_staff(selected_branch_info, role, staff_roles_window)

    button_waiting_staff = tk.Button(buttons_frame, text="Waiting Staff", command=lambda: button_click("Waiting Staff"), font=('Helvetica', 12, 'bold'), height=2, width=15)
    button_manager = tk.Button(buttons_frame, text="Manager", command=lambda: button_click("Manager"), font=('Helvetica', 12, 'bold'), height=2, width=15)
    button_kitchen_staff = tk.Button(buttons_frame, text="Kitchen Staff", command=lambda: button_click("Kitchen Staff"), font=('Helvetica', 12, 'bold'), height=2, width=15)
    
    button_waiting_staff.pack(side=tk.LEFT, padx=10)
    button_manager.pack(side=tk.LEFT, padx=10)
    button_kitchen_staff.pack(side=tk.LEFT, padx=10)

def select_branch():
    window.withdraw()

    hr_options_window = tk.Toplevel(window)
    hr_options_window.title("HR Director Branches")
    hr_options_window.geometry("400x400")  # Adjusted for better layout

    cursor = db.cursor(buffered=True)
    branch_query = "SELECT City, PostCode FROM Branch"
    cursor.execute(branch_query)
    branch_results = cursor.fetchall()

    branch_names = sorted([f"{city}, {postcode}" for city, postcode in branch_results])

    selected_branch = tk.StringVar(hr_options_window)
    selected_branch.set(branch_names[0] if branch_names else "")

    # Dropdown for selecting a branch
    branch_dropdown = tk.OptionMenu(hr_options_window, selected_branch, *branch_names)
    branch_dropdown.pack(pady=10)

    def select_branch():
        chosen_branch_info = selected_branch.get()
        open_staff_roles_window(chosen_branch_info)
        hr_options_window.destroy()

    select_branch_button = tk.Button(hr_options_window, text="Select Branch", command=select_branch, **buttonStyle)
    select_branch_button.pack(pady=10)

    # Separator
    ttk.Separator(hr_options_window, orient='horizontal').pack(fill='x', pady=10)

    # Dropdown for removing a branch
    selected_remove_branch = tk.StringVar(hr_options_window)
    selected_remove_branch.set(branch_names[0] if branch_names else "")
    
    add_branch_button = tk.Button(hr_options_window, text="Add New Branch", command=lambda: add_branch_window(hr_options_window), **buttonStyle)
    add_branch_button.pack(pady=10)
    ttk.Separator(hr_options_window, orient='horizontal').pack(fill='x', pady=10)
    remove_branch_dropdown = tk.OptionMenu(hr_options_window, selected_remove_branch, *branch_names)
    remove_branch_dropdown.pack(pady=10)

    remove_branch_button = tk.Button(hr_options_window, text="Remove Branch", command=lambda: remove_branch(selected_remove_branch.get(), hr_options_window), **buttonStyle)
    remove_branch_button.pack(pady=10)

    hr_options_window.protocol("WM_DELETE_WINDOW", select_branch_close)
    
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
            if role == 'Director':
                select_branch()
            else:
                print(f"Login successful! Role: {role}")
                # Here, you would redirect to other role-specific interfaces
        else:
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

