import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
import mysql.connector
from tkinter import messagebox

# Initialize the main window
window = tk.Tk()
window.state('zoomed')
# window.attributes('-fullscreen', True)  # Uncomment this for Linux/Mac

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
    new_branch_window.state("zoomed")
    # new_branch_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

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

def show_staff(selected_branch_info):
    all_staff_window = tk.Toplevel(window)
    city, postcode = selected_branch_info.split(", ")
    all_staff_window.title(f"All Staff in {city} - {postcode}")

    cursor = db.cursor(buffered=True)
    all_staff_query = """
        SELECT Account.AccountID, Account.ForeName, Account.SurName, Account.Role
        FROM Account
        JOIN Branch ON Account.BranchID = Branch.BranchID
        WHERE Branch.City = %s AND Branch.PostCode = %s
    """
    cursor.execute(all_staff_query, (city, postcode))
    all_staff_results = cursor.fetchall()

    if all_staff_results:
        for account_id, forename, surname, role in all_staff_results:
            tk.Label(all_staff_window, text=f"{account_id}. {forename} {surname} - {role}", font=fontStyle).pack(pady=2)
    else:
        tk.Label(all_staff_window, text=f"No staff found in {city} - {postcode}.", font=fontStyle).pack(pady=10)

    back_button = tk.Button(all_staff_window, text="Back", command=all_staff_window.destroy, **buttonStyle)
    back_button.pack(pady=10)

def manager_options(selected_branch_info, previous_window):
    # Close the previous window (staff roles window)
    previous_window.destroy()

    manager_options_window = tk.Toplevel(window)
    manager_options_window.title(f"Manager Options - {selected_branch_info}")
    manager_options_window.state('zoomed')
    # manager_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

    # Define functionalities for each button (placeholder functions)
    def show_all_staff():
        all_staff_window = tk.Toplevel(window)
        all_staff_window.title("All Staff")
        all_staff_window.state('zoomed')
        # all_staff_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

        cursor = db.cursor(buffered=True)
        all_staff_query = """
            SELECT AccountID, ForeName, SurName, Role
            FROM Account
        """
        cursor.execute(all_staff_query)
        all_staff_results = cursor.fetchall()

        if all_staff_results:
            for account_id, forename, surname, role in all_staff_results:
                tk.Label(all_staff_window, text=f"{account_id}. {forename} {surname} - {role}", font=fontStyle).pack(pady=2)
        else:
            tk.Label(all_staff_window, text="No staff found.", font=fontStyle).pack(pady=10)

        back_button = tk.Button(all_staff_window, text="Back", command=all_staff_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

    def add_staff():
        add_staff_window = tk.Toplevel(window)
        add_staff_window.title("Add Staff")
        add_staff_window.state('zoomed')
        # add_staff_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

        # Entry fields for staff details
        forename_label = tk.Label(add_staff_window, text="Forename:", font=fontStyle)
        forename_label.pack()
        forename_entry = tk.Entry(add_staff_window, font=fontStyle)
        forename_entry.pack()

        surname_label = tk.Label(add_staff_window, text="Surname:", font=fontStyle)
        surname_label.pack()
        surname_entry = tk.Entry(add_staff_window, font=fontStyle)
        surname_entry.pack()

        email_label = tk.Label(add_staff_window, text="Email:", font=fontStyle)
        email_label.pack()
        email_entry = tk.Entry(add_staff_window, font=fontStyle)
        email_entry.pack()

        # Password entry with hidden input
        password_label = tk.Label(add_staff_window, text="Password:", font=fontStyle)
        password_label.pack()
        password_entry = tk.Entry(add_staff_window, font=fontStyle, show="*")
        password_entry.pack()

        # Dropdown for role selection
        role_label = tk.Label(add_staff_window, text="Role:", font=fontStyle)
        role_label.pack()
        role_var = tk.StringVar(add_staff_window)
        role_options = ['Manager', 'Waiting Staff', 'Kitchen Staff']
        role_var.set(role_options[0])  # set default value
        role_dropdown = tk.OptionMenu(add_staff_window, role_var, *role_options)
        role_dropdown.pack()

        # Submit function
        def submit_staff_details():
            forename = forename_entry.get()
            surname = surname_entry.get()
            email = email_entry.get()
            password = password_entry.get()
            role = role_var.get()
            city, postcode = selected_branch_info.split(", ")

            # Generate Account ID based on role
            account_id_prefix = {'Manager': 'M', 'Waiting Staff': 'W', 'Kitchen Staff': 'K'}
            prefix = account_id_prefix[role]

            # Find the last account ID for the selected role and increment it
            find_last_id_query = f"SELECT MAX(AccountID) FROM Account WHERE AccountID LIKE '{prefix}%'"
            cursor = db.cursor()
            cursor.execute(find_last_id_query)
            last_id_row = cursor.fetchone()
            last_id = last_id_row[0] if last_id_row and last_id_row[0] else prefix + "0"
            new_id_number = int(last_id.lstrip(prefix)) + 1
            new_account_id = prefix + str(new_id_number)

            # Insert into database (adjust according to your schema)
            insert_query = """
                INSERT INTO Account (AccountID, ForeName, SurName, Email, Password, Role, BranchID)
                SELECT %s, %s, %s, %s, %s, %s, Branch.BranchID
                FROM Branch
                WHERE Branch.City = %s AND Branch.PostCode = %s
            """
            try:
                cursor.execute(insert_query, (new_account_id, forename, surname, email, password, role, city, postcode))
                db.commit()
                messagebox.showinfo("Success", f"Account for {forename} {surname} (ID: {new_account_id}) has been successfully created.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                add_staff_window.destroy()

        submit_button = tk.Button(add_staff_window, text="Submit", command=submit_staff_details, **buttonStyle)
        submit_button.pack()
        back_button = tk.Button(add_staff_window, text="Back", command=add_staff_window.destroy, **buttonStyle)
        back_button.pack(pady=10)


    def remove_staff():
        remove_staff_window = tk.Toplevel(window)
        remove_staff_window.title("Remove Staff")
        remove_staff_window.state('zoomed')
        # remove_staff_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

        # Fetch staff details from the database
        staff_query = """
            SELECT AccountID, ForeName, SurName
            FROM Account
            JOIN Branch ON Account.BranchID = Branch.BranchID
            WHERE Branch.City = %s AND Branch.PostCode = %s
        """
        city, postcode = selected_branch_info.split(", ")
        cursor = db.cursor()
        cursor.execute(staff_query, (city, postcode))
        staff_results = cursor.fetchall()

        # Create a list of staff for the dropdown
        staff_list = [f"{row[0]}: {row[1]} {row[2]}" for row in staff_results] if staff_results else []

        if staff_list:
            staff_var = tk.StringVar(remove_staff_window)
            staff_var.set(staff_list[0])  # Set default value
            staff_dropdown = tk.OptionMenu(remove_staff_window, staff_var, *staff_list)
            staff_dropdown.pack()

            def remove_selected_staff():
                selected = staff_var.get().split(":")[0]  # Extract AccountID
                delete_query = "DELETE FROM Account WHERE AccountID = %s"
                try:
                    cursor.execute(delete_query, (selected,))
                    db.commit()
                    messagebox.showinfo("Success", f"Staff member with ID {selected} has been removed.")
                    remove_staff_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")

            remove_button = tk.Button(remove_staff_window, text="Remove Staff", command=remove_selected_staff, **buttonStyle)
            remove_button.pack()
            back_button = tk.Button(remove_staff_window, text="Back", command=remove_staff_window.destroy, **buttonStyle)
            back_button.pack(pady=10)
        else:
            tk.Label(remove_staff_window, text="No staff found to remove.", font=fontStyle).pack()
            back_button = tk.Button(remove_staff_window, text="Back", command=remove_staff_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

    def show_reports():
        pass  # Implement the functionality

    # Create buttons
    show_all_staff_button = tk.Button(manager_options_window, text="Show all staff", command=lambda: show_staff(selected_branch_info), **buttonStyle)
    add_staff_button = tk.Button(manager_options_window, text="Add staff", command=add_staff, **buttonStyle)
    remove_staff_button = tk.Button(manager_options_window, text="Remove staff", command=remove_staff, **buttonStyle)
    show_reports_button = tk.Button(manager_options_window, text="Show reports", command=show_reports, **buttonStyle)

    # Pack buttons
    show_all_staff_button.pack(pady=5)
    add_staff_button.pack(pady=5)
    remove_staff_button.pack(pady=5)
    show_reports_button.pack(pady=5)

    back_button = tk.Button(manager_options_window, text="Back", command=lambda: [manager_options_window.destroy(), open_staff_roles_window(selected_branch_info)], **buttonStyle)
    back_button.pack(pady=10)

def open_staff_roles_window(selected_branch_info):
    staff_roles_window = tk.Toplevel(window)
    staff_roles_window.title(f"Staff Roles - {selected_branch_info}")
    staff_roles_window.state('zoomed')
    # staff_roles_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
    
    heading_roles_frame = tk.Frame(staff_roles_window)
    heading_roles_frame.pack(side=tk.TOP, pady=10)

    heading_roles_label = tk.Label(heading_roles_frame, text="Staff Roles", font=('Helvetica', 16, 'bold'))
    heading_roles_label.pack(side=tk.LEFT, padx=10)

    buttons_frame = tk.Frame(staff_roles_window)
    buttons_frame.pack(side=tk.TOP, pady=10)
    back_button = tk.Button(staff_roles_window, text="Back", command=lambda: [staff_roles_window.destroy(), select_branch()], **buttonStyle)
    back_button.pack(side=tk.BOTTOM, pady=10)

    def button_click(role):
        if role == "Manager":
            manager_options(selected_branch_info, staff_roles_window)
        else:
            show_staff(selected_branch_info, role, staff_roles_window)

    button_waiting_staff = tk.Button(buttons_frame, text="Waiting Staff", command=lambda: button_click("Waiting Staff"), font=('Helvetica', 12, 'bold'), height=2, width=15)
    button_manager = tk.Button(buttons_frame, text="Manager", command=lambda: button_click("Manager"), font=('Helvetica', 12, 'bold'), height=2, width=15)
    button_kitchen_staff = tk.Button(buttons_frame, text="Kitchen Staff", command=lambda: button_click("Kitchen Staff"), font=('Helvetica', 12, 'bold'), height=2, width=15)
    
    button_manager.pack(side=tk.LEFT, padx=10)
    button_waiting_staff.pack(side=tk.LEFT, padx=10)
    button_kitchen_staff.pack(side=tk.LEFT, padx=10)

def select_branch():
    window.withdraw()

    hr_options_window = tk.Toplevel(window)
    hr_options_window.title("HR Director Branches")
    hr_options_window.state('zoomed')
    # hr_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

    cursor = db.cursor(buffered=True)
    branch_query = "SELECT City, PostCode FROM Branch WHERE NOT BranchID = 'BM'"
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

