import tkinter as tk
import tkinter.font as tkFont
import sqlite3
from tkinter import ttk
import mysql.connector
from tkinter import messagebox
from PIL import Image, ImageTk
from PIL import Image, ImageEnhance
from decimal import Decimal, InvalidOperation
import datetime

tree=None
tree = None
stock_id_label = None
stock_type_label = None
amount_in_stock_label = None
price_label = None
# Initialize the main window
window = tk.Tk()
window.state('zoomed')
# window.attributes('-fullscreen', True)  # Uncomment this for Linux/Mac

# Create font styles after initializing the main window
fontStyle = tkFont.Font(family="Segoe UI", size=12)

# Soft color scheme with consistent border and relief
soft_grey = "#f0f0f0"
dark_grey = "#303030"

buttonStyle = {
    "font": fontStyle, 
    "bg": dark_grey, 
    "fg": soft_grey, 
    "bd": 2, 
    "relief": "groove",
    "padx": 5,
    "pady": 5
}

labelStyle = {
    "font": fontStyle, 
    "fg": dark_grey,
    "bg": "white"
}

entryStyle = {
    "font": fontStyle, 
    "fg": dark_grey, 
    "bd": 2, 
    "insertbackground": dark_grey  # Changes cursor color
}

# Connect to the database
db = mysql.connector.connect(
    host="mysqldevoyard.mysql.database.azure.com",
    user="admintest",
    password="P@ssw0rd",
    database="group1_asd"
)
widget.pack(anchor='center')
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

        # First, retrieve the BranchID based on the city and postcode
        get_branch_id_query = "SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s"
        cursor.execute(get_branch_id_query, (city, postcode))
        branch_result = cursor.fetchone()
        if branch_result:
            branch_id = branch_result[0]

            # Then, delete all tables associated with this branch
            delete_tables_query = "DELETE FROM Tables WHERE BranchID = %s"
            cursor.execute(delete_tables_query, (branch_id,))

        # Then, delete the branch itself
        delete_branch_query = "DELETE FROM Branch WHERE City = %s AND PostCode = %s"
        cursor.execute(delete_branch_query, (city, postcode))

        db.commit()
        tk.messagebox.showinfo("Success", f"Branch in {city}, {postcode} and all associated tables successfully removed.")
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

def add_tables_for_branch(branch_id, num_tables, cursor):
    for i in range(1, num_tables + 1):
        table_id = f"{branch_id}-T{i}"
        cursor.execute("INSERT INTO Tables (TableID, BranchID) VALUES (%s, %s)", (table_id, branch_id))

def save_new_branch(city, postcode, num_tables_str, new_branch_window):
    try:
        # Get the next branch ID
        new_branch_id = get_next_branch_id()
        
        # Convert the number of tables to an integer
        num_tables = int(num_tables_str)
        
        # Insert the new branch into the Branch table
        cursor = db.cursor()
        insert_query = "INSERT INTO Branch (BranchID, City, PostCode, NumberOfTables) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (new_branch_id, city, postcode, num_tables))
        
        # Add tables for the new branch
        add_tables_for_branch(new_branch_id, num_tables, cursor)
        
        # Commit the changes to the database
        db.commit()
        tk.messagebox.showinfo("Success", f"Branch {new_branch_id} successfully added with {num_tables} tables.")
        new_branch_window.destroy()
        select_branch()
    except ValueError:
        tk.messagebox.showerror("Error", "Number of tables must be an integer.")
    except mysql.connector.Error as err:
        tk.messagebox.showerror("Error", f"Database error: {err}")
        db.rollback()  # Rollback in case of error
    except Exception as e:
        tk.messagebox.showerror("Error", str(e))
        db.rollback()  # Rollback in case of error
    finally:
        if cursor is not None:
            cursor.close()

def show_staff(selected_branch_info):
    all_staff_window = tk.Toplevel(window)
    def help_on_enter(e):
            help_button.config(bg='gray')  # Change color on hover

    def help_on_leave(e):
        help_button.config(bg='lightgrey') 
    def open_help():
        help_window = tk.Toplevel(window)
        help_window.title("Help")
        help_window.geometry("400x300")  # Adjust size as needed

        # Text area for comments
        comment_text = tk.Text(help_window, height=10, width=40)
        comment_text.pack(pady=10)
        def submit_comment():
            comment = comment_text.get("1.0", "end-1c")
            print("Comment submitted:", comment)  # Replace with actual processing logic
            help_window.destroy()
        submit_button = tk.Button(help_window, text="Submit Comment", command=submit_comment)
        submit_button.pack(pady=10)
    hr_options_window = tk.Toplevel(window)
    hr_options_window.title("HR Director Branches")
    hr_options_window.state('zoomed')

    # hr_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
    top_border = tk.Canvas(hr_options_window, height=50, bg='black')
    top_border.pack(side='top', fill='x')    
    main_frame = tk.Frame(hr_options_window)
    main_frame.pack(padx=20, pady=20)
    title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
    title_label.pack(pady=(0, 10))
    help_font = tkFont.Font(family="Arial", size=25, weight="bold")
    help_button = tk.Button(top_border, text="Help", command=open_help, font=help_font, bg='white', relief='groove', bd=2)
    help_button.pack(side='right', padx=10, pady=5)
    help_button.bind("<Enter>", help_on_enter)
    help_button.bind("<Leave>", help_on_leave)
    center_frame = tk.Frame(hr_options_window)
    center_frame.pack(expand=True)
    center_frame.grid_columnconfigure(0, weight=1)
    logo_image = Image.open("restt.png")  # Replace with your logo path
    logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
    logo_label.image = logo_photo  # Keep a reference
    logo_label.pack(side='left', padx=10, pady=5)
    
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


    # hr_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
    top_border = tk.Canvas(manager_options_window, height=50, bg='black')
    top_border.pack(side='top', fill='x')    
    main_frame = tk.Frame(manager_options_window)
    main_frame.pack(padx=20, pady=20)
    title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
    title_label.pack(pady=(0, 10))
    center_frame = tk.Frame(manager_options_window)
    center_frame.pack(expand=True)
    center_frame.grid_columnconfigure(0, weight=1)
    logo_image = Image.open("restt.png")  # Replace with your logo path
    logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
    logo_label.image = logo_photo  # Keep a reference
    logo_label.pack(side='left', padx=10, pady=5)
    # manager_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
    def calculate_branch_cost():
        city, postcode = selected_branch_info.split(", ")
        
        # Get the branch id
        cursor = db.cursor()
        cursor.execute("SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s", (city, postcode))
        branch_id = cursor.fetchone()[0]

        # Get the total cost of all stock
        cursor.execute("SELECT SUM(AmountInStock * Price) FROM Stock WHERE BranchID = %s", (branch_id,))
        total_stock_cost = cursor.fetchone()[0] or 0

        #today's date
        today = datetime.date.today()

        # current time
        now = datetime.datetime.now()

        # Create window to enter cost details
        cost_window = tk.Toplevel(window)
        cost_window.title("Enter Cost Details")
        cost_window.state('zoomed')
        # cost_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

        # Utility Cost entry
        utility_cost_label = tk.Label(cost_window, text="Utility Cost:", font=fontStyle)
        utility_cost_label.pack(pady=(10, 0))
        utility_cost_entry = tk.Entry(cost_window, font=fontStyle)
        utility_cost_entry.pack(pady=(0, 10))

        # Wages entry
        wages_label = tk.Label(cost_window, text="Wages:", font=fontStyle)
        wages_label.pack(pady=(10, 0))
        wages_entry = tk.Entry(cost_window, font=fontStyle)
        wages_entry.pack(pady=(0, 20))

        # Submit function
        def submit_cost_details():
            try:
                utility_cost = Decimal(utility_cost_entry.get())
                wages = Decimal(wages_entry.get())
                total_cost = total_stock_cost + utility_cost + wages

                # Generate Cost ID
                cursor.execute("SELECT CostID FROM Cost ORDER BY CAST(SUBSTRING(CostID, 2) AS UNSIGNED) DESC Limit 1;")
                last_cost_id_row = cursor.fetchone()
                last_cost_id = last_cost_id_row[0] if last_cost_id_row and last_cost_id_row[0] else "C0"
                new_cost_id_number = int(last_cost_id.lstrip("C")) + 1
                new_cost_id = "C" + str(new_cost_id_number)

                # Insert the cost details into the database
                insert_query = "INSERT INTO Cost (CostID, UtilityCost, Wages, StockCost, TotalCost, BranchID, Date, Time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (new_cost_id, utility_cost, wages, total_stock_cost, float(total_cost), branch_id, today, now))
                db.commit()
                messagebox.showinfo("Success", f"Cost {new_cost_id} successfully added. Total cost: £{total_cost}")
                cost_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for utility cost and wages.")
            except Exception as e:
                db.rollback()
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        submit_button = tk.Button(cost_window, text="Submit", command=submit_cost_details, **buttonStyle)
        submit_button.pack()

        back_button = tk.Button(cost_window, text="Back", command=cost_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

    def branch_report():
        previous_window.destroy()
        show_reports_window = tk.Toplevel(window)
        show_reports_window.title(f"Branch report - {selected_branch_info}")
        show_reports_window.state('zoomed')
        top_border = tk.Canvas(show_reports_window, height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(show_reports_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(show_reports_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        city, postcode = selected_branch_info.split(", ")

        stock_query = """
            SELECT StockID, StockType, AmountInStock, Price
            FROM Stock
            WHERE BranchID = (
                SELECT BranchID
                FROM Branch
                WHERE City = %s AND PostCode = %s
            )
        """
        cursor = db.cursor()
        cursor.execute(stock_query, (city, postcode))
        stock_results = cursor.fetchall()

        if stock_results:
            header_label = tk.Label(show_reports_window, text="Stock for this branch", font=('Helvetica', 14, 'bold'))
            header_label.pack(pady=10)
            for stock_id, stock_type, amount_in_stock, price in stock_results:
                stock_info = f"{stock_id}: {stock_type} - {amount_in_stock} in stock - £{price}"
                tk.Label(show_reports_window, text=stock_info, font=fontStyle).pack()
        else:
            header_label = tk.Label(show_reports_window, text="Empty Stock", font=('Helvetica', 14, 'bold'))
            header_label.pack(pady=10)

        #separator
        ttk.Separator(show_reports_window, orient='horizontal').pack(fill='x', pady=10)

        #heading for the total cost
        header_label = tk.Label(show_reports_window, text="Cost Details", font=('Helvetica', 14, 'bold'))
        header_label.pack(pady=10)
        
        #print cost details for the branch
        cursor = db.cursor()
        cursor.execute("SELECT CostID, UtilityCost, Wages, StockCost, TotalCost, Date, Time FROM Cost WHERE BranchID = (SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s)", (city, postcode))
        cost_details = cursor.fetchall()

        if cost_details:
            #show all costs not just the last order the cost by date and time 
            cost_details.sort(key=lambda x: (x[5], x[6]), reverse=True)
            for cost_id, utility_cost, wages, stock_cost, total_cost, date, time in cost_details:
                cost_info = f"{cost_id}: Utility Cost - £{utility_cost}, Wages - £{wages}, Stock Cost - £{stock_cost}, Total Cost - £{total_cost}, Date - {date}, Time - {time}"
                tk.Label(show_reports_window, text=cost_info, font=fontStyle).pack()
        else:
            tk.Label(show_reports_window, text="No cost details found.", font=fontStyle).pack()



        back_button = tk.Button(show_reports_window, text="Back", command=show_reports_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

    def staff_report():
        staff_report_window = tk.Toplevel(window)
        staff_report_window.title("Staff report")
        staff_report_window.state('zoomed')
        # staff_report_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
        top_border = tk.Canvas(staff_report_window, height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(staff_report_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(staff_report_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        #staff report title
        header_label = tk.Label(staff_report_window, text="Managers", font=('Helvetica', 14, 'bold'))
        header_label.pack(pady=10)

        # Extract the BranchID from the selected branch info
        city, postcode = selected_branch_info.split(", ")
        cursor = db.cursor()
        cursor.execute("SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s", (city, postcode))
        branch_id = cursor.fetchone()[0]
        cursor.close()

        # Fetch all managers for the branch
        cursor = db.cursor()
        cursor.execute("SELECT AccountID, ForeName, SurName FROM Account WHERE BranchID = %s AND Role = 'Manager'", (branch_id,))
        manager_results = cursor.fetchall()
        cursor.close()

        if manager_results:
            for account_id, forename, surname in manager_results:
                manager_info = f"{account_id}: {forename} {surname}"
                tk.Label(staff_report_window, text=manager_info, font=fontStyle).pack()
        else:
            tk.Label(staff_report_window, text="No managers found for this branch.", font=fontStyle).pack()

        #separator
        ttk.Separator(staff_report_window, orient='horizontal').pack(fill='x', pady=10)

        #Waiting staff report title
        header_label = tk.Label(staff_report_window, text="Waiting Staff", font=('Helvetica', 14, 'bold'))
        header_label.pack(pady=10)

        # Fetch all waiting staff for the branch
        cursor = db.cursor()
        cursor.execute("SELECT AccountID, ForeName, SurName, Points FROM Account WHERE BranchID = %s AND Role = 'Waiting Staff'", (branch_id,))
        waiting_staff_results = cursor.fetchall()
        cursor.close()

        if waiting_staff_results:
            #sort the staff by points
            waiting_staff_results.sort(key=lambda x: x[3], reverse=True)
            for account_id, forename, surname, points in waiting_staff_results:
                waiting_staff_info = f"{account_id}: {forename} {surname} - {points} points"
                tk.Label(staff_report_window, text=waiting_staff_info, font=fontStyle).pack()
        else:
            tk.Label(staff_report_window, text="No waiting staff found for this branch.", font=fontStyle).pack()

        #separator
        ttk.Separator(staff_report_window, orient='horizontal').pack(fill='x', pady=10)

        #Kitchen staff report title
        header_label = tk.Label(staff_report_window, text="Kitchen Staff", font=('Helvetica', 14, 'bold'))
        header_label.pack(pady=10)

        # Fetch all kitchen staff for the branch
        cursor = db.cursor()
        cursor.execute("SELECT AccountID, ForeName, SurName, Points FROM Account WHERE BranchID = %s AND Role = 'Kitchen Staff'", (branch_id,))
        kitchen_staff_results = cursor.fetchall()
        cursor.close()

        #sort the staff by points
        kitchen_staff_results.sort(key=lambda x: x[3], reverse=True)

        if kitchen_staff_results:
            for account_id, forename, surname, points in kitchen_staff_results:
                kitchen_staff_info = f"{account_id}: {forename} {surname} - {points} points"
                tk.Label(staff_report_window, text=kitchen_staff_info, font=fontStyle).pack()
        else:
            tk.Label(staff_report_window, text="No kitchen staff found for this branch.", font=fontStyle).pack()

        #reset the points of all staff
        def reset_points():
            cursor = db.cursor()
            cursor.execute("UPDATE Account SET Points = 0 WHERE BranchID = %s", (branch_id,))
            db.commit()
            messagebox.showinfo("Success", f"Points for all staff in {city} - {postcode} reset to 0.")
            staff_report_window.destroy()
            manager_options(selected_branch_info, previous_window)

        #separator
        ttk.Separator(staff_report_window, orient='horizontal').pack(fill='x', pady=10)

        #number of managers heading
        header_label = tk.Label(staff_report_window, text="Number of Staff", font=('Helvetica', 14, 'bold'))
        header_label.pack(pady=10)

        cursor = db.cursor()
        cursor.execute("SELECT AccountID, ForeName, SurName FROM Account WHERE BranchID = %s AND Role = 'Manager'", (branch_id,))
        manager_results = cursor.fetchall()
        cursor.close()

        # Print the number of managers
        number_of_managers = len(manager_results)
        tk.Label(staff_report_window, text=f"Number of Managers: {number_of_managers}", font=fontStyle).pack()

        #number of waiting staff heading
        cursor = db.cursor()
        cursor.execute("SELECT AccountID, ForeName, SurName FROM Account WHERE BranchID = %s AND Role = 'Waiting Staff'", (branch_id,))
        waiting_staff_results = cursor.fetchall()

        # Print the number of waiting staff
        number_of_waiting_staff = len(waiting_staff_results)
        tk.Label(staff_report_window, text=f"Number of Waiting Staff: {number_of_waiting_staff}", font=fontStyle).pack()

        #number of kitchen staff heading
        cursor = db.cursor()
        cursor.execute("SELECT AccountID, ForeName, SurName FROM Account WHERE BranchID = %s AND Role = 'Kitchen Staff'", (branch_id,))
        kitchen_staff_results = cursor.fetchall()

        # Print the number of kitchen staff
        number_of_kitchen_staff = len(kitchen_staff_results)
        tk.Label(staff_report_window, text=f"Number of Kitchen Staff: {number_of_kitchen_staff}", font=fontStyle).pack()

        #total number of staff heading
        total_number_of_staff = number_of_managers + number_of_waiting_staff + number_of_kitchen_staff

        # Print the total number of staff
        tk.Label(staff_report_window, text=f"Total Number of Staff: {total_number_of_staff}", font=fontStyle).pack()

        reset_points_button = tk.Button(staff_report_window, text="Reset Points", command=reset_points, **buttonStyle)
        reset_points_button.pack(pady=10)


        back_button = tk.Button(staff_report_window, text="Back", command=staff_report_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

    def show_reports():
        previous_window.destroy()

        stock_options_window = tk.Toplevel(window)
        stock_options_window.title(f"Reports - {selected_branch_info}")
        stock_options_window.state('zoomed')
        top_border = tk.Canvas(stock_options_window, height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(stock_options_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(stock_options_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        stock_center_frame = tk.Frame(stock_options_window)
        stock_center_frame.pack(expand=True)

        staff_report_button = tk.Button(stock_center_frame, text="Staff report", command= lambda: staff_report(),  font=('Helvetica', 12, 'bold'), height=2, width=15)
        branch_report_button = tk.Button(stock_center_frame, text="Branch report", command=lambda: branch_report(), font=('Helvetica', 12, 'bold'), height=2, width=15)

        staff_report_button.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        branch_report_button.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        stock_center_frame.grid_rowconfigure(0, weight=1)
        stock_center_frame.grid_columnconfigure(0, weight=1)
        stock_center_frame.grid_columnconfigure(1, weight=1)

        back_button = tk.Button(stock_options_window, text="Back", command=stock_options_window.destroy, **buttonStyle)
        back_button.pack(pady=10)
    
    def stock_options():
        # Close the previous window (manager options window)
        previous_window.destroy()
        
        stock_options_window = tk.Toplevel(window)
        stock_options_window.title(f"Stock Options - {selected_branch_info}")
        stock_options_window.state('zoomed')
        top_border = tk.Canvas(stock_options_window, height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(stock_options_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(stock_options_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        stock_center_frame = tk.Frame(stock_options_window)
        stock_center_frame.pack(expand=True)
        # stock_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

        # Define functionalities for each button 
        view_stock_button = tk.Button(stock_center_frame, text="View Stock", command=lambda: view_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
        add_stock_button = tk.Button(stock_center_frame, text="Add Stock", command=lambda: add_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
        remove_stock_button = tk.Button(stock_center_frame, text="Remove Stock", command=lambda: remove_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
        
        # Pack buttons in the center frame
        view_stock_button.grid(row=0, column=0, padx=10, pady=10)
        add_stock_button.grid(row=0, column=1, padx=10, pady=10)
        remove_stock_button.grid(row=0, column=2, padx=10, pady=10)

        # Back button to go back to the previous window
        back_button = tk.Button(stock_options_window, text="Back", command=stock_options_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

    def view_stock(selected_branch_info):
        view_stock_window = tk.Toplevel(window)
        view_stock_window.title("View Stock")
        view_stock_window.state('zoomed')
        top_border = tk.Canvas(view_stock_window, height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(view_stock_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(view_stock_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        # Extract city and postcode from the selected_branch_info
        city, postcode = selected_branch_info.split(", ")

        stock_query = """
            SELECT StockID, StockType, AmountInStock, Price
            FROM Stock
            WHERE BranchID = (
                SELECT BranchID
                FROM Branch
                WHERE City = %s AND PostCode = %s
            )
        """
        cursor = db.cursor()
        cursor.execute(stock_query, (city, postcode))
        stock_results = cursor.fetchall()

        if stock_results:
            for stock_id, stock_type, amount_in_stock, price in stock_results:
                stock_info = f"{stock_id}: {stock_type} - {amount_in_stock} in stock - £{price}"
                tk.Label(view_stock_window, text=stock_info, font=fontStyle).pack()
        else:
            tk.Label(view_stock_window, text="No stock found for this branch.", font=fontStyle).pack()

        back_button = tk.Button(view_stock_window, text="Back", command=view_stock_window.destroy, **buttonStyle)
        back_button.pack(pady=10)
    
    def add_stock(selected_branch_info):
        # Close the previous window (stock options window)
        previous_window.destroy()

        add_stock_window = tk.Toplevel(window)
        add_stock_window.title("Add Stock")
        add_stock_window.state('zoomed')
        # add_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
        top_border = tk.Canvas(add_stock_window, height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(add_stock_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(add_stock_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        # Extract city and postcode from the selected_branch_info
        city, postcode = selected_branch_info.split(", ")

        #get the branch id
        cursor = db.cursor()
        cursor.execute("SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s", (city, postcode))
        branch_id = cursor.fetchone()[0]


        # Entry fields for stock details
        stock_type_label = tk.Label(add_stock_window, text="Stock Type:", font=fontStyle)
        stock_type_label.pack()
        stock_type_entry = tk.Entry(add_stock_window, font=fontStyle)
        stock_type_entry.pack()

        amount_in_stock_label = tk.Label(add_stock_window, text="Amount in Stock:", font=fontStyle)
        amount_in_stock_label.pack()
        amount_in_stock_entry = tk.Entry(add_stock_window, font=fontStyle)
        amount_in_stock_entry.pack()

        price_label = tk.Label(add_stock_window, text="Price:", font=fontStyle)
        price_label.pack()
        price_entry = tk.Entry(add_stock_window, font=fontStyle)
        price_entry.pack()

        # Submit function
        def submit_stock_details():
            stock_type = stock_type_entry.get()
            amount_in_stock = amount_in_stock_entry.get()
            price = price_entry.get()

            # Generate Stock ID based on the last StockID
            cursor = db.cursor()
            cursor.execute("SELECT MAX(StockID) FROM Stock")
            last_stock_id_row = cursor.fetchone()
            last_stock_id = last_stock_id_row[0] if last_stock_id_row and last_stock_id_row[0] else "S0"
            new_stock_id_number = int(last_stock_id.lstrip("S")) + 1
            new_stock_id = "S" + str(new_stock_id_number)

            # Insert into database (adjust according to your schema)
            insert_query = """
                INSERT INTO Stock (StockID, StockType, AmountInStock, Price, BranchID)
                SELECT %s, %s, %s, %s, Branch.BranchID
                FROM Branch
                WHERE Branch.City = %s AND Branch.PostCode = %s
            """
            try:
                cursor.execute(insert_query, (new_stock_id, stock_type, amount_in_stock, price, city, postcode))
                db.commit()
                messagebox.showinfo("Success", f"Stock {new_stock_id} successfully added.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                add_stock_window.destroy()
                stock_options(selected_branch_info)

        submit_button = tk.Button(add_stock_window, text="Submit", command=submit_stock_details, **buttonStyle)
        submit_button.pack()
        back_button = tk.Button(add_stock_window, text="Back", command=add_stock_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

        # Separator
        ttk.Separator(add_stock_window, orient='horizontal').pack(fill='x', pady=10)

        #dropdown list of all available stock
        def get_available_stock(branch_id):
            cursor = db.cursor()
            cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s", (branch_id,))
            return cursor.fetchall()
        
        available_stock = get_available_stock(branch_id)

        stock_var = tk.StringVar(add_stock_window)
        stock_var.set("Select stock")
        stock_dropdown_label = tk.Label(add_stock_window, text="Select Stock:", font=fontStyle)
        stock_dropdown_label.pack()
        stock_dropdown = tk.OptionMenu(add_stock_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
        stock_dropdown.pack()

        # add ammoount to stock text box
        amount_to_add_label = tk.Label(add_stock_window, text="Amount to Add:", font=fontStyle)
        amount_to_add_label.pack()
        amount_to_add_entry = tk.Entry(add_stock_window, font=fontStyle)
        amount_to_add_entry.pack()

        #function to add stock
        def add_stock():
            selected_stock_id = stock_var.get().split(" - ")[0]
            amount_to_add = amount_to_add_entry.get()

            if selected_stock_id.startswith("Select"):
                messagebox.showerror("Error", "You must select a valid stock.")
                return

            cursor = db.cursor()
            try:
                #update the stock amount
                update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock + %s WHERE StockID = %s"
                cursor.execute(update_stock_query, (amount_to_add, selected_stock_id))
                db.commit()
                messagebox.showinfo("Success", f"{amount_to_add} of stock {selected_stock_id} successfully added.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                add_stock_window.destroy()
                stock_options(selected_branch_info)

        add_button = tk.Button(add_stock_window, text="Add Stock", command=add_stock, **buttonStyle)
        add_button.pack()

        #back button to go back to the previous window
        back_button = tk.Button(add_stock_window, text="Back", command=add_stock_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

    def remove_stock(selected_branch_info):
        # Close the previous window (stock options window)
        previous_window.destroy()

        remove_stock_window = tk.Toplevel(window)
        remove_stock_window.title("Remove Stock")
        remove_stock_window.state('zoomed')
        # remove_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
        top_border = tk.Canvas(remove_stock_window, height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(remove_stock_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(remove_stock_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        # Extract city and postcode from the selected_branch_info
        city, postcode = selected_branch_info.split(", ")

        #get the branch id
        cursor = db.cursor()
        cursor.execute("SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s", (city, postcode))
        branch_id = cursor.fetchone()[0]

        # Fetch stock details from the database
        stock_query = """
            SELECT StockID, StockType
            FROM Stock
            WHERE BranchID = (
                SELECT BranchID
                FROM Branch
                WHERE City = %s AND PostCode = %s
            )
        """
        cursor = db.cursor()
        cursor.execute(stock_query, (city, postcode))
        stock_results = cursor.fetchall()

        # Create a list of stock for the dropdown
        stock_list = [f"{row[0]}: {row[1]}" for row in stock_results] if stock_results else []

        if stock_list:
            stock_var = tk.StringVar(remove_stock_window)
            stock_var.set(stock_list[0])
            stock_dropdown = tk.OptionMenu(remove_stock_window, stock_var, *stock_list)
            stock_dropdown.pack()
    
            def remove_selected_stock():
                selected = stock_var.get().split(":")[0]
                delete_query = "DELETE FROM Stock WHERE StockID = %s"
                try:
                    cursor.execute(delete_query, (selected,))
                    db.commit()
                    messagebox.showinfo("Success", f"Stock {selected} has been removed.")
                    remove_stock_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
            
            remove_button = tk.Button(remove_stock_window, text="Remove Stock", command=remove_selected_stock, **buttonStyle)
            remove_button.pack()
            back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

            #separator
            ttk.Separator(remove_stock_window, orient='horizontal').pack(fill='x', pady=10)

            #dropdown list of all available stock
            def get_available_stock(branch_id):
                cursor = db.cursor()
                cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s", (branch_id,))
                return cursor.fetchall()
            
            available_stock = get_available_stock(branch_id)

            stock_var = tk.StringVar(remove_stock_window)
            stock_var.set("Select stock")
            stock_dropdown_label = tk.Label(remove_stock_window, text="Select Stock:", font=fontStyle)
            stock_dropdown_label.pack()
            stock_dropdown = tk.OptionMenu(remove_stock_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
            stock_dropdown.pack()

            # add ammoount to stock text box
            amount_to_remove_label = tk.Label(remove_stock_window, text="Amount to Remove:", font=fontStyle)
            amount_to_remove_label.pack()
            amount_to_remove_entry = tk.Entry(remove_stock_window, font=fontStyle)
            amount_to_remove_entry.pack()

            #function to add stock
            def remove_stock():
                selected_stock_id = stock_var.get().split(" - ")[0]
                amount_to_remove = amount_to_remove_entry.get()

                if selected_stock_id.startswith("Select"):
                    messagebox.showerror("Error", "You must select a valid stock.")
                    return

                cursor = db.cursor()
                try:
                    #update the stock amount
                    update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock - %s WHERE StockID = %s"
                    cursor.execute(update_stock_query, (amount_to_remove, selected_stock_id))
                    db.commit()
                    messagebox.showinfo("Success", f"{amount_to_remove} of stock {selected_stock_id} successfully removed.")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    remove_stock_window.destroy()
                    stock_options(selected_branch_info)

            remove_button = tk.Button(remove_stock_window, text="Remove Stock", command=remove_stock, **buttonStyle)
            remove_button.pack()

            #back button to go back to the previous window
            back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
            back_button.pack(pady=10)
        else:
            tk.Label(remove_stock_window, text="No stock found to remove.", font=fontStyle).pack()
            back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
            back_button.pack(pady=10)
            

    # Center frame for holding the buttons
    center_frame = tk.Frame(manager_options_window)
    center_frame.pack(expand=True)

    # Create buttons with the same style as in open_staff_roles_window
    
    stock_options_button = tk.Button(center_frame, text="Stock", command=stock_options, font=('Helvetica', 12, 'bold'), height=2, width=15)
    show_reports_button = tk.Button(center_frame, text="Show reports", command=show_reports, font=('Helvetica', 12, 'bold'), height=2, width=15)

    # Pack buttons in the center frame

    stock_options_button.grid(row=0, column=3, padx=10, pady=10)
    show_reports_button.grid(row=0, column=4, padx=10, pady=10)

    calculate_cost_button = tk.Button(manager_options_window, text="Calculate Branch Cost", command=lambda:calculate_branch_cost(), **buttonStyle)
    calculate_cost_button.pack(pady=10)
    back_button = tk.Button(manager_options_window, text="Back", command=lambda: [manager_options_window.destroy(), open_staff_roles_window(selected_branch_info)], **buttonStyle)
    back_button.pack(side=tk.BOTTOM, pady=10)

def waiting_staff_options(selected_branch_info, previous_window):
    # Close the previous window
    previous_window.destroy()

    waiting_staff_window = tk.Toplevel(window)
    waiting_staff_window.title(f"Waiting Staff Options - {selected_branch_info}")
    waiting_staff_window.state('zoomed')
    
    # hr_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
    top_border = tk.Canvas(waiting_staff_window, height=50, bg='black')
    top_border.pack(side='top', fill='x')    
    main_frame = tk.Frame(waiting_staff_window)
    main_frame.pack(padx=20, pady=20)
    title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
    title_label.pack(pady=(0, 10))
    center_frame = tk.Frame(waiting_staff_window)
    center_frame.pack(expand=True)
    center_frame.grid_columnconfigure(0, weight=1)
    logo_image = Image.open("restt.png")  # Replace with your logo path
    logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
    logo_label.image = logo_photo  # Keep a reference
    logo_label.pack(side='left', padx=10, pady=5)
    # waiting_staff_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

    # Center frame for holding the buttons
    center_frame = tk.Frame(waiting_staff_window)
    center_frame.pack(expand=True)

    # Define functionalities for each button (placeholder functions)
    def order():
        order_window = tk.Toplevel(window)
        order_window.title("Order")
        order_window.state('zoomed')
        # take_order_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
        top_border = tk.Canvas(order_window, height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(order_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(order_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        def take_order(selected_branch_info):
            # Create a new window for taking an order
            take_order_window = tk.Toplevel(window)
            take_order_window.title("Take Order")
            take_order_window.state('zoomed')
            # take_order_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
            top_border = tk.Canvas(take_order_window, height=50, bg='black')
            top_border.pack(side='top', fill='x')    
            main_frame = tk.Frame(take_order_window)
            main_frame.pack(padx=20, pady=20)
            title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
            title_label.pack(pady=(0, 10))
            center_frame = tk.Frame(take_order_window)
            center_frame.pack(expand=True)
            center_frame.grid_columnconfigure(0, weight=1)
            logo_image = Image.open("restt.png")  # Replace with your logo path
            logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack(side='left', padx=10, pady=5)
            # Extract the BranchID from the selected branch info
            city, postcode = selected_branch_info.split(", ")
            cursor = db.cursor()
            cursor.execute("SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s", (city, postcode))
            branch_id = cursor.fetchone()[0]

            # Function to fetch available stock
            def get_available_stock(branch_id):
                cursor = db.cursor()
                cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s AND AmountInStock > 0", (branch_id,))
                available_stock = cursor.fetchall()
                cursor.close()
                return available_stock

            # Function to fetch available tables
            def get_available_tables(branch_id):
                cursor = db.cursor()
                cursor.execute("SELECT TableID FROM Tables WHERE BranchID = %s", (branch_id,))
                available_tables = cursor.fetchall()
                cursor.close()
                return available_tables

            # Fetch available stock and tables for the branch
            available_stock = get_available_stock(branch_id)
            available_tables = get_available_tables(branch_id)


            # Dropdown for selecting stock
            stock_var = tk.StringVar(take_order_window)
            stock_var.set("Select stock")
            stock_dropdown_label = tk.Label(take_order_window, text="Select Stock:", font=fontStyle)
            stock_dropdown_label.pack()
            stock_dropdown = tk.OptionMenu(take_order_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
            stock_dropdown.pack()

            # Dropdown for selecting a table
            table_var = tk.StringVar(take_order_window)
            table_var.set("Select table")
            table_dropdown_label = tk.Label(take_order_window, text="Select Table:", font=fontStyle)
            table_dropdown_label.pack()
            table_dropdown = tk.OptionMenu(take_order_window, table_var, *[table[0] for table in available_tables])
            table_dropdown.pack()

            # Function to create a new order entry
            def submit_order_details():
                selected_stock_id = stock_var.get().split(" - ")[0]
                selected_table_id = table_var.get()

                if selected_stock_id.startswith("Select") or selected_table_id.startswith("Select"):
                    messagebox.showerror("Error", "You must select a valid stock and table.")
                    return

                cursor = db.cursor()
                try:
                    # Generate a new unique TrackID
                    cursor.execute("SELECT TrackID FROM orderr ORDER BY CAST(SUBSTRING(TrackID, 2) AS UNSIGNED) DESC LIMIT 1;")
                    last_track_id = cursor.fetchone()[0]
                    last_track_id_number = int(last_track_id[1:]) if last_track_id else 0
                    new_track_id = f"T{last_track_id_number + 1}"

                    # Insert the new order
                    insert_query = "INSERT INTO Orderr (TrackID, StockID, TableID) VALUES (%s, %s, %s)"
                    cursor.execute(insert_query, (new_track_id, selected_stock_id, selected_table_id))

                    # Update stock amount
                    update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock - 1 WHERE StockID = %s"
                    cursor.execute(update_stock_query, (selected_stock_id,))

                    # Set the table as unavailable
                    update_table_query = "UPDATE Tables SET Availability = 0 WHERE TableID = %s"
                    cursor.execute(update_table_query, (selected_table_id,))

                    # Commit the transaction
                    db.commit()
                    messagebox.showinfo("Success", f"Order with tracking ID {new_track_id} successfully taken for table {selected_table_id}.")
                    
                except Exception as e:
                    db.rollback()
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    cursor.close()
                    
            def remove_order(branch_id):
                remove_order_window = tk.Toplevel(window)
                remove_order_window.title("Remove Order")
                remove_order_window.state('zoomed')
                # remove_order_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
                top_border = tk.Canvas(remove_order_window, height=50, bg='black')
                top_border.pack(side='top', fill='x')    
                main_frame = tk.Frame(remove_order_window)
                main_frame.pack(padx=20, pady=20)
                title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
                title_label.pack(pady=(0, 10))
                center_frame = tk.Frame(remove_order_window)
                center_frame.pack(expand=True)
                center_frame.grid_columnconfigure(0, weight=1)
                logo_image = Image.open("restt.png")  # Replace with your logo path
                logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
                logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
                logo_label.image = logo_photo  # Keep a reference
                logo_label.pack(side='left', padx=10, pady=5)
                # Fetch all orders with their corresponding StockType for the branch
                cursor = db.cursor()
                cursor.execute("""
                    SELECT o.TrackID, s.StockType, o.TableID 
                    FROM Orderr o 
                    INNER JOIN Stock s ON o.StockID = s.StockID 
                    WHERE o.TableID IN (
                        SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 0
                    )
                """, (branch_id,))
                order_results = cursor.fetchall()
                cursor.close()

                # Create a list of orders for the dropdown, showing StockType instead of StockID
                order_list = [f"{row[0]}: {row[1]} - Table ID: {row[2]}"
                            for row in order_results] if order_results else []

                if order_list:
                    order_var = tk.StringVar(remove_order_window)
                    order_var.set(order_list[0])  # Set default value
                    order_dropdown = tk.OptionMenu(remove_order_window, order_var, *order_list)
                    order_dropdown.pack()
                    
                    def remove_selected_order():
                        selected_track_id = order_var.get().split(":")[0]
                        cursor = db.cursor()
                        try:
                            # Start transaction
                            cursor.execute("START TRANSACTION")
                            
                            # Delete the order
                            delete_query = "DELETE FROM Orderr WHERE TrackID = %s"
                            cursor.execute(delete_query, (selected_track_id,))

                            # Update the availability of the table
                            # Ensure to retrieve and update the correct TableID from the Order
                            update_table_query = """
                            UPDATE Tables SET Availability = 1 
                            WHERE TableID = (
                                SELECT TableID FROM Orderr WHERE TrackID = %s
                            )
                            """
                            cursor.execute(update_table_query, (selected_track_id,))

                            # Commit the changes
                            db.commit()
                            messagebox.showinfo("Success", f"Order {selected_track_id} has been cancelled")
                            
                            remove_order_window.destroy()
                        except Exception as e:
                            db.rollback()
                            messagebox.showerror("Error", f"An error occurred: {e}")
                        finally:
                            cursor.close()

                    remove_button = tk.Button(remove_order_window, text="Remove Order", command=remove_selected_order, **buttonStyle)
                    remove_button.pack()
                    back_button = tk.Button(remove_order_window, text="Back", command=remove_order_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)
                else:
                    tk.Label(remove_order_window, text="No orders found for this branch.", font=fontStyle).pack()
                    back_button = tk.Button(remove_order_window, text="Back", command=remove_order_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

            # Button to submit the order details
            submit_button = tk.Button(take_order_window, text="Submit Order", command=submit_order_details, **buttonStyle)
            submit_button.pack()

            # Button to go back to the previous window
            back_button = tk.Button(take_order_window, text="Back", command=take_order_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

            # Add a button for removing an order in the take_order_window
            remove_order_button = tk.Button(take_order_window, text="Remove Order", command=lambda: remove_order(branch_id), **buttonStyle)
            remove_order_button.pack()

        def view_orders(selected_branch_info):
            view_orders_window = tk.Toplevel(window)
            view_orders_window.title("View Orders")
            view_orders_window.state('zoomed')
            # view_orders_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
            top_border = tk.Canvas(view_orders_window, height=50, bg='black')
            top_border.pack(side='top', fill='x')    
            main_frame = tk.Frame(view_orders_window)
            main_frame.pack(padx=20, pady=20)
            title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
            title_label.pack(pady=(0, 10))
            center_frame = tk.Frame(view_orders_window)
            center_frame.pack(expand=True)
            center_frame.grid_columnconfigure(0, weight=1)
            logo_image = Image.open("restt.png")  # Replace with your logo path
            logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack(side='left', padx=10, pady=5)

            # Extract the BranchID from the selected branch info
            city, postcode = selected_branch_info.split(", ")
            cursor = db.cursor()
            cursor.execute("SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s", (city, postcode))
            branch_id = cursor.fetchone()[0]
            cursor.close()

            # Fetch all orders with their corresponding StockType for the branch
            cursor = db.cursor()
            cursor.execute("""SELECT o.TrackID, s.StockType, o.TableID
                                FROM Orderr o
                                INNER JOIN Stock s ON o.StockID = s.StockID
                                WHERE o.TableID IN (
                                    SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 0
                                )""", (branch_id,))
            
            order_results = cursor.fetchall()
            cursor.close()

            # print all the orders in the window

            if order_results:
                for track_id, stock_type, table_id in order_results:
                    order_info = f"{track_id}: {stock_type} - Table ID: {table_id}"
                    tk.Label(view_orders_window, text=order_info, font=fontStyle).pack()
            else:
                tk.Label(view_orders_window, text="No orders found for this branch.", font=fontStyle).pack()

            back_button = tk.Button(view_orders_window, text="Back", command=view_orders_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

        def print_receipt(selected_branch_info):
            print_receipt_window = tk.Toplevel(window)
            print_receipt_window.title("Print Receipt")
            print_receipt_window.state('zoomed')
            # print_receipt_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
            top_border = tk.Canvas(print_receipt_window, height=50, bg='black')
            top_border.pack(side='top', fill='x')    
            main_frame = tk.Frame(print_receipt_window)
            main_frame.pack(padx=20, pady=20)
            title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
            title_label.pack(pady=(0, 10))
            center_frame = tk.Frame(print_receipt_window)
            center_frame.pack(expand=True)
            center_frame.grid_columnconfigure(0, weight=1)
            logo_image = Image.open("restt.png")  # Replace with your logo path
            logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack(side='left', padx=10, pady=5)
            # Extract the BranchID from the selected branch info
            city, postcode = selected_branch_info.split(", ")
            cursor = db.cursor()
            cursor.execute("SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s", (city, postcode))
            branch_id = cursor.fetchone()[0]
            cursor.close()

            #dropdown for selecting the table
            def get_available_tables(branch_id):
                cursor = db.cursor()
                cursor.execute("SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 0", (branch_id,))
                return cursor.fetchall()
            
            available_tables = get_available_tables(branch_id)

            #if there are no available tables, then the dropdown will show "No tables available"
            if not available_tables:
                available_tables = ["No tables available"]
                table_var = tk.StringVar(print_receipt_window)
                table_var.set(available_tables[0])
                table_dropdown_label = tk.Label(print_receipt_window, text="Select Table:", font=fontStyle)
                table_dropdown_label.pack()
                table_dropdown = tk.OptionMenu(print_receipt_window, table_var, *[table for table in available_tables])
                table_dropdown.pack()
            else:
                table_var = tk.StringVar(print_receipt_window)
                table_var.set(available_tables[0][0] if available_tables else "No tables available")
                table_dropdown_label = tk.Label(print_receipt_window, text="Select Table:", font=fontStyle)
                table_dropdown_label.pack()
                table_dropdown = tk.OptionMenu(print_receipt_window, table_var, *[table[0] for table in available_tables])
                table_dropdown.pack()


            #generate receipt
            def generate_receipt():
                selected_table = table_var.get()
                if selected_table == "No tables available":
                    messagebox.showerror("Error", "No available tables to print receipt for.")
                    return

                #fetch all the orders for the selected table
                cursor = db.cursor()
                cursor.execute("""
                    SELECT o.TrackID, s.StockType, o.TableID, s.Price
                    FROM Orderr o
                    INNER JOIN Stock s ON o.StockID = s.StockID
                    WHERE o.TableID = %s
                """, (selected_table,))
                order_results = cursor.fetchall()
                cursor.close()

                if order_results:
                    #calculate total price
                    total_price = sum([order[3] for order in order_results])
                    receipt = f"Table ID: {selected_table}\n"
                    receipt += f"{'-' * 20}\n"
                    for track_id, stock_type, table_id, price in order_results:
                        receipt += f"{track_id}: {stock_type} - £{price}\n"
                    receipt += f"{'-' * 20}\n"
                    receipt += f"Total: £{total_price}"
                    tk.Label(print_receipt_window, text=receipt, font=fontStyle).pack()

                    #update the table availability
                    cursor = db.cursor()
                    cursor.execute("UPDATE Tables SET Availability = 1 WHERE TableID = %s", (selected_table,))
                    cursor.close()

                    #delete the orders
                    cursor = db.cursor()
                    cursor.execute("DELETE FROM Orderr WHERE TableID = %s", (selected_table,))
                    cursor.close()

                    #update the receipt table
                    cursor = db.cursor()
                    cursor.execute("SELECT ReceiptID FROM receipt ORDER BY CAST(SUBSTRING(ReceiptID, 2) AS UNSIGNED) DESC Limit 1;")
                    last_receipt_id = cursor.fetchone()[0]
                    last_receipt_id_number = int(last_receipt_id[1:]) if last_receipt_id else 0
                    new_receipt_id = f"R{last_receipt_id_number + 1}"
                    cursor.execute("INSERT INTO Receipt (ReceiptID, TableID, Price, BranchID) VALUES (%s, %s, %s, %s)", (new_receipt_id, selected_table, total_price, branch_id))
                    cursor.close()

                    #commit the changes
                    db.commit()

                    #back button to go back to the previous window
                    back_button = tk.Button(print_receipt_window, text="Back", command=print_receipt_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

                else:
                    tk.Label(print_receipt_window, text="No orders found for this table.", font=fontStyle).pack()

            #button to generate receipt
            generate_receipt_button = tk.Button(print_receipt_window, text="Generate Receipt", command=generate_receipt, **buttonStyle)
            generate_receipt_button.pack()

            #back button to go back to the previous window
            back_button = tk.Button(print_receipt_window, text="Back", command=print_receipt_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

        # 3 buttons for taking order, viewing orders, and print recipt
        take_order_button = tk.Button(order_window, text="Take Order", command=lambda: [order_window.destroy(), take_order(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)
        view_orders_button = tk.Button(order_window, text="View Orders", command=lambda: [order_window.destroy(), view_orders(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)
        print_receipt_button = tk.Button(order_window, text="Print Receipt", command=lambda: [order_window.destroy(), print_receipt(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)

        # Pack buttons in the center frame
        take_order_button.pack(pady=10)
        view_orders_button.pack(pady=10)
        print_receipt_button.pack(pady=10)

        #back button to go back to the previous window
        back_button = tk.Button(order_window, text="Back", command=lambda: [order_window.destroy(), waiting_staff_options(selected_branch_info, waiting_staff_window)], **buttonStyle)
        back_button.pack(pady=10)

    def reservation():
        reservation_window = tk.Toplevel(window)
        reservation_window.title("Reservation")
        reservation_window.state('zoomed')
        # reservation_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
        top_border = tk.Canvas(reservation_window, height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(reservation_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(reservation_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        def take_reservation(selected_branch_info):
            # Create a new window for taking reservation
            take_reservation_window = tk.Toplevel(window)
            take_reservation_window.title("Take Reservation")
            take_reservation_window.state('zoomed')
            # take_reservation_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
            top_border = tk.Canvas(take_reservation_window, height=50, bg='black')
            top_border.pack(side='top', fill='x')    
            main_frame = tk.Frame(take_reservation_window)
            main_frame.pack(padx=20, pady=20)
            title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
            title_label.pack(pady=(0, 10))
            center_frame = tk.Frame(take_reservation_window)
            center_frame.pack(expand=True)
            center_frame.grid_columnconfigure(0, weight=1)
            logo_image = Image.open("restt.png")  # Replace with your logo path
            logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack(side='left', padx=10, pady=5)
            # Entry fields for reservation details
            customer_name_label = tk.Label(take_reservation_window, text="Customer Name:", font=fontStyle)
            customer_name_label.pack()
            customer_name_entry = tk.Entry(take_reservation_window, font=fontStyle)
            customer_name_entry.pack()

            #customer phone number entry
            customer_phone_label = tk.Label(take_reservation_window, text="Customer Phone Number:", font=fontStyle)
            customer_phone_label.pack()
            customer_phone_entry = tk.Entry(take_reservation_window, font=fontStyle)
            customer_phone_entry.pack()

            #date entry
            date_label = tk.Label(take_reservation_window, text="Date (YYYY-MM-DD):", font=fontStyle)
            date_label.pack()
            date_entry = tk.Entry(take_reservation_window, font=fontStyle)
            date_entry.pack()

            #time entry
            time_label = tk.Label(take_reservation_window, text="Time (HH:MM):", font=fontStyle)
            time_label.pack()
            time_entry = tk.Entry(take_reservation_window, font=fontStyle)
            time_entry.pack()

            # Function to fetch available tables
            def get_available_tables(branch_id):
                cursor = db.cursor()
                cursor.execute("SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 1", (branch_id,))
                return cursor.fetchall()

            # Function to update table availability
            def update_table_availability(table_id, availability):
                cursor = db.cursor()
                cursor.execute("UPDATE Tables SET Availability = %s WHERE TableID = %s", (availability, table_id))
                cursor.close()

            # Retrieve the BranchID from the selected branch info
            city, postcode = selected_branch_info.split(", ")
            cursor = db.cursor()
            cursor.execute("SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s", (city, postcode))
            branch_id = cursor.fetchone()[0]
            cursor.close()

            # Dropdown for selecting a table
            available_tables = get_available_tables(branch_id)
            table_var = tk.StringVar(take_reservation_window)
            table_var.set(available_tables[0][0] if available_tables else "No tables available")
            table_dropdown_label = tk.Label(take_reservation_window, text="Available Tables:", font=fontStyle)
            table_dropdown_label.pack()
            table_dropdown = tk.OptionMenu(take_reservation_window, table_var, *[table[0] for table in available_tables])
            table_dropdown.pack()

            # Function to create a new reservation
            def submit_reservation_details():
                customer_name = customer_name_entry.get()
                customer_phone = customer_phone_entry.get()
                date = date_entry.get()
                time = time_entry.get()
                selected_table = table_var.get()

                if selected_table == "No tables available":
                    messagebox.showerror("Error", "No available tables to reserve.")
                    return

                # Start transaction
                cursor = db.cursor()
                cursor.execute("START TRANSACTION")
                try:
                    # Create a new reservation ID
                    cursor.execute("SELECT MAX(ReservationID) FROM Reservation")
                    last_id = cursor.fetchone()[0]
                    last_id_number = int(last_id[1:]) if last_id else 0
                    new_reservation_id = f"R{last_id_number + 1}"

                    # Insert the new reservation
                    insert_query = """
                        INSERT INTO Reservation (ReservationID, CustomerName, CustomerPhoneNO, Date, Time, BranchID, TableID)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (new_reservation_id, customer_name, customer_phone, date, time, branch_id, selected_table))

                    # Update table availability
                    update_table_availability(selected_table, 0)

                    # Commit the transaction
                    db.commit()
                    messagebox.showinfo("Success", f"Reservation {new_reservation_id} successfully added and table {selected_table} is now reserved.")
                    take_reservation_window.destroy()
                except Exception as e:
                    db.rollback()
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    cursor.close()

            # Button to submit the reservation details
            submit_button = tk.Button(take_reservation_window, text="Submit Reservation", command=submit_reservation_details, **buttonStyle)
            submit_button.pack()

            # Button to go back to the previous window
            back_button = tk.Button(take_reservation_window, text="Back", command=take_reservation_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

        def view_reservations():
            # Create a new window for viewing reservation
            view_reservation_window = tk.Toplevel(window)
            view_reservation_window.title("View Reservation")
            view_reservation_window.state('zoomed')
            # view_reservation_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
            top_border = tk.Canvas(view_reservation_window , height=50, bg='black')
            top_border.pack(side='top', fill='x')    
            main_frame = tk.Frame(view_reservation_window )
            main_frame.pack(padx=20, pady=20)
            title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
            title_label.pack(pady=(0, 10))
            center_frame = tk.Frame(view_reservation_window )
            center_frame.pack(expand=True)
            center_frame.grid_columnconfigure(0, weight=1)
            logo_image = Image.open("restt.png")  # Replace with your logo path
            logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack(side='left', padx=10, pady=5)
            #get branch id from selected branch info
            city, postcode = selected_branch_info.split(", ")
            cursor = db.cursor(buffered=True)
            branch_query = "SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s"
            cursor.execute(branch_query, (city, postcode))
            branch_result = cursor.fetchone()
            branch_id = branch_result[0]

            #fetch reservation details from the database
            reservation_query = """
                SELECT ReservationID, CustomerName, CustomerPhoneNO, Date, Time, TableID
                FROM Reservation
                WHERE BranchID = %s
            """
            cursor = db.cursor()
            cursor.execute(reservation_query, (branch_id,))
            reservation_results = cursor.fetchall()

            # show all the reservations in the window
            if reservation_results:
                for reservation_id, customer_name, customer_phone, date, time, table_id in reservation_results:
                    reservation_info = f"{reservation_id}: {customer_name} - {customer_phone} - {date} - {time} - ({table_id})"
                    tk.Label(view_reservation_window, text=reservation_info, font=fontStyle).pack()
            else:
                tk.Label(view_reservation_window, text="No reservation found for this branch.", font=fontStyle).pack()

            back_button = tk.Button(view_reservation_window, text="Back", command=view_reservation_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

        def cancel_reservation(selected_branch_info):
            # Create a new window for canceling reservation
            cancel_reservation_window = tk.Toplevel(window)
            cancel_reservation_window.title("Cancel Reservation")
            cancel_reservation_window.state('zoomed')
            top_border = tk.Canvas(cancel_reservation_window , height=50, bg='black')
            top_border.pack(side='top', fill='x')    
            main_frame = tk.Frame(cancel_reservation_window)
            main_frame.pack(padx=20, pady=20)
            title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
            title_label.pack(pady=(0, 10))
            center_frame = tk.Frame(cancel_reservation_window)
            center_frame.pack(expand=True)
            center_frame.grid_columnconfigure(0, weight=1)
            logo_image = Image.open("restt.png")  # Replace with your logo path
            logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack(side='left', padx=10, pady=5)
            # Retrieve the BranchID from the selected branch info
            city, postcode = selected_branch_info.split(", ")
            cursor = db.cursor()
            cursor.execute("SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s", (city, postcode))
            branch_id = cursor.fetchone()[0]
            cursor.close()

            # Fetch reservation details from the database for the branch
            cursor = db.cursor()
            reservation_query = """
                SELECT ReservationID, CustomerName, CustomerPhoneNO, Date, Time, TableID
                FROM Reservation
                WHERE BranchID = %s
            """
            cursor.execute(reservation_query, (branch_id,))
            reservation_results = cursor.fetchall()
            cursor.close()

            # Create a list of reservations for the dropdown
            reservation_list = [
                f"{row[0]}: {row[1]} - {row[2]} - {row[3]} - {row[4]}"
                for row in reservation_results
            ] if reservation_results else []

            reservation_var = tk.StringVar(cancel_reservation_window)
            reservation_var.set(reservation_list[0] if reservation_list else "No reservations available")
            reservation_dropdown = tk.OptionMenu(cancel_reservation_window, reservation_var, *reservation_list)
            reservation_dropdown.pack()

            def cancel_selected_reservation():
                selected_reservation_id = reservation_var.get().split(":")[0]
                cursor = db.cursor()
                try:
                    # Start transaction
                    cursor.execute("START TRANSACTION")
                    
                    # Get the TableID of the reservation to be canceled
                    get_table_query = "SELECT TableID FROM Reservation WHERE ReservationID = %s"
                    cursor.execute(get_table_query, (selected_reservation_id,))
                    table_id = cursor.fetchone()
                    
                    if table_id:
                        table_id = table_id[0]  # Extract the TableID
                        
                        # Delete the reservation
                        delete_query = "DELETE FROM Reservation WHERE ReservationID = %s"
                        cursor.execute(delete_query, (selected_reservation_id,))
                        
                        # Update the availability of the table
                        update_table_query = "UPDATE Tables SET Availability = 1 WHERE TableID = %s"
                        cursor.execute(update_table_query, (table_id,))
                        
                        # Commit the changes
                        db.commit()
                        messagebox.showinfo("Success", f"Reservation {selected_reservation_id} has been canceled and table {table_id} is now available.")
                    else:
                        db.rollback()  # Rollback if no TableID is found for the reservation
                        messagebox.showinfo("Notice", f"Reservation {selected_reservation_id} was not found or has no associated table.")
                    
                    cancel_reservation_window.destroy()
                except Exception as e:
                    db.rollback()
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    cursor.close()

            cancel_button = tk.Button(cancel_reservation_window, text="Cancel Reservation", command=cancel_selected_reservation, **buttonStyle)
            cancel_button.pack()

            back_button = tk.Button(cancel_reservation_window, text="Back", command=cancel_reservation_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

        # 3 buttons for taking reservation, viewing reservations, and cancel reservation
        take_reservation_button = tk.Button(reservation_window, text="Take Reservation", command=lambda: [reservation_window.destroy(), take_reservation(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)
        view_reservations_button = tk.Button(reservation_window, text="View Reservations", command=lambda: [reservation_window.destroy(), view_reservations()], font=('Helvetica', 12, 'bold'), height=2, width=15)
        cancel_reservation_button = tk.Button(reservation_window, text="Cancel Reservation", command=lambda: [reservation_window.destroy(), cancel_reservation(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)

        # Pack buttons in the center frame
        take_reservation_button.pack(pady=10)
        view_reservations_button.pack(pady=10)
        cancel_reservation_button.pack(pady=10)

        #back button to go back to the previous window
        back_button = tk.Button(reservation_window, text="Back", command=lambda: [reservation_window.destroy(), waiting_staff_options(selected_branch_info, waiting_staff_window)], **buttonStyle)
        back_button.pack(pady=10)
        


    # Create buttons
    take_order_button = tk.Button(center_frame, text="Orders", command=order, font=('Helvetica', 12, 'bold'), height=2, width=15)
    book_reservation_button = tk.Button(center_frame, text="Reservations", command=reservation, font=('Helvetica', 12, 'bold'), height=2, width=15)

    # Pack buttons in the center frame
    take_order_button.grid(row=0, column=0, padx=10, pady=10)
    book_reservation_button.grid(row=0, column=1, padx=10, pady=10)

    back_button = tk.Button(center_frame, text="Back", command=lambda: [waiting_staff_window.destroy(), open_staff_roles_window(selected_branch_info)], **buttonStyle)
    back_button.grid(row=1, column=0, columnspan=2, pady=10)

def kitchen_staff_options(selected_branch_info, previous_window):
    # Close the previous window
    previous_window.destroy()

    kitchen_staff_window = tk.Toplevel(window)
    kitchen_staff_window.title(f"Kitchen Staff Options - {selected_branch_info}")
    kitchen_staff_window.state('zoomed')
    # kitchen_staff_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
    # hr_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
    top_border = tk.Canvas( kitchen_staff_window, height=50, bg='black')
    top_border.pack(side='top', fill='x')    
    main_frame = tk.Frame( kitchen_staff_window)
    main_frame.pack(padx=20, pady=20)
    title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
    title_label.pack(pady=(0, 10))
    center_frame = tk.Frame( kitchen_staff_window)
    center_frame.pack(expand=True)
    center_frame.grid_columnconfigure(0, weight=1)
    logo_image = Image.open("restt.png")  # Replace with your logo path
    logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
    logo_label.image = logo_photo  # Keep a reference
    logo_label.pack(side='left', padx=10, pady=5)
    # Center frame for holding the buttons
    center_frame = tk.Frame(kitchen_staff_window)
    center_frame.pack(expand=True)

    # Define functionalities for each button (placeholder functions)

    def view_orders():
        view_orders_window = tk.Toplevel(window)
        view_orders_window.title("View Orders")
        view_orders_window.state('zoomed')
        # view_orders_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
        top_border = tk.Canvas(view_orders_window , height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(view_orders_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(view_orders_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        # Listbox to display orders
        orders_listbox = tk.Listbox(view_orders_window, width=50, height=20)
        orders_listbox.pack(pady=20)

        # Extract the BranchID from the selected branch info
        city, postcode = selected_branch_info.split(", ")
        cursor = db.cursor()
        cursor.execute("SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s", (city, postcode))
        branch_id = cursor.fetchone()[0]
        cursor.close()

        # Fetch all orders with their corresponding StockType for the branch
        cursor = db.cursor()
        cursor.execute("""SELECT o.TrackID, s.StockType, o.TableID
                            FROM Orderr o
                            INNER JOIN Stock s ON o.StockID = s.StockID
                            WHERE o.TableID IN (
                                SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 0
                            )""", (branch_id,))
        
        order_results = cursor.fetchall()
        cursor.close()

        # Populate the listbox with orders
        for order in order_results:
            orders_listbox.insert(tk.END, f"{order[0]}: {order[1]} - Table ID: {order[2]}")

        def complete_order():
            # Check if an order is selected
            if orders_listbox.curselection():
                index = orders_listbox.curselection()[0]
                selected_order = orders_listbox.get(index)
                track_id = selected_order.split(":")[0]

                # Process to remove the order from the system and add points to the account
                cursor = db.cursor()
                try:
                    # Remove the order from the ListBox
                    orders_listbox.delete(index)
                    messagebox.showinfo("Success", "Order completed.")

                except Exception as e:
                    db.rollback()
                    messagebox.showerror("Error", str(e))
                finally:
                    cursor.close()

        # Button to mark an order as completed
        complete_order_button = tk.Button(view_orders_window, text="Complete Order", command=complete_order, **buttonStyle)
        complete_order_button.pack(pady=10)

        back_button = tk.Button(view_orders_window, text="Back", command=view_orders_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

    def update_stock():
        # Close the previous window (manager options window)
        previous_window.destroy()
        
        stock_options_window = tk.Toplevel(window)
        stock_options_window.title(f"Stock Options - {selected_branch_info}")
        stock_options_window.state('zoomed')
        top_border = tk.Canvas(stock_options_window , height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(stock_options_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Framestock_options_window
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        stock_center_frame = tk.Frame(stock_options_window)
        stock_center_frame.pack(expand=True)
        # stock_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

        # Define functionalities for each button 
        view_stock_button = tk.Button(stock_center_frame, text="View Stock", command=lambda: view_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
        add_stock_button = tk.Button(stock_center_frame, text="Add Stock", command=lambda: add_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
        remove_stock_button = tk.Button(stock_center_frame, text="Remove Stock", command=lambda: remove_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
        
        # Pack buttons in the center frame
        view_stock_button.grid(row=0, column=0, padx=10, pady=10)
        add_stock_button.grid(row=0, column=1, padx=10, pady=10)
        remove_stock_button.grid(row=0, column=2, padx=10, pady=10)

        # Back button to go back to the previous window
        back_button = tk.Button(stock_options_window, text="Back", command=stock_options_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

    def view_stock(selected_branch_info):
        view_stock_window = tk.Toplevel(window)
        view_stock_window.title("View Stock")
        view_stock_window.state('zoomed')
        top_border = tk.Canvas(view_stock_window , height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(view_stock_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Framestock_options_window
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        # Extract city and postcode from the selected_branch_info
        city, postcode = selected_branch_info.split(", ")

        stock_query = """
            SELECT StockID, StockType, AmountInStock, Price
            FROM Stock
            WHERE BranchID = (
                SELECT BranchID
                FROM Branch
                WHERE City = %s AND PostCode = %s
            )
        """
        cursor = db.cursor()
        cursor.execute(stock_query, (city, postcode))
        stock_results = cursor.fetchall()

        if stock_results:
            for stock_id, stock_type, amount_in_stock, price in stock_results:
                stock_info = f"{stock_id}: {stock_type} - {amount_in_stock} in stock - £{price}"
                tk.Label(view_stock_window, text=stock_info, font=fontStyle).pack()
        else:
            tk.Label(view_stock_window, text="No stock found for this branch.", font=fontStyle).pack()

        back_button = tk.Button(view_stock_window, text="Back", command=view_stock_window.destroy, **buttonStyle)
        back_button.pack(pady=10)
    
    def add_stock(selected_branch_info):
        # Close the previous window (stock options window)
        previous_window.destroy()

        add_stock_window = tk.Toplevel(window)
        add_stock_window.title("Add Stock")
        add_stock_window.state('zoomed')
        # add_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
        top_border = tk.Canvas(add_stock_window , height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(add_stock_window )
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Framestock_options_window
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        # Extract city and postcode from the selected_branch_info
        city, postcode = selected_branch_info.split(", ")

        #get the branch id
        cursor = db.cursor()
        cursor.execute("SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s", (city, postcode))
        branch_id = cursor.fetchone()[0]


        # Entry fields for stock details
        stock_type_label = tk.Label(add_stock_window, text="Stock Type:", font=fontStyle)
        stock_type_label.pack()
        stock_type_entry = tk.Entry(add_stock_window, font=fontStyle)
        stock_type_entry.pack()

        amount_in_stock_label = tk.Label(add_stock_window, text="Amount in Stock:", font=fontStyle)
        amount_in_stock_label.pack()
        amount_in_stock_entry = tk.Entry(add_stock_window, font=fontStyle)
        amount_in_stock_entry.pack()

        price_label = tk.Label(add_stock_window, text="Price:", font=fontStyle)
        price_label.pack()
        price_entry = tk.Entry(add_stock_window, font=fontStyle)
        price_entry.pack()

        # Submit function
        def submit_stock_details():
            stock_type = stock_type_entry.get()
            amount_in_stock = amount_in_stock_entry.get()
            price = price_entry.get()

            # Generate Stock ID based on the last StockID
            cursor = db.cursor()
            cursor.execute("SELECT MAX(StockID) FROM Stock")
            last_stock_id_row = cursor.fetchone()
            last_stock_id = last_stock_id_row[0] if last_stock_id_row and last_stock_id_row[0] else "S0"
            new_stock_id_number = int(last_stock_id.lstrip("S")) + 1
            new_stock_id = "S" + str(new_stock_id_number)

            # Insert into database (adjust according to your schema)
            insert_query = """
                INSERT INTO Stock (StockID, StockType, AmountInStock, Price, BranchID)
                SELECT %s, %s, %s, %s, Branch.BranchID
                FROM Branch
                WHERE Branch.City = %s AND Branch.PostCode = %s
            """
            try:
                cursor.execute(insert_query, (new_stock_id, stock_type, amount_in_stock, price, city, postcode))
                db.commit()
                messagebox.showinfo("Success", f"Stock {new_stock_id} successfully added.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                add_stock_window.destroy()
                update_stock(selected_branch_info)

        submit_button = tk.Button(add_stock_window, text="Submit", command=submit_stock_details, **buttonStyle)
        submit_button.pack()
        back_button = tk.Button(add_stock_window, text="Back", command=add_stock_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

        # Separator
        ttk.Separator(add_stock_window, orient='horizontal').pack(fill='x', pady=10)

        #dropdown list of all available stock
        def get_available_stock(branch_id):
            cursor = db.cursor()
            cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s", (branch_id,))
            return cursor.fetchall()
        
        available_stock = get_available_stock(branch_id)

        stock_var = tk.StringVar(add_stock_window)
        stock_var.set("Select stock")
        stock_dropdown_label = tk.Label(add_stock_window, text="Select Stock:", font=fontStyle)
        stock_dropdown_label.pack()
        stock_dropdown = tk.OptionMenu(add_stock_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
        stock_dropdown.pack()

        # add ammoount to stock text box
        amount_to_add_label = tk.Label(add_stock_window, text="Amount to Add:", font=fontStyle)
        amount_to_add_label.pack()
        amount_to_add_entry = tk.Entry(add_stock_window, font=fontStyle)
        amount_to_add_entry.pack()

        #function to add stock
        def add_stock():
            selected_stock_id = stock_var.get().split(" - ")[0]
            amount_to_add = amount_to_add_entry.get()

            if selected_stock_id.startswith("Select"):
                messagebox.showerror("Error", "You must select a valid stock.")
                return

            cursor = db.cursor()
            try:
                #update the stock amount
                update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock + %s WHERE StockID = %s"
                cursor.execute(update_stock_query, (amount_to_add, selected_stock_id))
                db.commit()
                messagebox.showinfo("Success", f"{amount_to_add} of stock {selected_stock_id} successfully added.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                add_stock_window.destroy()
                update_stock(selected_branch_info)

        add_button = tk.Button(add_stock_window, text="Add Stock", command=add_stock, **buttonStyle)
        add_button.pack()

        #back button to go back to the previous window
        back_button = tk.Button(add_stock_window, text="Back", command=add_stock_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

    def remove_stock(selected_branch_info):
        # Close the previous window (stock options window)
        previous_window.destroy()

        remove_stock_window = tk.Toplevel(window)
        remove_stock_window.title("Remove Stock")
        remove_stock_window.state('zoomed')
        # remove_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

        # Extract city and postcode from the selected_branch_info
        city, postcode = selected_branch_info.split(", ")

        #get the branch id
        cursor = db.cursor()
        cursor.execute("SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s", (city, postcode))
        branch_id = cursor.fetchone()[0]

        # Fetch stock details from the database
        stock_query = """
            SELECT StockID, StockType
            FROM Stock
            WHERE BranchID = (
                SELECT BranchID
                FROM Branch
                WHERE City = %s AND PostCode = %s
            )
        """
        cursor = db.cursor()
        cursor.execute(stock_query, (city, postcode))
        stock_results = cursor.fetchall()

        # Create a list of stock for the dropdown
        stock_list = [f"{row[0]}: {row[1]}" for row in stock_results] if stock_results else []

        if stock_list:
            stock_var = tk.StringVar(remove_stock_window)
            stock_var.set(stock_list[0])
            stock_dropdown = tk.OptionMenu(remove_stock_window, stock_var, *stock_list)
            stock_dropdown.pack()
    
            def remove_selected_stock():
                selected = stock_var.get().split(":")[0]
                delete_query = "DELETE FROM Stock WHERE StockID = %s"
                try:
                    cursor.execute(delete_query, (selected,))
                    db.commit()
                    messagebox.showinfo("Success", f"Stock {selected} has been removed.")
                    remove_stock_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
            
            remove_button = tk.Button(remove_stock_window, text="Remove Stock", command=remove_selected_stock, **buttonStyle)
            remove_button.pack()
            back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

            #separator
            ttk.Separator(remove_stock_window, orient='horizontal').pack(fill='x', pady=10)

            #dropdown list of all available stock
            def get_available_stock(branch_id):
                cursor = db.cursor()
                cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s", (branch_id,))
                return cursor.fetchall()
            
            available_stock = get_available_stock(branch_id)

            stock_var = tk.StringVar(remove_stock_window)
            stock_var.set("Select stock")
            stock_dropdown_label = tk.Label(remove_stock_window, text="Select Stock:", font=fontStyle)
            stock_dropdown_label.pack()
            stock_dropdown = tk.OptionMenu(remove_stock_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
            stock_dropdown.pack()

            # add ammoount to stock text box
            amount_to_remove_label = tk.Label(remove_stock_window, text="Amount to Remove:", font=fontStyle)
            amount_to_remove_label.pack()
            amount_to_remove_entry = tk.Entry(remove_stock_window, font=fontStyle)
            amount_to_remove_entry.pack()

            #function to add stock
            def remove_stock():
                selected_stock_id = stock_var.get().split(" - ")[0]
                amount_to_remove = amount_to_remove_entry.get()

                if selected_stock_id.startswith("Select"):
                    messagebox.showerror("Error", "You must select a valid stock.")
                    return

                cursor = db.cursor()
                try:
                    #update the stock amount
                    update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock - %s WHERE StockID = %s"
                    cursor.execute(update_stock_query, (amount_to_remove, selected_stock_id))
                    db.commit()
                    messagebox.showinfo("Success", f"{amount_to_remove} of stock {selected_stock_id} successfully removed.")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    remove_stock_window.destroy()
                    update_stock(selected_branch_info)

            remove_button = tk.Button(remove_stock_window, text="Remove Stock", command=remove_stock, **buttonStyle)
            remove_button.pack()

            #back button to go back to the previous window
            back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
            back_button.pack(pady=10)
        else:
            tk.Label(remove_stock_window, text="No stock found to remove.", font=fontStyle).pack()
            back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
            back_button.pack(pady=10)
    
    # Create buttons
    view_orders_button = tk.Button(center_frame, text="View Orders", command=view_orders, font=('Helvetica', 12, 'bold'), height=2, width=15)
    update_stock_button = tk.Button(center_frame, text="Update Stock", command=update_stock, font=('Helvetica', 12, 'bold'), height=2, width=15)

    # Pack buttons in the center frame
    view_orders_button.grid(row=0, column=0, padx=10, pady=10)
    update_stock_button.grid(row=0, column=1, padx=10, pady=10)

    back_button = tk.Button(center_frame, text="Back", command=lambda: [kitchen_staff_window.destroy(), open_staff_roles_window(selected_branch_info)], **buttonStyle)
    back_button.grid(row=1, column=0, columnspan=2, pady=10)

def open_staff_roles_window(selected_branch_info):
    staff_roles_window = tk.Toplevel(window)
    staff_roles_window.title(f"Staff Roles - {selected_branch_info}")
    staff_roles_window.state('zoomed')
    # staff_roles_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
    
    top_border = tk.Canvas(staff_roles_window, height=50, bg='black')
    top_border.pack(side='top', fill='x') 
    logo_image = Image.open("restt.png")  # Replace with your logo path
    logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
    logo_label.image = logo_photo  # Keep a reference
    logo_label.pack(side='left', padx=10, pady=5)
    heading_roles_frame = tk.Frame(staff_roles_window)
    heading_roles_frame.pack(side=tk.TOP, pady=10)

    heading_roles_label = tk.Label(heading_roles_frame, text="Staff Roles", font=('Helvetica', 16, 'bold'))
    heading_roles_label.pack(side=tk.LEFT, padx=10)

    buttons_frame = tk.Frame(staff_roles_window)
    buttons_frame.pack(side=tk.TOP, pady=10)

    back_button = tk.Button(staff_roles_window, text="Back", command=lambda: [staff_roles_window.destroy(), select_branch()], **buttonStyle)
    back_button.pack(side=tk.BOTTOM, pady=10)

    center_frame = tk.Frame(staff_roles_window)
    center_frame.pack(expand=True)

    def show_all_staff():
        all_staff_window = tk.Toplevel(window)
        all_staff_window.title("All Staff")
        all_staff_window.state('zoomed')
        # all_staff_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
    # hr_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
        top_border = tk.Canvas( all_staff_window , height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame( all_staff_window )
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame( all_staff_window )
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
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
        top_border = tk.Canvas( add_staff_window , height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame( add_staff_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(add_staff_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
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
        top_border = tk.Canvas(remove_staff_window, height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(remove_staff_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(remove_staff_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
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

    def button_click(role):
        if role == "Manager":
            manager_options(selected_branch_info, staff_roles_window)
        elif role == "Waiting Staff":
            waiting_staff_options(selected_branch_info, staff_roles_window)
        elif role == "Kitchen Staff":
            kitchen_staff_options(selected_branch_info, staff_roles_window)
        else:
            show_staff(selected_branch_info, role, staff_roles_window)

    button_waiting_staff = tk.Button(center_frame, text="Waiting Staff", command=lambda: button_click("Waiting Staff"), font=('Helvetica', 12, 'bold'), height=2, width=15)
    button_manager = tk.Button(center_frame, text="Manager", command=lambda: button_click("Manager"), font=('Helvetica', 12, 'bold'), height=2, width=15)
    button_kitchen_staff = tk.Button(center_frame, text="Kitchen Staff", command=lambda: button_click("Kitchen Staff"), font=('Helvetica', 12, 'bold'), height=2, width=15)
    
    show_all_staff_button = tk.Button(center_frame, text="Show all staff", command=lambda: show_staff(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
    add_staff_button = tk.Button(center_frame, text="Add staff", command=add_staff, font=('Helvetica', 12, 'bold'), height=2, width=15)
    remove_staff_button = tk.Button(center_frame, text="Remove staff", command=remove_staff, font=('Helvetica', 12, 'bold'), height=2, width=15)

    button_manager.grid(row=0, column=0, padx=10, pady=10)
    button_waiting_staff.grid(row=0, column=1, padx=10, pady=10)
    button_kitchen_staff.grid(row=0, column=2, padx=10, pady=10)
    show_all_staff_button.grid(row=1, column=0, padx=10, pady=10)
    add_staff_button.grid(row=1, column=1, padx=10, pady=10)
    remove_staff_button.grid(row=1, column=2, padx=10, pady=10)

def select_branch():
    window.withdraw()
    def help_on_enter(e):
            help_button.config(bg='gray')  # Change color on hover

    def help_on_leave(e):
        help_button.config(bg='lightgrey') 
    def open_help():
        help_window = tk.Toplevel(window)
        help_window.title("Help")
        help_window.geometry("400x300")  # Adjust size as needed

        # Text area for comments
        comment_text = tk.Text(help_window, height=10, width=40)
        comment_text.pack(pady=10)
        def submit_comment():
            comment = comment_text.get("1.0", "end-1c")
            print("Comment submitted:", comment)  # Replace with actual processing logic
            help_window.destroy()
        submit_button = tk.Button(help_window, text="Submit Comment", command=submit_comment)
        submit_button.pack(pady=10)
    hr_options_window = tk.Toplevel(window)
    hr_options_window.title("HR Director Branches")
    hr_options_window.state('zoomed')

    # hr_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
    top_border = tk.Canvas(hr_options_window, height=50, bg='black')
    top_border.pack(side='top', fill='x')    
    main_frame = tk.Frame(hr_options_window)
    main_frame.pack(padx=20, pady=20)
    title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
    title_label.pack(pady=(0, 10))
    help_font = tkFont.Font(family="Arial", size=25, weight="bold")
    help_button = tk.Button(top_border, text="Help", command=open_help, font=help_font, bg='white', relief='groove', bd=2)
    help_button.pack(side='right', padx=10, pady=5)
    help_button.bind("<Enter>", help_on_enter)
    help_button.bind("<Leave>", help_on_leave)
    center_frame = tk.Frame(hr_options_window)
    center_frame.pack(expand=True)
    center_frame.grid_columnconfigure(0, weight=1)
    logo_image = Image.open("restt.png")  # Replace with your logo path
    logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
    logo_label.image = logo_photo  # Keep a reference
    logo_label.pack(side='left', padx=10, pady=5)
    
    cursor = db.cursor(buffered=True)
    branch_query = "SELECT City, PostCode FROM Branch WHERE NOT BranchID = 'BM'"
    cursor.execute(branch_query)
    branch_results = cursor.fetchall()

    branch_names = sorted([f"{city}, {postcode}" for city, postcode in branch_results])

    selected_branch = tk.StringVar(hr_options_window)
    selected_branch.set(branch_names[0] if branch_names else "")

    # Dropdown for selecting a branch
    branch_dropdown = tk.OptionMenu(center_frame, selected_branch, *branch_names)
    branch_dropdown.grid(row=0, column=0, pady=10)
    
    def select_branch():
        chosen_branch_info = selected_branch.get()
        open_staff_roles_window(chosen_branch_info)
        hr_options_window.destroy()

    select_branch_button = tk.Button(center_frame, text="Select Branch", command=select_branch, **buttonStyle)
    select_branch_button.grid(row=1, column=0, pady=10)

    # Separator


    # Dropdown for removing a branch
    selected_remove_branch = tk.StringVar(hr_options_window)
    selected_remove_branch.set(branch_names[0] if branch_names else "")
    
    add_branch_button = tk.Button(center_frame, text="Add New Branch", command=lambda: add_branch_window(hr_options_window), **buttonStyle)
    add_branch_button.grid(row=2, column=0, pady=10)

    remove_branch_dropdown = tk.OptionMenu(center_frame, selected_remove_branch, *branch_names)
    remove_branch_dropdown.grid(row=3, column=0, pady=10)

    remove_branch_button = tk.Button(center_frame, text="Remove Branch", command=lambda: remove_branch(selected_remove_branch.get(), hr_options_window), **buttonStyle)
    remove_branch_button.grid(row=4, column=0, pady=10)
    def logout():
        hr_options_window.destroy()
        window.deiconify()

    logout_button = tk.Button(center_frame, text="Logout", command=logout, **buttonStyle)
    logout_button.grid(row=5, column=0, pady=10)

    hr_options_window.protocol("WM_DELETE_WINDOW", select_branch_close)

def waiting_staff_Login(email_entry, password_entry):
    # Close the previous window
    window.withdraw()

    #get branch id from staff email and password
    cursor = db.cursor()
    cursor.execute("SELECT BranchID FROM Account WHERE Email = %s AND Password = %s", (email_entry.get(), password_entry.get()))
    branch_id = cursor.fetchone()[0]
    cursor.close()

    #get account id from staff email and password
    cursor = db.cursor()
    cursor.execute("SELECT AccountID FROM Account WHERE Email = %s AND Password = %s", (email_entry.get(), password_entry.get()))
    account_id = cursor.fetchone()[0]
    cursor.close()

    #get branch info from branch id
    cursor = db.cursor()
    cursor.execute("SELECT City, PostCode FROM Branch WHERE BranchID = %s", (branch_id,))
    selected_branch_info = cursor.fetchone()
    cursor.close()

    waiting_staff_window = tk.Toplevel(window)
    waiting_staff_window.title(f"Waiting Staff Options - {selected_branch_info}")
    waiting_staff_window.state('zoomed')
    # waiting_staff_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

    top_border = tk.Canvas(waiting_staff_window, height=50, bg='black')
    top_border.pack(side='top', fill='x')    
    main_frame = tk.Frame(waiting_staff_window)
    main_frame.pack(padx=20, pady=20)
    title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
    title_label.pack(pady=(0, 10))
    center_frame = tk.Frame(waiting_staff_window)
    center_frame.pack(expand=True)
    center_frame.grid_columnconfigure(0, weight=1)
    logo_image = Image.open("restt.png")  # Replace with your logo path
    logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
    logo_label.image = logo_photo  # Keep a reference
    logo_label.pack(side='left', padx=10, pady=5)
    # Center frame for holding the buttons
    center_frame = tk.Frame(waiting_staff_window)
    center_frame.pack(expand=True)

    # Define functionalities for each button (placeholder functions)
    def order():
        order_window = tk.Toplevel(window)
        order_window.title("Order")
        order_window.state('zoomed')
        # take_order_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
        top_border = tk.Canvas(order_window, height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(order_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(order_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        def take_order(selected_branch_info):
            # Create a new window for taking an order
            take_order_window = tk.Toplevel(window)
            take_order_window.title("Take Order")
            take_order_window.state('zoomed')
            # take_order_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
            top_border = tk.Canvas(take_order_window, height=50, bg='black')
            top_border.pack(side='top', fill='x')    
            main_frame = tk.Frame(take_order_window)
            main_frame.pack(padx=20, pady=20)
            title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
            title_label.pack(pady=(0, 10))
            center_frame = tk.Frame(take_order_window)
            center_frame.pack(expand=True)
            center_frame.grid_columnconfigure(0, weight=1)
            logo_image = Image.open("restt.png")  # Replace with your logo path
            logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
            logo_label.image = logo_photo  # Keep a reference
            logo_label.pack(side='left', padx=10, pady=5)
            # Function to fetch available stock
            def get_available_stock(branch_id):
                cursor = db.cursor()
                cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s AND AmountInStock > 0", (branch_id,))
                available_stock = cursor.fetchall()
                cursor.close()
                return available_stock

            # Function to fetch available tables
            def get_available_tables(branch_id):
                cursor = db.cursor()
                cursor.execute("SELECT TableID FROM Tables WHERE BranchID = %s", (branch_id,))
                available_tables = cursor.fetchall()
                cursor.close()
                return available_tables

            # Fetch available stock and tables for the branch
            available_stock = get_available_stock(branch_id)
            available_tables = get_available_tables(branch_id)


            # Dropdown for selecting stock
            stock_var = tk.StringVar(take_order_window)
            stock_var.set("Select stock")
            stock_dropdown_label = tk.Label(take_order_window, text="Select Stock:", font=fontStyle)
            stock_dropdown_label.pack()
            stock_dropdown = tk.OptionMenu(take_order_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
            stock_dropdown.pack()

            # Dropdown for selecting a table
            table_var = tk.StringVar(take_order_window)
            table_var.set("Select table")
            table_dropdown_label = tk.Label(take_order_window, text="Select Table:", font=fontStyle)
            table_dropdown_label.pack()
            table_dropdown = tk.OptionMenu(take_order_window, table_var, *[table[0] for table in available_tables])
            table_dropdown.pack()

            # Function to create a new order entry
            def submit_order_details():
                selected_stock_id = stock_var.get().split(" - ")[0]
                selected_table_id = table_var.get()

                if selected_stock_id.startswith("Select") or selected_table_id.startswith("Select"):
                    messagebox.showerror("Error", "You must select a valid stock and table.")
                    return

                cursor = db.cursor()
                try:
                    # Generate a new unique TrackID
                    cursor.execute("SELECT TrackID FROM orderr ORDER BY CAST(SUBSTRING(TrackID, 2) AS UNSIGNED) DESC LIMIT 1;")
                    last_track_id = cursor.fetchone()[0]
                    last_track_id_number = int(last_track_id[1:]) if last_track_id else 0
                    new_track_id = f"T{last_track_id_number + 1}"

                    # Insert the new order
                    insert_query = "INSERT INTO Orderr (TrackID, StockID, TableID) VALUES (%s, %s, %s)"
                    cursor.execute(insert_query, (new_track_id, selected_stock_id, selected_table_id))

                    # Update stock amount
                    update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock - 1 WHERE StockID = %s"
                    cursor.execute(update_stock_query, (selected_stock_id,))

                    # Set the table as unavailable
                    update_table_query = "UPDATE Tables SET Availability = 0 WHERE TableID = %s"
                    cursor.execute(update_table_query, (selected_table_id,))

                    # Commit the transaction
                    db.commit()
                    messagebox.showinfo("Success", f"Order with tracking ID {new_track_id} successfully taken for table {selected_table_id}.")
                    
                except Exception as e:
                    db.rollback()
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    cursor.close()
                    
            def remove_order(branch_id):
                remove_order_window = tk.Toplevel(window)
                remove_order_window.title("Remove Order")
                remove_order_window.state('zoomed')
                # remove_order_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                # Fetch all orders with their corresponding StockType for the branch
                cursor = db.cursor()
                cursor.execute("""
                    SELECT o.TrackID, s.StockType, o.TableID 
                    FROM Orderr o 
                    INNER JOIN Stock s ON o.StockID = s.StockID 
                    WHERE o.TableID IN (
                        SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 0
                    )
                """, (branch_id,))
                order_results = cursor.fetchall()
                cursor.close()

                # Create a list of orders for the dropdown, showing StockType instead of StockID
                order_list = [f"{row[0]}: {row[1]} - Table ID: {row[2]}"
                            for row in order_results] if order_results else []

                if order_list:
                    order_var = tk.StringVar(remove_order_window)
                    order_var.set(order_list[0])  # Set default value
                    order_dropdown = tk.OptionMenu(remove_order_window, order_var, *order_list)
                    order_dropdown.pack()
                    
                    def remove_selected_order():
                        selected_track_id = order_var.get().split(":")[0]
                        cursor = db.cursor()
                        try:
                            # Start transaction
                            cursor.execute("START TRANSACTION")
                            
                            # Delete the order
                            delete_query = "DELETE FROM Orderr WHERE TrackID = %s"
                            cursor.execute(delete_query, (selected_track_id,))

                            # Update the availability of the table
                            # Ensure to retrieve and update the correct TableID from the Order
                            update_table_query = """
                            UPDATE Tables SET Availability = 1 
                            WHERE TableID = (
                                SELECT TableID FROM Orderr WHERE TrackID = %s
                            )
                            """
                            cursor.execute(update_table_query, (selected_track_id,))

                            # Commit the changes
                            db.commit()
                            messagebox.showinfo("Success", f"Order {selected_track_id} has been cancelled")
                            
                            remove_order_window.destroy()
                        except Exception as e:
                            db.rollback()
                            messagebox.showerror("Error", f"An error occurred: {e}")
                        finally:
                            cursor.close()

                    remove_button = tk.Button(remove_order_window, text="Remove Order", command=remove_selected_order, **buttonStyle)
                    remove_button.pack()
                    back_button = tk.Button(remove_order_window, text="Back", command=remove_order_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)
                else:
                    tk.Label(remove_order_window, text="No orders found for this branch.", font=fontStyle).pack()
                    back_button = tk.Button(remove_order_window, text="Back", command=remove_order_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

            # Button to submit the order details
            submit_button = tk.Button(take_order_window, text="Submit Order", command=submit_order_details, **buttonStyle)
            submit_button.pack()

            # Button to go back to the previous window
            back_button = tk.Button(take_order_window, text="Back", command=take_order_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

            # Add a button for removing an order in the take_order_window
            remove_order_button = tk.Button(take_order_window, text="Remove Order", command=lambda: remove_order(branch_id), **buttonStyle)
            remove_order_button.pack()

        def view_orders(selected_branch_info):
            view_orders_window = tk.Toplevel(window)
            view_orders_window.title("View Orders")
            view_orders_window.state('zoomed')
            # view_orders_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

            # Fetch all orders with their corresponding StockType for the branch
            cursor = db.cursor()
            cursor.execute("""SELECT o.TrackID, s.StockType, o.TableID
                                FROM Orderr o
                                INNER JOIN Stock s ON o.StockID = s.StockID
                                WHERE o.TableID IN (
                                    SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 0
                                )""", (branch_id,))
            
            order_results = cursor.fetchall()
            cursor.close()

            # print all the orders in the window

            if order_results:
                for track_id, stock_type, table_id in order_results:
                    order_info = f"{track_id}: {stock_type} - Table ID: {table_id}"
                    tk.Label(view_orders_window, text=order_info, font=fontStyle).pack()
            else:
                tk.Label(view_orders_window, text="No orders found for this branch.", font=fontStyle).pack()

            back_button = tk.Button(view_orders_window, text="Back", command=view_orders_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

        def print_receipt(selected_branch_info):
            print_receipt_window = tk.Toplevel(window)
            print_receipt_window.title("Print Receipt")
            print_receipt_window.state('zoomed')
            # print_receipt_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

            #dropdown for selecting the table
            def get_available_tables(branch_id):
                cursor = db.cursor()
                cursor.execute("SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 0", (branch_id,))
                return cursor.fetchall()
            
            available_tables = get_available_tables(branch_id)

            #if there are no available tables, then the dropdown will show "No tables available"
            if not available_tables:
                available_tables = ["No tables available"]
                table_var = tk.StringVar(print_receipt_window)
                table_var.set(available_tables[0])
                table_dropdown_label = tk.Label(print_receipt_window, text="Select Table:", font=fontStyle)
                table_dropdown_label.pack()
                table_dropdown = tk.OptionMenu(print_receipt_window, table_var, *[table for table in available_tables])
                table_dropdown.pack()
            else:
                table_var = tk.StringVar(print_receipt_window)
                table_var.set(available_tables[0][0] if available_tables else "No tables available")
                table_dropdown_label = tk.Label(print_receipt_window, text="Select Table:", font=fontStyle)
                table_dropdown_label.pack()
                table_dropdown = tk.OptionMenu(print_receipt_window, table_var, *[table[0] for table in available_tables])
                table_dropdown.pack()


            #generate receipt
            def generate_receipt():
                selected_table = table_var.get()
                if selected_table == "No tables available":
                    messagebox.showerror("Error", "No available tables to print receipt for.")
                    return

                #fetch all the orders for the selected table
                cursor = db.cursor()
                cursor.execute("""
                    SELECT o.TrackID, s.StockType, o.TableID, s.Price
                    FROM Orderr o
                    INNER JOIN Stock s ON o.StockID = s.StockID
                    WHERE o.TableID = %s
                """, (selected_table,))
                order_results = cursor.fetchall()
                cursor.close()

                if order_results:
                    #calculate total price
                    total_price = sum([order[3] for order in order_results])
                    receipt = f"Table ID: {selected_table}\n"
                    receipt += f"{'-' * 20}\n"
                    for track_id, stock_type, table_id, price in order_results:
                        receipt += f"{track_id}: {stock_type} - £{price}\n"
                    receipt += f"{'-' * 20}\n"
                    receipt += f"Total: £{total_price}"
                    tk.Label(print_receipt_window, text=receipt, font=fontStyle).pack()

                    #update the table availability
                    cursor = db.cursor()
                    cursor.execute("UPDATE Tables SET Availability = 1 WHERE TableID = %s", (selected_table,))
                    cursor.close()

                    #add 1 point to the account
                    cursor = db.cursor()
                    cursor.execute("UPDATE Account SET Points = Points + 1 WHERE AccountID = %s", (account_id,))
                    cursor.close()


                    #delete the orders
                    cursor = db.cursor()
                    cursor.execute("DELETE FROM Orderr WHERE TableID = %s", (selected_table,))
                    cursor.close()

                    #update the receipt table
                    cursor = db.cursor()
                    cursor.execute("SELECT ReceiptID FROM receipt ORDER BY CAST(SUBSTRING(ReceiptID, 2) AS UNSIGNED) DESC Limit 1;")
                    last_receipt_id = cursor.fetchone()[0]
                    last_receipt_id_number = int(last_receipt_id[1:]) if last_receipt_id else 0
                    new_receipt_id = f"R{last_receipt_id_number + 1}"
                    cursor.execute("INSERT INTO Receipt (ReceiptID, TableID, Price, BranchID) VALUES (%s, %s, %s, %s)", (new_receipt_id, selected_table, total_price, branch_id))
                    cursor.close()

                    #commit the changes
                    db.commit()

                    #back button to go back to the previous window
                    back_button = tk.Button(print_receipt_window, text="Back", command=print_receipt_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

                else:
                    tk.Label(print_receipt_window, text="No orders found for this table.", font=fontStyle).pack()

            #button to generate receipt
            generate_receipt_button = tk.Button(print_receipt_window, text="Generate Receipt", command=generate_receipt, **buttonStyle)
            generate_receipt_button.pack()

            #back button to go back to the previous window
            back_button = tk.Button(print_receipt_window, text="Back", command=print_receipt_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

        # 3 buttons for taking order, viewing orders, and print recipt
        take_order_button = tk.Button(order_window, text="Take Order", command=lambda: [order_window.destroy(), take_order(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)
        view_orders_button = tk.Button(order_window, text="View Orders", command=lambda: [order_window.destroy(), view_orders(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)
        print_receipt_button = tk.Button(order_window, text="Print Receipt", command=lambda: [order_window.destroy(), print_receipt(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)

        # Pack buttons in the center frame
        take_order_button.pack(pady=10)
        view_orders_button.pack(pady=10)
        print_receipt_button.pack(pady=10)

        #back button to go back to the previous window
        back_button = tk.Button(order_window, text="Back", command=lambda: [order_window.destroy()], **buttonStyle)
        back_button.pack(pady=10)

    def reservation():
        reservation_window = tk.Toplevel(window)
        reservation_window.title("Reservation")
        reservation_window.state('zoomed')
        # reservation_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

        def take_reservation(selected_branch_info):
            # Create a new window for taking reservation
            take_reservation_window = tk.Toplevel(window)
            take_reservation_window.title("Take Reservation")
            take_reservation_window.state('zoomed')
            # take_reservation_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

            # Entry fields for reservation details
            customer_name_label = tk.Label(take_reservation_window, text="Customer Name:", font=fontStyle)
            customer_name_label.pack()
            customer_name_entry = tk.Entry(take_reservation_window, font=fontStyle)
            customer_name_entry.pack()

            #customer phone number entry
            customer_phone_label = tk.Label(take_reservation_window, text="Customer Phone Number:", font=fontStyle)
            customer_phone_label.pack()
            customer_phone_entry = tk.Entry(take_reservation_window, font=fontStyle)
            customer_phone_entry.pack()

            #date entry
            date_label = tk.Label(take_reservation_window, text="Date (YYYY-MM-DD):", font=fontStyle)
            date_label.pack()
            date_entry = tk.Entry(take_reservation_window, font=fontStyle)
            date_entry.pack()

            #time entry
            time_label = tk.Label(take_reservation_window, text="Time (HH:MM):", font=fontStyle)
            time_label.pack()
            time_entry = tk.Entry(take_reservation_window, font=fontStyle)
            time_entry.pack()

            # Function to fetch available tables
            def get_available_tables(branch_id):
                cursor = db.cursor()
                cursor.execute("SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 1", (branch_id,))
                return cursor.fetchall()

            # Function to update table availability
            def update_table_availability(table_id, availability):
                cursor = db.cursor()
                cursor.execute("UPDATE Tables SET Availability = %s WHERE TableID = %s", (availability, table_id))
                cursor.close()

            # Dropdown for selecting a table
            available_tables = get_available_tables(branch_id)
            table_var = tk.StringVar(take_reservation_window)
            table_var.set(available_tables[0][0] if available_tables else "No tables available")
            table_dropdown_label = tk.Label(take_reservation_window, text="Available Tables:", font=fontStyle)
            table_dropdown_label.pack()
            table_dropdown = tk.OptionMenu(take_reservation_window, table_var, *[table[0] for table in available_tables])
            table_dropdown.pack()

            # Function to create a new reservation
            def submit_reservation_details():
                customer_name = customer_name_entry.get()
                customer_phone = customer_phone_entry.get()
                date = date_entry.get()
                time = time_entry.get()
                selected_table = table_var.get()

                if selected_table == "No tables available":
                    messagebox.showerror("Error", "No available tables to reserve.")
                    return

                # Start transaction
                cursor = db.cursor()
                cursor.execute("START TRANSACTION")
                try:
                    # Create a new reservation ID
                    cursor.execute("SELECT MAX(ReservationID) FROM Reservation")
                    last_id = cursor.fetchone()[0]
                    last_id_number = int(last_id[1:]) if last_id else 0
                    new_reservation_id = f"R{last_id_number + 1}"

                    # Insert the new reservation
                    insert_query = """
                        INSERT INTO Reservation (ReservationID, CustomerName, CustomerPhoneNO, Date, Time, BranchID, TableID)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (new_reservation_id, customer_name, customer_phone, date, time, branch_id, selected_table))

                    # Update table availability
                    update_table_availability(selected_table, 0)

                    #add 1 point to the account
                    cursor.execute("UPDATE Account SET Points = Points + 1 WHERE AccountID = %s", (account_id,))

                    # Commit the transaction
                    db.commit()
                    messagebox.showinfo("Success", f"Reservation {new_reservation_id} successfully added and table {selected_table} is now reserved.")
                    take_reservation_window.destroy()
                except Exception as e:
                    db.rollback()
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    cursor.close()

            # Button to submit the reservation details
            submit_button = tk.Button(take_reservation_window, text="Submit Reservation", command=submit_reservation_details, **buttonStyle)
            submit_button.pack()

            # Button to go back to the previous window
            back_button = tk.Button(take_reservation_window, text="Back", command=take_reservation_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

        def view_reservations():
            # Create a new window for viewing reservation
            view_reservation_window = tk.Toplevel(window)
            view_reservation_window.title("View Reservation")
            view_reservation_window.state('zoomed')
            # view_reservation_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

            #fetch reservation details from the database
            reservation_query = """
                SELECT ReservationID, CustomerName, CustomerPhoneNO, Date, Time, TableID
                FROM Reservation
                WHERE BranchID = %s
            """
            cursor = db.cursor()
            cursor.execute(reservation_query, (branch_id,))
            reservation_results = cursor.fetchall()

            # show all the reservations in the window
            if reservation_results:
                for reservation_id, customer_name, customer_phone, date, time, table_id in reservation_results:
                    reservation_info = f"{reservation_id}: {customer_name} - {customer_phone} - {date} - {time} - ({table_id})"
                    tk.Label(view_reservation_window, text=reservation_info, font=fontStyle).pack()
            else:
                tk.Label(view_reservation_window, text="No reservation found for this branch.", font=fontStyle).pack()

            back_button = tk.Button(view_reservation_window, text="Back", command=view_reservation_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

        def cancel_reservation(selected_branch_info):
            # Create a new window for canceling reservation
            cancel_reservation_window = tk.Toplevel(window)
            cancel_reservation_window.title("Cancel Reservation")
            cancel_reservation_window.state('zoomed')
            # cancel_reservation_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

            # Fetch reservation details from the database for the branch
            cursor = db.cursor()
            reservation_query = """
                SELECT ReservationID, CustomerName, CustomerPhoneNO, Date, Time, TableID
                FROM Reservation
                WHERE BranchID = %s
            """
            cursor.execute(reservation_query, (branch_id,))
            reservation_results = cursor.fetchall()
            cursor.close()

            # Create a list of reservations for the dropdown
            reservation_list = [
                f"{row[0]}: {row[1]} - {row[2]} - {row[3]} - {row[4]}"
                for row in reservation_results
            ] if reservation_results else []

            reservation_var = tk.StringVar(cancel_reservation_window)
            reservation_var.set(reservation_list[0] if reservation_list else "No reservations available")
            reservation_dropdown = tk.OptionMenu(cancel_reservation_window, reservation_var, *reservation_list)
            reservation_dropdown.pack()

            def cancel_selected_reservation():
                selected_reservation_id = reservation_var.get().split(":")[0]
                cursor = db.cursor()
                try:
                    # Start transaction
                    cursor.execute("START TRANSACTION")
                    
                    # Get the TableID of the reservation to be canceled
                    get_table_query = "SELECT TableID FROM Reservation WHERE ReservationID = %s"
                    cursor.execute(get_table_query, (selected_reservation_id,))
                    table_id = cursor.fetchone()
                    
                    if table_id:
                        table_id = table_id[0]  # Extract the TableID
                        
                        # Delete the reservation
                        delete_query = "DELETE FROM Reservation WHERE ReservationID = %s"
                        cursor.execute(delete_query, (selected_reservation_id,))
                        
                        # Update the availability of the table
                        update_table_query = "UPDATE Tables SET Availability = 1 WHERE TableID = %s"
                        cursor.execute(update_table_query, (table_id,))
                        
                        # Commit the changes
                        db.commit()
                        messagebox.showinfo("Success", f"Reservation {selected_reservation_id} has been canceled and table {table_id} is now available.")
                    else:
                        db.rollback()  # Rollback if no TableID is found for the reservation
                        messagebox.showinfo("Notice", f"Reservation {selected_reservation_id} was not found or has no associated table.")
                    
                    cancel_reservation_window.destroy()
                except Exception as e:
                    db.rollback()
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    cursor.close()

            cancel_button = tk.Button(cancel_reservation_window, text="Cancel Reservation", command=cancel_selected_reservation, **buttonStyle)
            cancel_button.pack()

            back_button = tk.Button(cancel_reservation_window, text="Back", command=cancel_reservation_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

        # 3 buttons for taking reservation, viewing reservations, and cancel reservation
        take_reservation_button = tk.Button(reservation_window, text="Take Reservation", command=lambda: [reservation_window.destroy(), take_reservation(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)
        view_reservations_button = tk.Button(reservation_window, text="View Reservations", command=lambda: [reservation_window.destroy(), view_reservations()], font=('Helvetica', 12, 'bold'), height=2, width=15)
        cancel_reservation_button = tk.Button(reservation_window, text="Cancel Reservation", command=lambda: [reservation_window.destroy(), cancel_reservation(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)

        # Pack buttons in the center frame
        take_reservation_button.pack(pady=10)
        view_reservations_button.pack(pady=10)
        cancel_reservation_button.pack(pady=10)

        #back button to go back to the previous window
        back_button = tk.Button(reservation_window, text="Back", command=lambda: [reservation_window.destroy()], **buttonStyle)
        back_button.pack(pady=10)
        


    # Create buttons
    take_order_button = tk.Button(center_frame, text="Orders", command=order, font=('Helvetica', 12, 'bold'), height=2, width=15)
    book_reservation_button = tk.Button(center_frame, text="Reservations", command=reservation, font=('Helvetica', 12, 'bold'), height=2, width=15)

    # Pack buttons in the center frame
    take_order_button.grid(row=0, column=0, padx=10, pady=10)
    book_reservation_button.grid(row=0, column=1, padx=10, pady=10)

    #logout button to go back to the login screen
    logout_button = tk.Button(center_frame, text="Logout", command=lambda: [waiting_staff_window.destroy(), window.deiconify()], **buttonStyle)
    logout_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

def Kitchen_Staff_Login(email_entry, password_entry):
    # Close the previous window
    window.withdraw()

    #get branch id from staff email and password
    cursor = db.cursor()
    cursor.execute("SELECT BranchID FROM Account WHERE Email = %s AND Password = %s", (email_entry.get(), password_entry.get()))
    branch_id = cursor.fetchone()[0]
    cursor.close()

    #get account id from staff email and password
    cursor = db.cursor()
    cursor.execute("SELECT AccountID FROM Account WHERE Email = %s AND Password = %s", (email_entry.get(), password_entry.get()))
    account_id = cursor.fetchone()[0]
    cursor.close()

    #get branch info from branch id
    cursor = db.cursor()
    cursor.execute("SELECT City, PostCode FROM Branch WHERE BranchID = %s", (branch_id,))
    selected_branch_info = cursor.fetchone()
    cursor.close()

    kitchen_staff_window = tk.Toplevel(window)
    kitchen_staff_window.title(f"Kitchen Staff Options - {selected_branch_info}")
    kitchen_staff_window.state('zoomed')
    top_border = tk.Canvas(kitchen_staff_window, height=50, bg='black')
    top_border.pack(side='top', fill='x')    
    main_frame = tk.Frame(kitchen_staff_window)
    main_frame.pack(padx=20, pady=20)
    title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
    title_label.pack(pady=(0, 10))
    center_frame = tk.Frame(kitchen_staff_window)
    center_frame.pack(expand=True)
    center_frame.grid_columnconfigure(0, weight=1)
    logo_image = Image.open("restt.png")  # Replace with your logo path
    logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
    logo_label.image = logo_photo  # Keep a reference
    logo_label.pack(side='left', padx=10, pady=5)   
    # kitchen_staff_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

    # Center frame for holding the buttons
    center_frame = tk.Frame(kitchen_staff_window)
    center_frame.pack(expand=True)

    # Define functionalities for each button (placeholder functions)

    def view_orders():
        view_orders_window = tk.Toplevel(window)
        view_orders_window.title("View Orders")
        view_orders_window.state('zoomed')
        # view_orders_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
        top_border = tk.Canvas(view_orders_window, height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(view_orders_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(view_orders_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        # Listbox to display orders
        orders_listbox = tk.Listbox(view_orders_window, width=50, height=20)
        orders_listbox.pack(pady=20)

        # Fetch all orders with their corresponding StockType for the branch
        cursor = db.cursor()
        cursor.execute("""SELECT o.TrackID, s.StockType, o.TableID
                        FROM Orderr o
                        INNER JOIN Stock s ON o.StockID = s.StockID
                        WHERE o.TableID IN (
                            SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 0
                        )""", (branch_id,))
        
        order_results = cursor.fetchall()
        cursor.close()

        # Populate the listbox with orders
        for order in order_results:
            orders_listbox.insert(tk.END, f"{order[0]}: {order[1]} - Table ID: {order[2]}")

        def complete_order():
            # Check if an order is selected
            if orders_listbox.curselection():
                index = orders_listbox.curselection()[0]
                selected_order = orders_listbox.get(index)
                track_id = selected_order.split(":")[0]

                # Process to remove the order from the system and add points to the account
                cursor = db.cursor()
                try:
                    cursor.execute("START TRANSACTION")

                    #add 1 point to the account
                    cursor.execute("UPDATE Account SET Points = Points + 1 WHERE AccountID = %s", (account_id,))

                    db.commit()
                    messagebox.showinfo("Success", "Order completed.")

                    # Remove the order from the ListBox
                    orders_listbox.delete(index)

                except Exception as e:
                    db.rollback()
                    messagebox.showerror("Error", str(e))
                finally:
                    cursor.close()

        # Button to mark an order as completed
        complete_order_button = tk.Button(view_orders_window, text="Complete Order", command=complete_order, **buttonStyle)
        complete_order_button.pack(pady=10)

        # Button to go back to the previous window
        back_button = tk.Button(view_orders_window, text="Back", command=view_orders_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

    def update_stock():
        
        stock_options_window = tk.Toplevel(window)
        stock_options_window.title(f"Stock Options - {selected_branch_info}")
        stock_options_window.state('zoomed')
        top_border = tk.Canvas(stock_options_window, height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(stock_options_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(stock_options_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        stock_center_frame = tk.Frame(stock_options_window)
        stock_center_frame.pack(expand=True)
        # stock_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

        # Define functionalities for each button 
        view_stock_button = tk.Button(stock_center_frame, text="View Stock", command=lambda: view_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
        add_stock_button = tk.Button(stock_center_frame, text="Add Stock", command=lambda: add_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
        remove_stock_button = tk.Button(stock_center_frame, text="Remove Stock", command=lambda: remove_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
        
        # Pack buttons in the center frame
        view_stock_button.grid(row=0, column=0, padx=10, pady=10)
        add_stock_button.grid(row=0, column=1, padx=10, pady=10)
        remove_stock_button.grid(row=0, column=2, padx=10, pady=10)

        # Back button to go back to the previous window
        back_button = tk.Button(stock_options_window, text="Back", command=stock_options_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

    def view_stock(selected_branch_info):
        view_stock_window = tk.Toplevel(window)
        view_stock_window.title("View Stock")
        view_stock_window.state('zoomed')
        # view_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
        top_border = tk.Canvas(view_stock_window , height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(view_stock_window )
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(view_stock_window )
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        # Fetch all stock for the branch
        cursor = db.cursor()
        cursor.execute("SELECT StockID, StockType, AmountInStock, Price FROM Stock WHERE BranchID = %s", (branch_id,))
        stock_results = cursor.fetchall()

        # Print all the stock in the window
        if stock_results:
            for stock_id, stock_type, amount_in_stock, price in stock_results:
                stock_info = f"{stock_id}: {stock_type} - Amount: {amount_in_stock} - Price: £{price}"
                tk.Label(view_stock_window, text=stock_info, font=fontStyle).pack()

        else:
            tk.Label(view_stock_window, text="No stock found for this branch.", font=fontStyle).pack()

        back_button = tk.Button(view_stock_window, text="Back", command=view_stock_window.destroy, **buttonStyle)
        back_button.pack(pady=10)
    
    def add_stock(selected_branch_info):
        add_stock_window = tk.Toplevel(window)
        add_stock_window.title("Add Stock")
        add_stock_window.state('zoomed')
        # add_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
        top_border = tk.Canvas(add_stock_window , height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(add_stock_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(add_stock_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        # Entry fields for stock details
        stock_type_label = tk.Label(add_stock_window, text="Stock Type:", font=fontStyle)
        stock_type_label.pack()
        stock_type_entry = tk.Entry(add_stock_window, font=fontStyle)
        stock_type_entry.pack()

        amount_in_stock_label = tk.Label(add_stock_window, text="Amount in Stock:", font=fontStyle)
        amount_in_stock_label.pack()
        amount_in_stock_entry = tk.Entry(add_stock_window, font=fontStyle)
        amount_in_stock_entry.pack()

        price_label = tk.Label(add_stock_window, text="Price:", font=fontStyle)
        price_label.pack()
        price_entry = tk.Entry(add_stock_window, font=fontStyle)
        price_entry.pack()

        # Submit function
        def submit_stock_details():
            stock_type = stock_type_entry.get()
            amount_in_stock = amount_in_stock_entry.get()
            price = price_entry.get()

            # Generate Stock ID based on the last StockID
            cursor = db.cursor()
            cursor.execute("SELECT MAX(StockID) FROM Stock")
            last_stock_id_row = cursor.fetchone()
            last_stock_id = last_stock_id_row[0] if last_stock_id_row and last_stock_id_row[0] else "S0"
            new_stock_id_number = int(last_stock_id.lstrip("S")) + 1
            new_stock_id = "S" + str(new_stock_id_number)

            # Insert into database (adjust according to your schema)
            insert_query = """
                INSERT INTO Stock (StockID, StockType, AmountInStock, Price, BranchID)
                SELECT %s, %s, %s, %s, Branch.BranchID
                FROM Branch
                WHERE BranchID = (%s)
            """
            try:
                cursor.execute(insert_query, (new_stock_id, stock_type, amount_in_stock, price, branch_id))
                db.commit()
                messagebox.showinfo("Success", f"Stock {new_stock_id} successfully added.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                add_stock_window.destroy()
                update_stock(selected_branch_info)

        submit_button = tk.Button(add_stock_window, text="Submit", command=submit_stock_details, **buttonStyle)
        submit_button.pack()
        back_button = tk.Button(add_stock_window, text="Back", command=add_stock_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

        # Separator
        ttk.Separator(add_stock_window, orient='horizontal').pack(fill='x', pady=10)

        #dropdown list of all available stock
        def get_available_stock(branch_id):
            cursor = db.cursor()
            cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s", (branch_id,))
            return cursor.fetchall()
        
        available_stock = get_available_stock(branch_id)

        stock_var = tk.StringVar(add_stock_window)
        stock_var.set("Select stock")
        stock_dropdown_label = tk.Label(add_stock_window, text="Select Stock:", font=fontStyle)
        stock_dropdown_label.pack()
        stock_dropdown = tk.OptionMenu(add_stock_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
        stock_dropdown.pack()

        # add ammoount to stock text box
        amount_to_add_label = tk.Label(add_stock_window, text="Amount to Add:", font=fontStyle)
        amount_to_add_label.pack()
        amount_to_add_entry = tk.Entry(add_stock_window, font=fontStyle)
        amount_to_add_entry.pack()

        #function to add stock
        def add_stock():
            selected_stock_id = stock_var.get().split(" - ")[0]
            amount_to_add = amount_to_add_entry.get()

            if selected_stock_id.startswith("Select"):
                messagebox.showerror("Error", "You must select a valid stock.")
                return

            cursor = db.cursor()
            try:
                #update the stock amount
                update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock + %s WHERE StockID = %s"
                cursor.execute(update_stock_query, (amount_to_add, selected_stock_id))
                db.commit()
                messagebox.showinfo("Success", f"{amount_to_add} of stock {selected_stock_id} successfully added.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                add_stock_window.destroy()
                update_stock(selected_branch_info)

        add_button = tk.Button(add_stock_window, text="Add Stock", command=add_stock, **buttonStyle)
        add_button.pack()

        #back button to go back to the previous window
        back_button = tk.Button(add_stock_window, text="Back", command=add_stock_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

    def remove_stock(selected_branch_info):
        remove_stock_window = tk.Toplevel(window)
        remove_stock_window.title("Remove Stock")
        remove_stock_window.state('zoomed')
        # remove_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

        # Fetch stock details from the database
        stock_query = """
            SELECT StockID, StockType
            FROM Stock
            WHERE BranchID = (
                SELECT BranchID
                FROM Branch
                WHERE BranchID = %s
            )
        """
        cursor = db.cursor()
        cursor.execute(stock_query, (branch_id,))
        stock_results = cursor.fetchall()

        # Create a list of stock for the dropdown
        stock_list = [f"{row[0]}: {row[1]}" for row in stock_results] if stock_results else []

        if stock_list:
            stock_var = tk.StringVar(remove_stock_window)
            stock_var.set(stock_list[0])
            stock_dropdown = tk.OptionMenu(remove_stock_window, stock_var, *stock_list)
            stock_dropdown.pack()
    
            def remove_selected_stock():
                selected = stock_var.get().split(":")[0]
                delete_query = "DELETE FROM Stock WHERE StockID = %s"
                try:
                    cursor.execute(delete_query, (selected,))
                    db.commit()
                    messagebox.showinfo("Success", f"Stock {selected} has been removed.")
                    remove_stock_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
            
            remove_button = tk.Button(remove_stock_window, text="Remove Stock", command=remove_selected_stock, **buttonStyle)
            remove_button.pack()
            back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

            #separator
            ttk.Separator(remove_stock_window, orient='horizontal').pack(fill='x', pady=10)

            #dropdown list of all available stock
            def get_available_stock(branch_id):
                cursor = db.cursor()
                cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s", (branch_id,))
                return cursor.fetchall()
            
            available_stock = get_available_stock(branch_id)

            stock_var = tk.StringVar(remove_stock_window)
            stock_var.set("Select stock")
            stock_dropdown_label = tk.Label(remove_stock_window, text="Select Stock:", font=fontStyle)
            stock_dropdown_label.pack()
            stock_dropdown = tk.OptionMenu(remove_stock_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
            stock_dropdown.pack()

            # add ammoount to stock text box
            amount_to_remove_label = tk.Label(remove_stock_window, text="Amount to Remove:", font=fontStyle)
            amount_to_remove_label.pack()
            amount_to_remove_entry = tk.Entry(remove_stock_window, font=fontStyle)
            amount_to_remove_entry.pack()

            #function to add stock
            def remove_stock():
                selected_stock_id = stock_var.get().split(" - ")[0]
                amount_to_remove = amount_to_remove_entry.get()

                if selected_stock_id.startswith("Select"):
                    messagebox.showerror("Error", "You must select a valid stock.")
                    return

                cursor = db.cursor()
                try:
                    #update the stock amount
                    update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock - %s WHERE StockID = %s"
                    cursor.execute(update_stock_query, (amount_to_remove, selected_stock_id))
                    db.commit()
                    messagebox.showinfo("Success", f"{amount_to_remove} of stock {selected_stock_id} successfully removed.")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    remove_stock_window.destroy()
                    update_stock(selected_branch_info)

            remove_button = tk.Button(remove_stock_window, text="Remove Stock", command=remove_stock, **buttonStyle)
            remove_button.pack()

            #back button to go back to the previous window
            back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
            back_button.pack(pady=10)
        else:
            tk.Label(remove_stock_window, text="No stock found to remove.", font=fontStyle).pack()
            back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
            back_button.pack(pady=10)
    
    # Create buttons
    view_orders_button = tk.Button(center_frame, text="View Orders", command=view_orders, font=('Helvetica', 12, 'bold'), height=2, width=15)
    update_stock_button = tk.Button(center_frame, text="Update Stock", command=update_stock, font=('Helvetica', 12, 'bold'), height=2, width=15)

    # Pack buttons in the center frame
    view_orders_button.grid(row=0, column=0, padx=10, pady=10)
    update_stock_button.grid(row=0, column=1, padx=10, pady=10)

    #logout button to go back to the login screen
    logout_button = tk.Button(center_frame, text="Logout", command=lambda: [kitchen_staff_window.destroy(), window.deiconify()], **buttonStyle)
    logout_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

def manager_Login(email_entry, password_entry):
    # Close the previous window
    window.withdraw()

    #get branch id from staff email and password
    cursor = db.cursor()
    cursor.execute("SELECT BranchID FROM Account WHERE Email = %s AND Password = %s", (email_entry.get(), password_entry.get()))
    branch_id = cursor.fetchone()[0]
    cursor.close()

    #get branch info from branch id
    cursor = db.cursor()
    cursor.execute("SELECT City, PostCode FROM Branch WHERE BranchID = %s", (branch_id,))
    branch_info = cursor.fetchone()
    selected_branch_info = f"{branch_info[0]} - {branch_info[1]}"
    cursor.close()

    staff_roles_window = tk.Toplevel(window)
    staff_roles_window.title(f"Manager Options - {selected_branch_info}")
    staff_roles_window.state('zoomed')
    # manager_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
    top_border = tk.Canvas(staff_roles_window , height=50, bg='black')
    top_border.pack(side='top', fill='x')    
    main_frame = tk.Frame(staff_roles_window)
    main_frame.pack(padx=20, pady=20)
    title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
    title_label.pack(pady=(0, 10))
    center_frame = tk.Frame(staff_roles_window)
    center_frame.pack(expand=True)
    center_frame.grid_columnconfigure(0, weight=1)
    logo_image = Image.open("restt.png")  # Replace with your logo path
    logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
    logo_label.image = logo_photo  # Keep a reference
    logo_label.pack(side='left', padx=10, pady=5)
    heading_roles_frame = tk.Frame(staff_roles_window)
    heading_roles_frame.pack(side=tk.TOP, pady=10)

    heading_roles_label = tk.Label(heading_roles_frame, text="Staff Roles", font=('Helvetica', 16, 'bold'))
    heading_roles_label.pack(side=tk.LEFT, padx=10)

    buttons_frame = tk.Frame(staff_roles_window)
    buttons_frame.pack(side=tk.TOP, pady=10)

    logout_button = tk.Button(staff_roles_window, text="Logout", command=lambda: [staff_roles_window.destroy(), window.deiconify()], **buttonStyle)
    logout_button.pack(side=tk.BOTTOM, pady=10)

    center_frame = tk.Frame(staff_roles_window)
    center_frame.pack(expand=True)

    def show_all_staff():
        # Create a new window for showing all staff in the branch
        show_all_staff_window = tk.Toplevel(window)
        show_all_staff_window.title("Show All Staff")
        top_border = tk.Canvas(show_all_staff_window , height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(show_all_staff_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(show_all_staff_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
        # Fetch all staff for the branch
        cursor = db.cursor()
        cursor.execute("SELECT AccountID, ForeName, SurName, Email, Role FROM Account WHERE BranchID = %s", (branch_id,))
        staff_results = cursor.fetchall()

        # Print all the staff in the window
        if staff_results:
            for account_id, forename, surname, email, role in staff_results:
                staff_info = f"{account_id}: {forename} {surname} - {email} - {role}"
                tk.Label(show_all_staff_window, text=staff_info, font=fontStyle).pack()

        else:
            tk.Label(show_all_staff_window, text="No staff found for this branch.", font=fontStyle).pack()

        back_button = tk.Button(show_all_staff_window, text="Back", command=show_all_staff_window.destroy, **buttonStyle)
        back_button.pack(pady=10)

    def add_staff():
        add_staff_window = tk.Toplevel(window)
        add_staff_window.title("Add Staff")
        add_staff_window.state('zoomed')
        # add_staff_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
        top_border = tk.Canvas(add_staff_window , height=50, bg='black')
        top_border.pack(side='top', fill='x')    
        main_frame = tk.Frame(add_staff_window)
        main_frame.pack(padx=20, pady=20)
        title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 10))
        center_frame = tk.Frame(add_staff_window)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        logo_image = Image.open("restt.png")  # Replace with your logo path
        logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(side='left', padx=10, pady=5)
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
        role_options = ['Waiting Staff', 'Kitchen Staff']
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
                WHERE BranchID = (%s)
            """
            try:
                cursor.execute(insert_query, (new_account_id, forename, surname, email, password, role, branch_id))
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
        # Create a new window for removing staff
        remove_staff_window = tk.Toplevel(window)
        remove_staff_window.title("Remove Staff")
        remove_staff_window.state('zoomed')
        # remove_staff_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

        # Fetch staff details from the database
        staff_query = """
            SELECT AccountID, ForeName, SurName, Email, Role
            FROM Account
            WHERE BranchID = (
                SELECT BranchID
                FROM Branch
                WHERE BranchID = %s AND Role != 'Manager'
            )
        """
        cursor = db.cursor()
        cursor.execute(staff_query, (branch_id,))
        staff_results = cursor.fetchall()

        # Create a list of staff for the dropdown
        staff_list = [f"{row[0]}: {row[1]} {row[2]} - {row[3]} - {row[4]}" for row in staff_results] if staff_results else []

        if staff_list:
            staff_var = tk.StringVar(remove_staff_window)
            staff_var.set(staff_list[0])
            staff_dropdown = tk.OptionMenu(remove_staff_window, staff_var, *staff_list)
            staff_dropdown.pack()
    
            def remove_selected_staff():
                selected = staff_var.get().split(":")[0]
                delete_query = "DELETE FROM Account WHERE AccountID = %s"
                try:
                    cursor.execute(delete_query, (selected,))
                    db.commit()
                    messagebox.showinfo("Success", f"Staff {selected} has been removed.")
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

    def button_click(role):
        if role == "Manager":
            # Close the previous window
            window.withdraw()

            #get branch id from staff email and password
            cursor = db.cursor()
            cursor.execute("SELECT BranchID FROM Account WHERE Email = %s AND Password = %s", (email_entry.get(), password_entry.get()))
            branch_id = cursor.fetchone()[0]
            cursor.close()

            #get branch info from branch id
            cursor = db.cursor()
            cursor.execute("SELECT City, PostCode FROM Branch WHERE BranchID = %s", (branch_id,))
            branch_info = cursor.fetchone()
            selected_branch_info = branch_info[0] + " - " + branch_info[1]
            cursor.close()
            # Close the previous window (staff roles window)
            manager_options_window = tk.Toplevel(window)
            manager_options_window.title(f"Manager Options - {selected_branch_info}")
            manager_options_window.state('zoomed')
            # manager_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

            def calculate_branch_cost():
                # Get the branch id
                cursor = db.cursor()
                cursor.execute("SELECT BranchID FROM Branch WHERE BranchID = %s", (branch_id,))
                branch_id = cursor.fetchone()[0]

                # Get the total cost of all stock
                cursor.execute("SELECT SUM(AmountInStock * Price) FROM Stock WHERE BranchID = %s", (branch_id,))
                total_stock_cost = cursor.fetchone()[0] or 0

                #today's date
                today = datetime.date.today()

                # current time
                now = datetime.datetime.now()

                # Create window to enter cost details
                cost_window = tk.Toplevel(window)
                cost_window.title("Enter Cost Details")
                cost_window.state('zoomed')
                # cost_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                # Utility Cost entry
                utility_cost_label = tk.Label(cost_window, text="Utility Cost:", font=fontStyle)
                utility_cost_label.pack(pady=(10, 0))
                utility_cost_entry = tk.Entry(cost_window, font=fontStyle)
                utility_cost_entry.pack(pady=(0, 10))

                # Wages entry
                wages_label = tk.Label(cost_window, text="Wages:", font=fontStyle)
                wages_label.pack(pady=(10, 0))
                wages_entry = tk.Entry(cost_window, font=fontStyle)
                wages_entry.pack(pady=(0, 20))

                # Submit function
                def submit_cost_details():
                    try:
                        utility_cost = Decimal(utility_cost_entry.get())
                        wages = Decimal(wages_entry.get())
                        total_cost = total_stock_cost + utility_cost + wages

                        # Generate Cost ID
                        cursor.execute("SELECT CostID FROM Cost ORDER BY CAST(SUBSTRING(CostID, 2) AS UNSIGNED) DESC Limit 1;")
                        last_cost_id_row = cursor.fetchone()
                        last_cost_id = last_cost_id_row[0] if last_cost_id_row and last_cost_id_row[0] else "C0"
                        new_cost_id_number = int(last_cost_id.lstrip("C")) + 1
                        new_cost_id = "C" + str(new_cost_id_number)

                        # Insert the cost details into the database
                        insert_query = "INSERT INTO Cost (CostID, UtilityCost, Wages, StockCost, TotalCost, BranchID, Date, Time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                        cursor.execute(insert_query, (new_cost_id, utility_cost, wages, total_stock_cost, float(total_cost), branch_id, today, now))
                        db.commit()
                        messagebox.showinfo("Success", f"Cost {new_cost_id} successfully added. Total cost: £{total_cost}")
                        cost_window.destroy()
                    except ValueError:
                        messagebox.showerror("Error", "Please enter valid numbers for utility cost and wages.")
                    except Exception as e:
                        db.rollback()
                        messagebox.showerror("Error", f"An error occurred: {str(e)}")

                submit_button = tk.Button(cost_window, text="Submit", command=submit_cost_details, **buttonStyle)
                submit_button.pack()

                back_button = tk.Button(cost_window, text="Back", command=cost_window.destroy, **buttonStyle)
                back_button.pack(pady=10)

            def branch_report():
                manager_options_window.destroy()
                show_reports_window = tk.Toplevel(window)
                show_reports_window.title(f"Branch report - {selected_branch_info}")
                show_reports_window.state('zoomed')
                city, postcode = selected_branch_info.split(", ")

                stock_query = """
                    SELECT StockID, StockType, AmountInStock, Price
                    FROM Stock
                    WHERE BranchID = (
                        SELECT BranchID
                        FROM Branch
                        WHERE BranchID = %s
                    )
                """
                cursor = db.cursor()
                cursor.execute(stock_query, (branch_id,))
                stock_results = cursor.fetchall()

                if stock_results:
                    header_label = tk.Label(show_reports_window, text="Stock for this branch", font=('Helvetica', 14, 'bold'))
                    header_label.pack(pady=10)
                    for stock_id, stock_type, amount_in_stock, price in stock_results:
                        stock_info = f"{stock_id}: {stock_type} - {amount_in_stock} in stock - £{price}"
                        tk.Label(show_reports_window, text=stock_info, font=fontStyle).pack()
                else:
                    header_label = tk.Label(show_reports_window, text="Empty Stock", font=('Helvetica', 14, 'bold'))
                    header_label.pack(pady=10)

                #separator
                ttk.Separator(show_reports_window, orient='horizontal').pack(fill='x', pady=10)

                #heading for the total cost
                header_label = tk.Label(show_reports_window, text="Cost Details", font=('Helvetica', 14, 'bold'))
                header_label.pack(pady=10)
                
                #print cost details for the branch
                cursor = db.cursor()
                cursor.execute("SELECT CostID, UtilityCost, Wages, StockCost, TotalCost, Date, Time FROM Cost WHERE BranchID = (SELECT BranchID FROM Branch WHERE BranchID = %s)", (branch_id,))
                cost_details = cursor.fetchall()

                if cost_details:
                    #show all costs not just the last order the cost by date and time 
                    cost_details.sort(key=lambda x: (x[5], x[6]), reverse=True)
                    for cost_id, utility_cost, wages, stock_cost, total_cost, date, time in cost_details:
                        cost_info = f"{cost_id}: Utility Cost - £{utility_cost}, Wages - £{wages}, Stock Cost - £{stock_cost}, Total Cost - £{total_cost}, Date - {date}, Time - {time}"
                        tk.Label(show_reports_window, text=cost_info, font=fontStyle).pack()
                else:
                    tk.Label(show_reports_window, text="No cost details found.", font=fontStyle).pack()



                back_button = tk.Button(show_reports_window, text="Back", command=show_reports_window.destroy, **buttonStyle)
                back_button.pack(pady=10)

            def staff_report():
                staff_report_window = tk.Toplevel(window)
                staff_report_window.title("Staff report")
                staff_report_window.state('zoomed')
                # staff_report_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
                top_border = tk.Canvas(staff_report_window , height=50, bg='black')
                top_border.pack(side='top', fill='x')    
                main_frame = tk.Frame(staff_report_window)
                main_frame.pack(padx=20, pady=20)
                title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
                title_label.pack(pady=(0, 10))
                center_frame = tk.Frame(staff_report_window)
                center_frame.pack(expand=True)
                center_frame.grid_columnconfigure(0, weight=1)
                logo_image = Image.open("restt.png")  # Replace with your logo path
                logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
                logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
                logo_label.image = logo_photo  # Keep a reference
                logo_label.pack(side='left', padx=10, pady=5)
                #staff report title
                header_label = tk.Label(staff_report_window, text="Managers", font=('Helvetica', 14, 'bold'))
                header_label.pack(pady=10)

                # Extract the BranchID from the selected branch info
                city, postcode = selected_branch_info.split(", ")
                cursor = db.cursor()
                cursor.execute("SELECT BranchID FROM Branch WHERE BranchID = %s", (branch_id,))
                branch_id = cursor.fetchone()[0]
                cursor.close()

                # Fetch all managers for the branch
                cursor = db.cursor()
                cursor.execute("SELECT AccountID, ForeName, SurName FROM Account WHERE BranchID = %s AND Role = 'Manager'", (branch_id,))
                manager_results = cursor.fetchall()
                cursor.close()

                if manager_results:
                    for account_id, forename, surname in manager_results:
                        manager_info = f"{account_id}: {forename} {surname}"
                        tk.Label(staff_report_window, text=manager_info, font=fontStyle).pack()
                else:
                    tk.Label(staff_report_window, text="No managers found for this branch.", font=fontStyle).pack()

                #separator
                ttk.Separator(staff_report_window, orient='horizontal').pack(fill='x', pady=10)

                #Waiting staff report title
                header_label = tk.Label(staff_report_window, text="Waiting Staff", font=('Helvetica', 14, 'bold'))
                header_label.pack(pady=10)

                # Fetch all waiting staff for the branch
                cursor = db.cursor()
                cursor.execute("SELECT AccountID, ForeName, SurName, Points FROM Account WHERE BranchID = %s AND Role = 'Waiting Staff'", (branch_id,))
                waiting_staff_results = cursor.fetchall()
                cursor.close()

                if waiting_staff_results:
                    #sort the staff by points
                    waiting_staff_results.sort(key=lambda x: x[3], reverse=True)
                    for account_id, forename, surname, points in waiting_staff_results:
                        waiting_staff_info = f"{account_id}: {forename} {surname} - {points} points"
                        tk.Label(staff_report_window, text=waiting_staff_info, font=fontStyle).pack()
                else:
                    tk.Label(staff_report_window, text="No waiting staff found for this branch.", font=fontStyle).pack()

                #separator
                ttk.Separator(staff_report_window, orient='horizontal').pack(fill='x', pady=10)

                #Kitchen staff report title
                header_label = tk.Label(staff_report_window, text="Kitchen Staff", font=('Helvetica', 14, 'bold'))
                header_label.pack(pady=10)

                # Fetch all kitchen staff for the branch
                cursor = db.cursor()
                cursor.execute("SELECT AccountID, ForeName, SurName, Points FROM Account WHERE BranchID = %s AND Role = 'Kitchen Staff'", (branch_id,))
                kitchen_staff_results = cursor.fetchall()
                cursor.close()

                #sort the staff by points
                kitchen_staff_results.sort(key=lambda x: x[3], reverse=True)

                if kitchen_staff_results:
                    for account_id, forename, surname, points in kitchen_staff_results:
                        kitchen_staff_info = f"{account_id}: {forename} {surname} - {points} points"
                        tk.Label(staff_report_window, text=kitchen_staff_info, font=fontStyle).pack()
                else:
                    tk.Label(staff_report_window, text="No kitchen staff found for this branch.", font=fontStyle).pack()

                #reset the points of all staff
                def reset_points():
                    cursor = db.cursor()
                    cursor.execute("UPDATE Account SET Points = 0 WHERE BranchID = %s", (branch_id,))
                    db.commit()
                    messagebox.showinfo("Success", f"Points for all staff in {city} - {postcode} reset to 0.")
                    staff_report_window.destroy()
                    manager_Login(email_entry, password_entry)

                #separator
                ttk.Separator(staff_report_window, orient='horizontal').pack(fill='x', pady=10)

                #number of managers heading
                header_label = tk.Label(staff_report_window, text="Number of Staff", font=('Helvetica', 14, 'bold'))
                header_label.pack(pady=10)

                cursor = db.cursor()
                cursor.execute("SELECT AccountID, ForeName, SurName FROM Account WHERE BranchID = %s AND Role = 'Manager'", (branch_id,))
                manager_results = cursor.fetchall()
                cursor.close()

                # Print the number of managers
                number_of_managers = len(manager_results)
                tk.Label(staff_report_window, text=f"Number of Managers: {number_of_managers}", font=fontStyle).pack()

                #number of waiting staff heading
                cursor = db.cursor()
                cursor.execute("SELECT AccountID, ForeName, SurName FROM Account WHERE BranchID = %s AND Role = 'Waiting Staff'", (branch_id,))
                waiting_staff_results = cursor.fetchall()

                # Print the number of waiting staff
                number_of_waiting_staff = len(waiting_staff_results)
                tk.Label(staff_report_window, text=f"Number of Waiting Staff: {number_of_waiting_staff}", font=fontStyle).pack()

                #number of kitchen staff heading
                cursor = db.cursor()
                cursor.execute("SELECT AccountID, ForeName, SurName FROM Account WHERE BranchID = %s AND Role = 'Kitchen Staff'", (branch_id,))
                kitchen_staff_results = cursor.fetchall()

                # Print the number of kitchen staff
                number_of_kitchen_staff = len(kitchen_staff_results)
                tk.Label(staff_report_window, text=f"Number of Kitchen Staff: {number_of_kitchen_staff}", font=fontStyle).pack()

                #total number of staff heading
                total_number_of_staff = number_of_managers + number_of_waiting_staff + number_of_kitchen_staff

                # Print the total number of staff
                tk.Label(staff_report_window, text=f"Total Number of Staff: {total_number_of_staff}", font=fontStyle).pack()

                reset_points_button = tk.Button(staff_report_window, text="Reset Points", command=reset_points, **buttonStyle)
                reset_points_button.pack(pady=10)


                back_button = tk.Button(staff_report_window, text="Back", command=staff_report_window.destroy, **buttonStyle)
                back_button.pack(pady=10)

            def show_reports():
                manager_options_window.destroy()

                stock_options_window = tk.Toplevel(window)
                stock_options_window.title(f"Reports - {selected_branch_info}")
                stock_options_window.state('zoomed')
                top_border = tk.Canvas(stock_options_window , height=50, bg='black')
                top_border.pack(side='top', fill='x')    
                main_frame = tk.Frame(stock_options_window)
                main_frame.pack(padx=20, pady=20)
                title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
                title_label.pack(pady=(0, 10))
                center_frame = tk.Frame(stock_options_window)
                center_frame.pack(expand=True)
                center_frame.grid_columnconfigure(0, weight=1)
                logo_image = Image.open("restt.png")  # Replace with your logo path
                logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
                logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
                logo_label.image = logo_photo  # Keep a reference
                logo_label.pack(side='left', padx=10, pady=5)
                stock_center_frame = tk.Frame(stock_options_window)
                stock_center_frame.pack(expand=True)

                staff_report_button = tk.Button(stock_center_frame, text="Staff report", command= lambda: staff_report(),  font=('Helvetica', 12, 'bold'), height=2, width=15)
                branch_report_button = tk.Button(stock_center_frame, text="Branch report", command=lambda: branch_report(), font=('Helvetica', 12, 'bold'), height=2, width=15)

                staff_report_button.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
                branch_report_button.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

                stock_center_frame.grid_rowconfigure(0, weight=1)
                stock_center_frame.grid_columnconfigure(0, weight=1)
                stock_center_frame.grid_columnconfigure(1, weight=1)

                back_button = tk.Button(stock_options_window, text="Back", command=stock_options_window.destroy, **buttonStyle)
                back_button.pack(pady=10)
    
            def stock_options():
                
                stock_options_window = tk.Toplevel(window)
                stock_options_window.title(f"Stock Options - {selected_branch_info}")
                stock_options_window.state('zoomed')
                top_border = tk.Canvas(stock_options_window , height=50, bg='black')
                top_border.pack(side='top', fill='x')    
                main_frame = tk.Frame(stock_options_window)
                main_frame.pack(padx=20, pady=20)
                title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
                title_label.pack(pady=(0, 10))
                center_frame = tk.Frame(stock_options_window)
                center_frame.pack(expand=True)
                center_frame.grid_columnconfigure(0, weight=1)
                logo_image = Image.open("restt.png")  # Replace with your logo path
                logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
                logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
                logo_label.image = logo_photo  # Keep a reference
                logo_label.pack(side='left', padx=10, pady=5)
                stock_center_frame = tk.Frame(stock_options_window)
                stock_center_frame.pack(expand=True)
                # stock_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                # Define functionalities for each button 
                view_stock_button = tk.Button(stock_center_frame, text="View Stock", command=lambda: view_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
                add_stock_button = tk.Button(stock_center_frame, text="Add Stock", command=lambda: add_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
                remove_stock_button = tk.Button(stock_center_frame, text="Remove Stock", command=lambda: remove_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
                
                # Pack buttons in the center frame
                view_stock_button.grid(row=0, column=0, padx=10, pady=10)
                add_stock_button.grid(row=0, column=1, padx=10, pady=10)
                remove_stock_button.grid(row=0, column=2, padx=10, pady=10)

                # Back button to go back to the previous window
                back_button = tk.Button(stock_options_window, text="Back", command=stock_options_window.destroy, **buttonStyle)
                back_button.pack(pady=10)

            def view_stock(selected_branch_info):
                view_stock_window = tk.Toplevel(window)
                view_stock_window.title("View Stock")
                view_stock_window.state('zoomed')
                # view_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
                top_border = tk.Canvas( view_stock_window, height=50, bg='black')
                top_border.pack(side='top', fill='x')    
                main_frame = tk.Frame( view_stock_window)
                main_frame.pack(padx=20, pady=20)
                title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
                title_label.pack(pady=(0, 10))
                center_frame = tk.Frame( view_stock_window)
                center_frame.pack(expand=True)
                center_frame.grid_columnconfigure(0, weight=1)
                logo_image = Image.open("restt.png")  # Replace with your logo path
                logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
                logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
                logo_label.image = logo_photo  # Keep a reference
                logo_label.pack(side='left', padx=10, pady=5)
                # Fetch all stock for the branch
                cursor = db.cursor()
                cursor.execute("SELECT StockID, StockType, AmountInStock, Price FROM Stock WHERE BranchID = %s", (branch_id,))
                stock_results = cursor.fetchall()

                # Print all the stock in the window
                if stock_results:
                    for stock_id, stock_type, amount_in_stock, price in stock_results:
                        stock_info = f"{stock_id}: {stock_type} - Amount: {amount_in_stock} - Price: £{price}"
                        tk.Label(view_stock_window, text=stock_info, font=fontStyle).pack()

                else:
                    tk.Label(view_stock_window, text="No stock found for this branch.", font=fontStyle).pack()

                back_button = tk.Button(view_stock_window, text="Back", command=view_stock_window.destroy, **buttonStyle)
                back_button.pack(pady=10)

            def add_stock(selected_branch_info):
                add_stock_window = tk.Toplevel(window)
                add_stock_window.title("Add Stock")
                add_stock_window.state('zoomed')
                # add_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
                top_border = tk.Canvas(add_stock_window, height=50, bg='black')
                top_border.pack(side='top', fill='x')    
                main_frame = tk.Frame( add_stock_window)
                main_frame.pack(padx=20, pady=20)
                title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
                title_label.pack(pady=(0, 10))
                center_frame = tk.Frame(add_stock_window)
                center_frame.pack(expand=True)
                center_frame.grid_columnconfigure(0, weight=1)
                logo_image = Image.open("restt.png")  # Replace with your logo path
                logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
                logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
                logo_label.image = logo_photo  # Keep a reference
                logo_label.pack(side='left', padx=10, pady=5)
                # Entry fields for stock details
                stock_type_label = tk.Label(add_stock_window, text="Stock Type:", font=fontStyle)
                stock_type_label.pack()
                stock_type_entry = tk.Entry(add_stock_window, font=fontStyle)
                stock_type_entry.pack()

                amount_in_stock_label = tk.Label(add_stock_window, text="Amount in Stock:", font=fontStyle)
                amount_in_stock_label.pack()
                amount_in_stock_entry = tk.Entry(add_stock_window, font=fontStyle)
                amount_in_stock_entry.pack()

                price_label = tk.Label(add_stock_window, text="Price:", font=fontStyle)
                price_label.pack()
                price_entry = tk.Entry(add_stock_window, font=fontStyle)
                price_entry.pack()

                # Submit function
                def submit_stock_details():
                    stock_type = stock_type_entry.get()
                    amount_in_stock = amount_in_stock_entry.get()
                    price = price_entry.get()

                    # Generate Stock ID based on the last StockID
                    cursor = db.cursor()
                    cursor.execute("SELECT MAX(StockID) FROM Stock")
                    last_stock_id_row = cursor.fetchone()
                    last_stock_id = last_stock_id_row[0] if last_stock_id_row and last_stock_id_row[0] else "S0"
                    new_stock_id_number = int(last_stock_id.lstrip("S")) + 1
                    new_stock_id = "S" + str(new_stock_id_number)

                    # Insert into database (adjust according to your schema)
                    insert_query = """
                        INSERT INTO Stock (StockID, StockType, AmountInStock, Price, BranchID)
                        SELECT %s, %s, %s, %s, Branch.BranchID
                        FROM Branch
                        WHERE BranchID = (%s)
                    """
                    try:
                        cursor.execute(insert_query, (new_stock_id, stock_type, amount_in_stock, price, branch_id))
                        db.commit()
                        messagebox.showinfo("Success", f"Stock {new_stock_id} successfully added.")
                    except Exception as e:
                        messagebox.showerror("Error", f"An error occurred: {e}")
                    finally:
                        add_stock_window.destroy()
                        stock_options(selected_branch_info)

                submit_button = tk.Button(add_stock_window, text="Submit", command=submit_stock_details, **buttonStyle)
                submit_button.pack()

                back_button = tk.Button(add_stock_window, text="Back", command=add_stock_window.destroy, **buttonStyle)
                back_button.pack(pady=10)

                #separator
                ttk.Separator(add_stock_window, orient='horizontal').pack(fill='x', pady=10)

                #dropdown list of all available stock
                def get_available_stock(branch_id):
                    cursor = db.cursor()
                    cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s", (branch_id,))
                    return cursor.fetchall()
                
                available_stock = get_available_stock(branch_id)

                stock_var = tk.StringVar(add_stock_window)
                stock_var.set("Select stock")
                stock_dropdown_label = tk.Label(add_stock_window, text="Select Stock:", font=fontStyle)
                stock_dropdown_label.pack()
                stock_dropdown = tk.OptionMenu(add_stock_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
                stock_dropdown.pack()

                # add ammoount to stock text box
                amount_to_add_label = tk.Label(add_stock_window, text="Amount to Add:", font=fontStyle)
                amount_to_add_label.pack()
                amount_to_add_entry = tk.Entry(add_stock_window, font=fontStyle)
                amount_to_add_entry.pack()

                #function to add stock
                def add_stock():
                    selected_stock_id = stock_var.get().split(" - ")[0]
                    amount_to_add = amount_to_add_entry.get()

                    if selected_stock_id.startswith("Select"):
                        messagebox.showerror("Error", "You must select a valid stock.")
                        return

                    cursor = db.cursor()
                    try:
                        #update the stock amount
                        update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock + %s WHERE StockID = %s"
                        cursor.execute(update_stock_query, (amount_to_add, selected_stock_id))
                        db.commit()
                        messagebox.showinfo("Success", f"{amount_to_add} of stock {selected_stock_id} successfully added.")
                    except Exception as e:
                        messagebox.showerror("Error", f"An error occurred: {e}")
                    finally:
                        add_stock_window.destroy()
                        stock_options(selected_branch_info)

                add_button = tk.Button(add_stock_window, text="Add Stock", command=add_stock, **buttonStyle)
                add_button.pack()

                #back button to go back to the previous window
                back_button = tk.Button(add_stock_window, text="Back", command=add_stock_window.destroy, **buttonStyle)
                back_button.pack(pady=10)

            def remove_stock(selected_branch_info):
                #get branch id from staff email and password
                cursor = db.cursor()
                cursor.execute("SELECT BranchID FROM Account WHERE Email = %s AND Password = %s", (email_entry.get(), password_entry.get()))
                branch_id = cursor.fetchone()[0]
                cursor.close()

                #get branch info from branch id
                cursor = db.cursor()
                cursor.execute("SELECT City, PostCode FROM Branch WHERE BranchID = %s", (branch_id,))
                selected_branch_info = cursor.fetchone()
                cursor.close()

                remove_stock_window = tk.Toplevel(window)
                remove_stock_window.title("Remove Stock")
                remove_stock_window.state('zoomed')
                # remove_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                # Fetch stock details from the database
                stock_query = """
                    SELECT StockID, StockType
                    FROM Stock
                    WHERE BranchID = (select BranchID from Branch where City = %s and PostCode = %s)
                """
                cursor = db.cursor()
                cursor.execute(stock_query, (selected_branch_info[0], selected_branch_info[1]))
                stock_results = cursor.fetchall()

                # Create a list of stock for the dropdown
                stock_list = [f"{row[0]}: {row[1]}" for row in stock_results] if stock_results else []

                if stock_list:
                    stock_var = tk.StringVar(remove_stock_window)
                    stock_var.set(stock_list[0])
                    stock_dropdown = tk.OptionMenu(remove_stock_window, stock_var, *stock_list)
                    stock_dropdown.pack()
            
                    def remove_selected_stock():
                        selected = stock_var.get().split(":")[0]
                        delete_query = "DELETE FROM Stock WHERE StockID = %s"
                        try:
                            cursor.execute(delete_query, (selected,))
                            db.commit()
                            messagebox.showinfo("Success", f"Stock {selected} has been removed.")
                            remove_stock_window.destroy()
                        except Exception as e:
                            messagebox.showerror("Error", f"An error occurred: {e}")
                    
                    remove_button = tk.Button(remove_stock_window, text="Remove Stock", command=remove_selected_stock, **buttonStyle)
                    remove_button.pack()
                    back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

                    #separator
                    ttk.Separator(remove_stock_window, orient='horizontal').pack(fill='x', pady=10)

                    #dropdown list of all available stock
                    def get_available_stock(branch_id):
                        cursor = db.cursor()
                        cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s", (branch_id,))
                        return cursor.fetchall()
                    
                    available_stock = get_available_stock(branch_id)

                    stock_var = tk.StringVar(remove_stock_window)
                    stock_var.set("Select stock")
                    stock_dropdown_label = tk.Label(remove_stock_window, text="Select Stock:", font=fontStyle)
                    stock_dropdown_label.pack()
                    stock_dropdown = tk.OptionMenu(remove_stock_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
                    stock_dropdown.pack()

                    # add ammoount to stock text box
                    amount_to_remove_label = tk.Label(remove_stock_window, text="Amount to Remove:", font=fontStyle)
                    amount_to_remove_label.pack()
                    amount_to_remove_entry = tk.Entry(remove_stock_window, font=fontStyle)
                    amount_to_remove_entry.pack()

                    #function to add stock
                    def remove_stock():
                        selected_stock_id = stock_var.get().split(" - ")[0]
                        amount_to_remove = amount_to_remove_entry.get()

                        if selected_stock_id.startswith("Select"):
                            messagebox.showerror("Error", "You must select a valid stock.")

                        cursor = db.cursor()
                        try:
                            #update the stock amount
                            update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock - %s WHERE StockID = %s"
                            cursor.execute(update_stock_query, (amount_to_remove, selected_stock_id))
                            db.commit()
                            messagebox.showinfo("Success", f"{amount_to_remove} of stock {selected_stock_id} successfully removed.")
                        except Exception as e:
                            messagebox.showerror("Error", f"An error occurred: {e}")
                        finally:
                            remove_stock_window.destroy()
                            stock_options(selected_branch_info)

                    remove_button = tk.Button(remove_stock_window, text="Remove Stock", command=remove_stock, **buttonStyle)
                    remove_button.pack()

                    #back button to go back to the previous window
                    back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

                else:
                    tk.Label(remove_stock_window, text="No stock found to remove.", font=fontStyle).pack()
                    back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

                    #separator
                    ttk.Separator(remove_stock_window, orient='horizontal').pack(fill='x', pady=10)

                    #dropdown list of all available stock
                    def get_available_stock(branch_id):
                        cursor = db.cursor()
                        cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s", (branch_id,))
                        return cursor.fetchall()
                    
                    available_stock = get_available_stock(branch_id)

                    stock_var = tk.StringVar(remove_stock_window)
                    stock_var.set("Select stock")
                    stock_dropdown_label = tk.Label(remove_stock_window, text="Select Stock:", font=fontStyle)
                    stock_dropdown_label.pack()
                    stock_dropdown = tk.OptionMenu(remove_stock_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
                    stock_dropdown.pack()

                    # add ammoount to stock text box
                    amount_to_remove_label = tk.Label(remove_stock_window, text="Amount to Remove:", font=fontStyle)
                    amount_to_remove_label.pack()
                    amount_to_remove_entry = tk.Entry(remove_stock_window, font=fontStyle)
                    amount_to_remove_entry.pack()

                    #function to add stock
                    def remove_stock():
                        selected_stock_id = stock_var.get().split(" - ")[0]
                        amount_to_remove = amount_to_remove_entry.get()

                        if selected_stock_id.startswith("Select"):
                            messagebox.showerror("Error", "You must select a valid stock.")

                        cursor = db.cursor()
                        try:
                            #update the stock amount
                            update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock - %s WHERE StockID = %s"
                            cursor.execute(update_stock_query, (amount_to_remove, selected_stock_id))
                            db.commit()
                            messagebox.showinfo("Success", f"{amount_to_remove} of stock {selected_stock_id} successfully removed.")
                        except Exception as e:
                            messagebox.showerror("Error", f"An error occurred: {e}")
                        finally:
                            remove_stock_window.destroy()
                            stock_options(selected_branch_info)

                    remove_button = tk.Button(remove_stock_window, text="Remove Stock", command=remove_stock, **buttonStyle)
                    remove_button.pack()

                    #back button to go back to the previous window
                    back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

            # Center frame for holding the buttons
            center_frame = tk.Frame(manager_options_window)
            center_frame.pack(expand=True)

            # Create buttons with the same style as in open_staff_roles_window
            
            stock_options_button = tk.Button(center_frame, text="Stock", command=stock_options, font=('Helvetica', 12, 'bold'), height=2, width=15)
            show_reports_button = tk.Button(center_frame, text="Show reports", command=show_reports, font=('Helvetica', 12, 'bold'), height=2, width=15)

            # Pack buttons in the center frame

            stock_options_button.grid(row=0, column=3, padx=10, pady=10)
            show_reports_button.grid(row=0, column=4, padx=10, pady=10)

            back_button = tk.Button(manager_options_window, text="Back", command=lambda: [manager_options_window.destroy()], **buttonStyle)
            back_button.pack(side=tk.BOTTOM, pady=10)

        elif role == "Waiting Staff":
                # Close the previous window
            window.withdraw()

            #get branch id from staff email and password
            cursor = db.cursor()
            cursor.execute("SELECT BranchID FROM Account WHERE Email = %s AND Password = %s", (email_entry.get(), password_entry.get()))
            branch_id = cursor.fetchone()[0]
            cursor.close()

            #get branch info from branch id
            cursor = db.cursor()
            cursor.execute("SELECT City, PostCode FROM Branch WHERE BranchID = %s", (branch_id,))
            branch_info = cursor.fetchone()
            selected_branch_info = branch_info[0] + " - " + branch_info[1]
            cursor.close()

            waiting_staff_window = tk.Toplevel(window)
            waiting_staff_window.title(f"Waiting Staff Options - {selected_branch_info}")
            waiting_staff_window.state('zoomed')
            # waiting_staff_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

            # Center frame for holding the buttons
            center_frame = tk.Frame(waiting_staff_window)
            center_frame.pack(expand=True)

            # Define functionalities for each button (placeholder functions)
            def order():
                order_window = tk.Toplevel(window)
                order_window.title("Order")
                order_window.state('zoomed')
                # take_order_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                def take_order(selected_branch_info):
                    # Create a new window for taking an order
                    take_order_window = tk.Toplevel(window)
                    take_order_window.title("Take Order")
                    take_order_window.state('zoomed')
                    # take_order_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
                    top_border = tk.Canvas(take_order_window, height=50, bg='black')
                    top_border.pack(side='top', fill='x')    
                    main_frame = tk.Frame( take_order_window)
                    main_frame.pack(padx=20, pady=20)
                    title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
                    title_label.pack(pady=(0, 10))
                    center_frame = tk.Frame(take_order_window)
                    center_frame.pack(expand=True)
                    center_frame.grid_columnconfigure(0, weight=1)
                    logo_image = Image.open("restt.png")  # Replace with your logo path
                    logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
                    logo_photo = ImageTk.PhotoImage(logo_image)
                    logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
                    logo_label.image = logo_photo  # Keep a reference
                    logo_label.pack(side='left', padx=10, pady=5)
                    # Function to fetch available stock
                    def get_available_stock(branch_id):
                        cursor = db.cursor()
                        cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s AND AmountInStock > 0", (branch_id,))
                        available_stock = cursor.fetchall()
                        cursor.close()
                        return available_stock

                    # Function to fetch available tables
                    def get_available_tables(branch_id):
                        cursor = db.cursor()
                        cursor.execute("SELECT TableID FROM Tables WHERE BranchID = %s", (branch_id,))
                        available_tables = cursor.fetchall()
                        cursor.close()
                        return available_tables

                    # Fetch available stock and tables for the branch
                    available_stock = get_available_stock(branch_id)
                    available_tables = get_available_tables(branch_id)


                    # Dropdown for selecting stock
                    stock_var = tk.StringVar(take_order_window)
                    stock_var.set("Select stock")
                    stock_dropdown_label = tk.Label(take_order_window, text="Select Stock:", font=fontStyle)
                    stock_dropdown_label.pack()
                    stock_dropdown = tk.OptionMenu(take_order_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
                    stock_dropdown.pack()

                    # Dropdown for selecting a table
                    table_var = tk.StringVar(take_order_window)
                    table_var.set("Select table")
                    table_dropdown_label = tk.Label(take_order_window, text="Select Table:", font=fontStyle)
                    table_dropdown_label.pack()
                    table_dropdown = tk.OptionMenu(take_order_window, table_var, *[table[0] for table in available_tables])
                    table_dropdown.pack()

                    # Function to create a new order entry
                    def submit_order_details():
                        selected_stock_id = stock_var.get().split(" - ")[0]
                        selected_table_id = table_var.get()

                        if selected_stock_id.startswith("Select") or selected_table_id.startswith("Select"):
                            messagebox.showerror("Error", "You must select a valid stock and table.")
                            return

                        cursor = db.cursor()
                        try:
                            # Generate a new unique TrackID
                            cursor.execute("SELECT TrackID FROM orderr ORDER BY CAST(SUBSTRING(TrackID, 2) AS UNSIGNED) DESC LIMIT 1;")
                            last_track_id = cursor.fetchone()[0]
                            last_track_id_number = int(last_track_id[1:]) if last_track_id else 0
                            new_track_id = f"T{last_track_id_number + 1}"

                            # Insert the new order
                            insert_query = "INSERT INTO Orderr (TrackID, StockID, TableID) VALUES (%s, %s, %s)"
                            cursor.execute(insert_query, (new_track_id, selected_stock_id, selected_table_id))

                            # Update stock amount
                            update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock - 1 WHERE StockID = %s"
                            cursor.execute(update_stock_query, (selected_stock_id,))

                            # Set the table as unavailable
                            update_table_query = "UPDATE Tables SET Availability = 0 WHERE TableID = %s"
                            cursor.execute(update_table_query, (selected_table_id,))

                            # Commit the transaction
                            db.commit()
                            messagebox.showinfo("Success", f"Order with tracking ID {new_track_id} successfully taken for table {selected_table_id}.")
                            
                        except Exception as e:
                            db.rollback()
                            messagebox.showerror("Error", f"An error occurred: {e}")
                        finally:
                            cursor.close()
                            
                    def remove_order(branch_id):
                        remove_order_window = tk.Toplevel(window)
                        remove_order_window.title("Remove Order")
                        remove_order_window.state('zoomed')
                        # remove_order_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                        # Fetch all orders with their corresponding StockType for the branch
                        cursor = db.cursor()
                        cursor.execute("""
                            SELECT o.TrackID, s.StockType, o.TableID 
                            FROM Orderr o 
                            INNER JOIN Stock s ON o.StockID = s.StockID 
                            WHERE o.TableID IN (
                                SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 0
                            )
                        """, (branch_id,))
                        order_results = cursor.fetchall()
                        cursor.close()

                        # Create a list of orders for the dropdown, showing StockType instead of StockID
                        order_list = [f"{row[0]}: {row[1]} - Table ID: {row[2]}"
                                    for row in order_results] if order_results else []

                        if order_list:
                            order_var = tk.StringVar(remove_order_window)
                            order_var.set(order_list[0])  # Set default value
                            order_dropdown = tk.OptionMenu(remove_order_window, order_var, *order_list)
                            order_dropdown.pack()
                            
                            def remove_selected_order():
                                selected_track_id = order_var.get().split(":")[0]
                                cursor = db.cursor()
                                try:
                                    # Start transaction
                                    cursor.execute("START TRANSACTION")
                                    
                                    # Delete the order
                                    delete_query = "DELETE FROM Orderr WHERE TrackID = %s"
                                    cursor.execute(delete_query, (selected_track_id,))

                                    # Update the availability of the table
                                    # Ensure to retrieve and update the correct TableID from the Order
                                    update_table_query = """
                                    UPDATE Tables SET Availability = 1 
                                    WHERE TableID = (
                                        SELECT TableID FROM Orderr WHERE TrackID = %s
                                    )
                                    """
                                    cursor.execute(update_table_query, (selected_track_id,))

                                    # Commit the changes
                                    db.commit()
                                    messagebox.showinfo("Success", f"Order {selected_track_id} has been cancelled")
                                    
                                    remove_order_window.destroy()
                                except Exception as e:
                                    db.rollback()
                                    messagebox.showerror("Error", f"An error occurred: {e}")
                                finally:
                                    cursor.close()

                            remove_button = tk.Button(remove_order_window, text="Remove Order", command=remove_selected_order, **buttonStyle)
                            remove_button.pack()
                            back_button = tk.Button(remove_order_window, text="Back", command=remove_order_window.destroy, **buttonStyle)
                            back_button.pack(pady=10)
                        else:
                            tk.Label(remove_order_window, text="No orders found for this branch.", font=fontStyle).pack()
                            back_button = tk.Button(remove_order_window, text="Back", command=remove_order_window.destroy, **buttonStyle)
                            back_button.pack(pady=10)

                    # Button to submit the order details
                    submit_button = tk.Button(take_order_window, text="Submit Order", command=submit_order_details, **buttonStyle)
                    submit_button.pack()

                    # Button to go back to the previous window
                    back_button = tk.Button(take_order_window, text="Back", command=take_order_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

                    # Add a button for removing an order in the take_order_window
                    remove_order_button = tk.Button(take_order_window, text="Remove Order", command=lambda: remove_order(branch_id), **buttonStyle)
                    remove_order_button.pack()

                def view_orders(selected_branch_info):
                    view_orders_window = tk.Toplevel(window)
                    view_orders_window.title("View Orders")
                    view_orders_window.state('zoomed')
                    # view_orders_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
                    top_border = tk.Canvas(view_orders_window, height=50, bg='black')
                    top_border.pack(side='top', fill='x')    
                    main_frame = tk.Frame( view_orders_window)
                    main_frame.pack(padx=20, pady=20)
                    title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
                    title_label.pack(pady=(0, 10))
                    center_frame = tk.Frame(view_orders_window)
                    center_frame.pack(expand=True)
                    center_frame.grid_columnconfigure(0, weight=1)
                    logo_image = Image.open("restt.png")  # Replace with your logo path
                    logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
                    logo_photo = ImageTk.PhotoImage(logo_image)
                    logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
                    logo_label.image = logo_photo  # Keep a reference
                    logo_label.pack(side='left', padx=10, pady=5)
                    # Fetch all orders with their corresponding StockType for the branch
                    cursor = db.cursor()
                    cursor.execute("""SELECT o.TrackID, s.StockType, o.TableID
                                        FROM Orderr o
                                        INNER JOIN Stock s ON o.StockID = s.StockID
                                        WHERE o.TableID IN (
                                            SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 0
                                        )""", (branch_id,))
                    
                    order_results = cursor.fetchall()
                    cursor.close()

                    # print all the orders in the window

                    if order_results:
                        for track_id, stock_type, table_id in order_results:
                            order_info = f"{track_id}: {stock_type} - Table ID: {table_id}"
                            tk.Label(view_orders_window, text=order_info, font=fontStyle).pack()
                    else:
                        tk.Label(view_orders_window, text="No orders found for this branch.", font=fontStyle).pack()

                    back_button = tk.Button(view_orders_window, text="Back", command=view_orders_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

                def print_receipt(selected_branch_info):
                    print_receipt_window = tk.Toplevel(window)
                    print_receipt_window.title("Print Receipt")
                    print_receipt_window.state('zoomed')
                    # print_receipt_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                    #dropdown for selecting the table
                    def get_available_tables(branch_id):
                        cursor = db.cursor()
                        cursor.execute("SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 0", (branch_id,))
                        return cursor.fetchall()
                    
                    available_tables = get_available_tables(branch_id)

                    #if there are no available tables, then the dropdown will show "No tables available"
                    if not available_tables:
                        available_tables = ["No tables available"]
                        table_var = tk.StringVar(print_receipt_window)
                        table_var.set(available_tables[0])
                        table_dropdown_label = tk.Label(print_receipt_window, text="Select Table:", font=fontStyle)
                        table_dropdown_label.pack()
                        table_dropdown = tk.OptionMenu(print_receipt_window, table_var, *[table for table in available_tables])
                        table_dropdown.pack()
                    else:
                        table_var = tk.StringVar(print_receipt_window)
                        table_var.set(available_tables[0][0] if available_tables else "No tables available")
                        table_dropdown_label = tk.Label(print_receipt_window, text="Select Table:", font=fontStyle)
                        table_dropdown_label.pack()
                        table_dropdown = tk.OptionMenu(print_receipt_window, table_var, *[table[0] for table in available_tables])
                        table_dropdown.pack()


                    #generate receipt
                    def generate_receipt():
                        selected_table = table_var.get()
                        if selected_table == "No tables available":
                            messagebox.showerror("Error", "No available tables to print receipt for.")
                            return

                        #fetch all the orders for the selected table
                        cursor = db.cursor()
                        cursor.execute("""
                            SELECT o.TrackID, s.StockType, o.TableID, s.Price
                            FROM Orderr o
                            INNER JOIN Stock s ON o.StockID = s.StockID
                            WHERE o.TableID = %s
                        """, (selected_table,))
                        order_results = cursor.fetchall()
                        cursor.close()

                        if order_results:
                            #calculate total price
                            total_price = sum([order[3] for order in order_results])
                            receipt = f"Table ID: {selected_table}\n"
                            receipt += f"{'-' * 20}\n"
                            for track_id, stock_type, table_id, price in order_results:
                                receipt += f"{track_id}: {stock_type} - £{price}\n"
                            receipt += f"{'-' * 20}\n"
                            receipt += f"Total: £{total_price}"
                            tk.Label(print_receipt_window, text=receipt, font=fontStyle).pack()

                            #update the table availability
                            cursor = db.cursor()
                            cursor.execute("UPDATE Tables SET Availability = 1 WHERE TableID = %s", (selected_table,))
                            cursor.close()

                            #delete the orders
                            cursor = db.cursor()
                            cursor.execute("DELETE FROM Orderr WHERE TableID = %s", (selected_table,))
                            cursor.close()

                            #update the receipt table
                            cursor = db.cursor()
                            cursor.execute("SELECT ReceiptID FROM receipt ORDER BY CAST(SUBSTRING(ReceiptID, 2) AS UNSIGNED) DESC Limit 1;")
                            last_receipt_id = cursor.fetchone()[0]
                            last_receipt_id_number = int(last_receipt_id[1:]) if last_receipt_id else 0
                            new_receipt_id = f"R{last_receipt_id_number + 1}"
                            cursor.execute("INSERT INTO Receipt (ReceiptID, TableID, Price, BranchID) VALUES (%s, %s, %s, %s)", (new_receipt_id, selected_table, total_price, branch_id))
                            cursor.close()

                            #commit the changes
                            db.commit()

                            #back button to go back to the previous window
                            back_button = tk.Button(print_receipt_window, text="Back", command=print_receipt_window.destroy, **buttonStyle)
                            back_button.pack(pady=10)

                        else:
                            tk.Label(print_receipt_window, text="No orders found for this table.", font=fontStyle).pack()

                    #button to generate receipt
                    generate_receipt_button = tk.Button(print_receipt_window, text="Generate Receipt", command=generate_receipt, **buttonStyle)
                    generate_receipt_button.pack()

                    #back button to go back to the previous window
                    back_button = tk.Button(print_receipt_window, text="Back", command=print_receipt_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

                # 3 buttons for taking order, viewing orders, and print recipt
                take_order_button = tk.Button(order_window, text="Take Order", command=lambda: [order_window.destroy(), take_order(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)
                view_orders_button = tk.Button(order_window, text="View Orders", command=lambda: [order_window.destroy(), view_orders(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)
                print_receipt_button = tk.Button(order_window, text="Print Receipt", command=lambda: [order_window.destroy(), print_receipt(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)

                # Pack buttons in the center frame
                take_order_button.pack(pady=10)
                view_orders_button.pack(pady=10)
                print_receipt_button.pack(pady=10)

                #back button to go back to the previous window
                back_button = tk.Button(order_window, text="Back", command=lambda: [order_window.destroy()], **buttonStyle)
                back_button.pack(pady=10)

            def reservation():
                reservation_window = tk.Toplevel(window)
                reservation_window.title("Reservation")
                reservation_window.state('zoomed')
                # reservation_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
                top_border = tk.Canvas(reservation_window, height=50, bg='black')
                top_border.pack(side='top', fill='x')    
                main_frame = tk.Frame(reservation_window)
                main_frame.pack(padx=20, pady=20)
                title_label = tk.Label(main_frame, text="Horizon Restaurants", font=("Helvetica", 20, "bold"))
                title_label.pack(pady=(0, 10))
                center_frame = tk.Frame(reservation_window)
                center_frame.pack(expand=True)
                center_frame.grid_columnconfigure(0, weight=1)
                logo_image = Image.open("restt.png")  # Replace with your logo path
                logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
                logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
                logo_label.image = logo_photo  # Keep a reference
                logo_label.pack(side='left', padx=10, pady=5)
                def take_reservation(selected_branch_info):
                    # Create a new window for taking reservation
                    take_reservation_window = tk.Toplevel(window)
                    take_reservation_window.title("Take Reservation")
                    take_reservation_window.state('zoomed')
                    # take_reservation_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                    # Entry fields for reservation details
                    customer_name_label = tk.Label(take_reservation_window, text="Customer Name:", font=fontStyle)
                    customer_name_label.pack()
                    customer_name_entry = tk.Entry(take_reservation_window, font=fontStyle)
                    customer_name_entry.pack()

                    #customer phone number entry
                    customer_phone_label = tk.Label(take_reservation_window, text="Customer Phone Number:", font=fontStyle)
                    customer_phone_label.pack()
                    customer_phone_entry = tk.Entry(take_reservation_window, font=fontStyle)
                    customer_phone_entry.pack()

                    #date entry
                    date_label = tk.Label(take_reservation_window, text="Date (YYYY-MM-DD):", font=fontStyle)
                    date_label.pack()
                    date_entry = tk.Entry(take_reservation_window, font=fontStyle)
                    date_entry.pack()

                    #time entry
                    time_label = tk.Label(take_reservation_window, text="Time (HH:MM):", font=fontStyle)
                    time_label.pack()
                    time_entry = tk.Entry(take_reservation_window, font=fontStyle)
                    time_entry.pack()

                    # Function to fetch available tables
                    def get_available_tables(branch_id):
                        cursor = db.cursor()
                        cursor.execute("SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 1", (branch_id,))
                        return cursor.fetchall()

                    # Function to update table availability
                    def update_table_availability(table_id, availability):
                        cursor = db.cursor()
                        cursor.execute("UPDATE Tables SET Availability = %s WHERE TableID = %s", (availability, table_id))
                        cursor.close()

                    # Dropdown for selecting a table
                    available_tables = get_available_tables(branch_id)
                    table_var = tk.StringVar(take_reservation_window)
                    table_var.set(available_tables[0][0] if available_tables else "No tables available")
                    table_dropdown_label = tk.Label(take_reservation_window, text="Available Tables:", font=fontStyle)
                    table_dropdown_label.pack()
                    table_dropdown = tk.OptionMenu(take_reservation_window, table_var, *[table[0] for table in available_tables])
                    table_dropdown.pack()

                    # Function to create a new reservation
                    def submit_reservation_details():
                        customer_name = customer_name_entry.get()
                        customer_phone = customer_phone_entry.get()
                        date = date_entry.get()
                        time = time_entry.get()
                        selected_table = table_var.get()

                        if selected_table == "No tables available":
                            messagebox.showerror("Error", "No available tables to reserve.")
                            return

                        # Start transaction
                        cursor = db.cursor()
                        cursor.execute("START TRANSACTION")
                        try:
                            # Create a new reservation ID
                            cursor.execute("SELECT MAX(ReservationID) FROM Reservation")
                            last_id = cursor.fetchone()[0]
                            last_id_number = int(last_id[1:]) if last_id else 0
                            new_reservation_id = f"R{last_id_number + 1}"

                            # Insert the new reservation
                            insert_query = """
                                INSERT INTO Reservation (ReservationID, CustomerName, CustomerPhoneNO, Date, Time, BranchID, TableID)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(insert_query, (new_reservation_id, customer_name, customer_phone, date, time, branch_id, selected_table))

                            # Update table availability
                            update_table_availability(selected_table, 0)

                            # Commit the transaction
                            db.commit()
                            messagebox.showinfo("Success", f"Reservation {new_reservation_id} successfully added and table {selected_table} is now reserved.")
                            take_reservation_window.destroy()
                        except Exception as e:
                            db.rollback()
                            messagebox.showerror("Error", f"An error occurred: {e}")
                        finally:
                            cursor.close()

                    # Button to submit the reservation details
                    submit_button = tk.Button(take_reservation_window, text="Submit Reservation", command=submit_reservation_details, **buttonStyle)
                    submit_button.pack()

                    # Button to go back to the previous window
                    back_button = tk.Button(take_reservation_window, text="Back", command=take_reservation_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

                def view_reservations():
                    # Create a new window for viewing reservation
                    view_reservation_window = tk.Toplevel(window)
                    view_reservation_window.title("View Reservation")
                    view_reservation_window.state('zoomed')
                    # view_reservation_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                    #fetch reservation details from the database
                    reservation_query = """
                        SELECT ReservationID, CustomerName, CustomerPhoneNO, Date, Time, TableID
                        FROM Reservation
                        WHERE BranchID = %s
                    """
                    cursor = db.cursor()
                    cursor.execute(reservation_query, (branch_id,))
                    reservation_results = cursor.fetchall()

                    # show all the reservations in the window
                    if reservation_results:
                        for reservation_id, customer_name, customer_phone, date, time, table_id in reservation_results:
                            reservation_info = f"{reservation_id}: {customer_name} - {customer_phone} - {date} - {time} - ({table_id})"
                            tk.Label(view_reservation_window, text=reservation_info, font=fontStyle).pack()
                    else:
                        tk.Label(view_reservation_window, text="No reservation found for this branch.", font=fontStyle).pack()

                    back_button = tk.Button(view_reservation_window, text="Back", command=view_reservation_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

                def cancel_reservation(selected_branch_info):
                    # Create a new window for canceling reservation
                    cancel_reservation_window = tk.Toplevel(window)
                    cancel_reservation_window.title("Cancel Reservation")
                    cancel_reservation_window.state('zoomed')
                    # cancel_reservation_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                    # Fetch reservation details from the database for the branch
                    cursor = db.cursor()
                    reservation_query = """
                        SELECT ReservationID, CustomerName, CustomerPhoneNO, Date, Time, TableID
                        FROM Reservation
                        WHERE BranchID = %s
                    """
                    cursor.execute(reservation_query, (branch_id,))
                    reservation_results = cursor.fetchall()
                    cursor.close()

                    # Create a list of reservations for the dropdown
                    reservation_list = [
                        f"{row[0]}: {row[1]} - {row[2]} - {row[3]} - {row[4]}"
                        for row in reservation_results
                    ] if reservation_results else []

                    reservation_var = tk.StringVar(cancel_reservation_window)
                    reservation_var.set(reservation_list[0] if reservation_list else "No reservations available")
                    reservation_dropdown = tk.OptionMenu(cancel_reservation_window, reservation_var, *reservation_list)
                    reservation_dropdown.pack()

                    def cancel_selected_reservation():
                        selected_reservation_id = reservation_var.get().split(":")[0]
                        cursor = db.cursor()
                        try:
                            # Start transaction
                            cursor.execute("START TRANSACTION")
                            
                            # Get the TableID of the reservation to be canceled
                            get_table_query = "SELECT TableID FROM Reservation WHERE ReservationID = %s"
                            cursor.execute(get_table_query, (selected_reservation_id,))
                            table_id = cursor.fetchone()
                            
                            if table_id:
                                table_id = table_id[0]  # Extract the TableID
                                
                                # Delete the reservation
                                delete_query = "DELETE FROM Reservation WHERE ReservationID = %s"
                                cursor.execute(delete_query, (selected_reservation_id,))
                                
                                # Update the availability of the table
                                update_table_query = "UPDATE Tables SET Availability = 1 WHERE TableID = %s"
                                cursor.execute(update_table_query, (table_id,))
                                
                                # Commit the changes
                                db.commit()
                                messagebox.showinfo("Success", f"Reservation {selected_reservation_id} has been canceled and table {table_id} is now available.")
                            else:
                                db.rollback()  # Rollback if no TableID is found for the reservation
                                messagebox.showinfo("Notice", f"Reservation {selected_reservation_id} was not found or has no associated table.")
                            
                            cancel_reservation_window.destroy()
                        except Exception as e:
                            db.rollback()
                            messagebox.showerror("Error", f"An error occurred: {e}")
                        finally:
                            cursor.close()

                    cancel_button = tk.Button(cancel_reservation_window, text="Cancel Reservation", command=cancel_selected_reservation, **buttonStyle)
                    cancel_button.pack()

                    back_button = tk.Button(cancel_reservation_window, text="Back", command=cancel_reservation_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

                # 3 buttons for taking reservation, viewing reservations, and cancel reservation
                take_reservation_button = tk.Button(reservation_window, text="Take Reservation", command=lambda: [reservation_window.destroy(), take_reservation(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)
                view_reservations_button = tk.Button(reservation_window, text="View Reservations", command=lambda: [reservation_window.destroy(), view_reservations()], font=('Helvetica', 12, 'bold'), height=2, width=15)
                cancel_reservation_button = tk.Button(reservation_window, text="Cancel Reservation", command=lambda: [reservation_window.destroy(), cancel_reservation(selected_branch_info)], font=('Helvetica', 12, 'bold'), height=2, width=15)

                # Pack buttons in the center frame
                take_reservation_button.pack(pady=10)
                view_reservations_button.pack(pady=10)
                cancel_reservation_button.pack(pady=10)

                #back button to go back to the previous window
                back_button = tk.Button(reservation_window, text="Back", command=lambda: [reservation_window.destroy()], **buttonStyle)
                back_button.pack(pady=10)

            # Create buttons
            take_order_button = tk.Button(center_frame, text="Orders", command=order, font=('Helvetica', 12, 'bold'), height=2, width=15)
            book_reservation_button = tk.Button(center_frame, text="Reservations", command=reservation, font=('Helvetica', 12, 'bold'), height=2, width=15)

            # Pack buttons in the center frame
            take_order_button.grid(row=0, column=0, padx=10, pady=10)
            book_reservation_button.grid(row=0, column=1, padx=10, pady=10)

            #back button to go to the previous window
            back_button = tk.Button(center_frame, text="Back", command=lambda: [waiting_staff_window.destroy(), staff_roles_window], **buttonStyle)
            back_button.grid(row=1, column=0, columnspan=2, pady=10)

        elif role == "Kitchen Staff":
            # Close the previous window
            window.withdraw()

            #get branch id from staff email and password
            cursor = db.cursor()
            cursor.execute("SELECT BranchID FROM Account WHERE Email = %s AND Password = %s", (email_entry.get(), password_entry.get()))
            branch_id = cursor.fetchone()[0]
            cursor.close()

            #get branch info from branch id
            cursor = db.cursor()
            cursor.execute("SELECT City, PostCode FROM Branch WHERE BranchID = %s", (branch_id,))
            branch_info = cursor.fetchone()
            selected_branch_info = branch_info[0] + " - " + branch_info[1]
            cursor.close()

            kitchen_staff_window = tk.Toplevel(window)
            kitchen_staff_window.title(f"Kitchen Staff Options - {selected_branch_info}")
            kitchen_staff_window.state('zoomed')
            # kitchen_staff_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

            # Center frame for holding the buttons
            center_frame = tk.Frame(kitchen_staff_window)
            center_frame.pack(expand=True)

            # Define functionalities for each button (placeholder functions)

            def view_orders():
                view_orders_window = tk.Toplevel(window)
                view_orders_window.title("View Orders")
                view_orders_window.state('zoomed')
                # view_orders_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                orders_listbox = tk.Listbox(view_orders_window, width=50, height=20)
                orders_listbox.pack(pady=20)

                # Fetch all orders with their corresponding StockType for the branch
                cursor = db.cursor()
                cursor.execute("""SELECT o.TrackID, s.StockType, o.TableID
                                    FROM Orderr o
                                    INNER JOIN Stock s ON o.StockID = s.StockID
                                    WHERE o.TableID IN (
                                        SELECT TableID FROM Tables WHERE BranchID = %s AND Availability = 0
                                    )""", (branch_id,))
                
                order_results = cursor.fetchall()
                cursor.close()

                # Populate the listbox with orders
                for order in order_results:
                    orders_listbox.insert(tk.END, f"{order[0]}: {order[1]} - Table ID: {order[2]}")

                def complete_order():
                    # Check if an order is selected
                    if orders_listbox.curselection():
                        index = orders_listbox.curselection()[0]
                        selected_order = orders_listbox.get(index)
                        track_id = selected_order.split(":")[0]

                        # Process to remove the order from the system and add points to the account
                        cursor = db.cursor()
                        try:
                            messagebox.showinfo("Success", "Order completed.")

                            # Remove the order from the ListBox
                            orders_listbox.delete(index)

                        except Exception as e:
                            db.rollback()
                            messagebox.showerror("Error", str(e))
                        finally:
                            cursor.close()

                # Button to mark an order as completed
                complete_order_button = tk.Button(view_orders_window, text="Complete Order", command=complete_order, **buttonStyle)
                complete_order_button.pack(pady=10)


                back_button = tk.Button(view_orders_window, text="Back", command=view_orders_window.destroy, **buttonStyle)
                back_button.pack(pady=10)

            def update_stock():
                
                stock_options_window = tk.Toplevel(window)
                stock_options_window.title(f"Stock Options - {selected_branch_info}")
                stock_options_window.state('zoomed')

                stock_center_frame = tk.Frame(stock_options_window)
                stock_center_frame.pack(expand=True)
                # stock_options_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                # Define functionalities for each button 
                view_stock_button = tk.Button(stock_center_frame, text="View Stock", command=lambda: view_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
                add_stock_button = tk.Button(stock_center_frame, text="Add Stock", command=lambda: add_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
                remove_stock_button = tk.Button(stock_center_frame, text="Remove Stock", command=lambda: remove_stock(selected_branch_info), font=('Helvetica', 12, 'bold'), height=2, width=15)
                
                # Pack buttons in the center frame
                view_stock_button.grid(row=0, column=0, padx=10, pady=10)
                add_stock_button.grid(row=0, column=1, padx=10, pady=10)
                remove_stock_button.grid(row=0, column=2, padx=10, pady=10)

                # Back button to go back to the previous window
                back_button = tk.Button(stock_options_window, text="Back", command=stock_options_window.destroy, **buttonStyle)
                back_button.pack(pady=10)

            def view_stock(selected_branch_info):
                view_stock_window = tk.Toplevel(window)
                view_stock_window.title("View Stock")
                view_stock_window.state('zoomed')
                # view_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                # Fetch all stock for the branch
                cursor = db.cursor()
                cursor.execute("SELECT StockID, StockType, AmountInStock, Price FROM Stock WHERE BranchID = %s", (branch_id,))
                stock_results = cursor.fetchall()

                # Print all the stock in the window
                if stock_results:
                    for stock_id, stock_type, amount_in_stock, price in stock_results:
                        stock_info = f"{stock_id}: {stock_type} - Amount: {amount_in_stock} - Price: £{price}"
                        tk.Label(view_stock_window, text=stock_info, font=fontStyle).pack()

                else:
                    tk.Label(view_stock_window, text="No stock found for this branch.", font=fontStyle).pack()

                back_button = tk.Button(view_stock_window, text="Back", command=view_stock_window.destroy, **buttonStyle)
                back_button.pack(pady=10)
            
            def add_stock(selected_branch_info):
                add_stock_window = tk.Toplevel(window)
                add_stock_window.title("Add Stock")
                add_stock_window.state('zoomed')
                # add_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                # Entry fields for stock details
                stock_type_label = tk.Label(add_stock_window, text="Stock Type:", font=fontStyle)
                stock_type_label.pack()
                stock_type_entry = tk.Entry(add_stock_window, font=fontStyle)
                stock_type_entry.pack()

                amount_in_stock_label = tk.Label(add_stock_window, text="Amount in Stock:", font=fontStyle)
                amount_in_stock_label.pack()
                amount_in_stock_entry = tk.Entry(add_stock_window, font=fontStyle)
                amount_in_stock_entry.pack()

                price_label = tk.Label(add_stock_window, text="Price:", font=fontStyle)
                price_label.pack()
                price_entry = tk.Entry(add_stock_window, font=fontStyle)
                price_entry.pack()

                # Submit function
                def submit_stock_details():
                    stock_type = stock_type_entry.get()
                    amount_in_stock = amount_in_stock_entry.get()
                    price = price_entry.get()

                    # Generate Stock ID based on the last StockID
                    cursor = db.cursor()
                    cursor.execute("SELECT MAX(StockID) FROM Stock")
                    last_stock_id_row = cursor.fetchone()
                    last_stock_id = last_stock_id_row[0] if last_stock_id_row and last_stock_id_row[0] else "S0"
                    new_stock_id_number = int(last_stock_id.lstrip("S")) + 1
                    new_stock_id = "S" + str(new_stock_id_number)

                    # Insert into database (adjust according to your schema)
                    insert_query = """
                        INSERT INTO Stock (StockID, StockType, AmountInStock, Price, BranchID)
                        SELECT %s, %s, %s, %s, Branch.BranchID
                        FROM Branch
                        WHERE BranchID = (%s)
                    """
                    try:
                        cursor.execute(insert_query, (new_stock_id, stock_type, amount_in_stock, price, branch_id))
                        db.commit()
                        messagebox.showinfo("Success", f"Stock {new_stock_id} successfully added.")
                    except Exception as e:
                        messagebox.showerror("Error", f"An error occurred: {e}")
                    finally:
                        add_stock_window.destroy()
                        update_stock(selected_branch_info)

                submit_button = tk.Button(add_stock_window, text="Submit", command=submit_stock_details, **buttonStyle)
                submit_button.pack()
                back_button = tk.Button(add_stock_window, text="Back", command=add_stock_window.destroy, **buttonStyle)
                back_button.pack(pady=10)

                # Separator
                ttk.Separator(add_stock_window, orient='horizontal').pack(fill='x', pady=10)

                #dropdown list of all available stock
                def get_available_stock(branch_id):
                    cursor = db.cursor()
                    cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s", (branch_id,))
                    return cursor.fetchall()
                
                available_stock = get_available_stock(branch_id)

                stock_var = tk.StringVar(add_stock_window)
                stock_var.set("Select stock")
                stock_dropdown_label = tk.Label(add_stock_window, text="Select Stock:", font=fontStyle)
                stock_dropdown_label.pack()
                stock_dropdown = tk.OptionMenu(add_stock_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
                stock_dropdown.pack()

                # add ammoount to stock text box
                amount_to_add_label = tk.Label(add_stock_window, text="Amount to Add:", font=fontStyle)
                amount_to_add_label.pack()
                amount_to_add_entry = tk.Entry(add_stock_window, font=fontStyle)
                amount_to_add_entry.pack()

                #function to add stock
                def add_stock():
                    selected_stock_id = stock_var.get().split(" - ")[0]
                    amount_to_add = amount_to_add_entry.get()

                    if selected_stock_id.startswith("Select"):
                        messagebox.showerror("Error", "You must select a valid stock.")
                        return

                    cursor = db.cursor()
                    try:
                        #update the stock amount
                        update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock + %s WHERE StockID = %s"
                        cursor.execute(update_stock_query, (amount_to_add, selected_stock_id))
                        db.commit()
                        messagebox.showinfo("Success", f"{amount_to_add} of stock {selected_stock_id} successfully added.")
                    except Exception as e:
                        messagebox.showerror("Error", f"An error occurred: {e}")
                    finally:
                        add_stock_window.destroy()
                        update_stock(selected_branch_info)

                add_button = tk.Button(add_stock_window, text="Add Stock", command=add_stock, **buttonStyle)
                add_button.pack()

                #back button to go back to the previous window
                back_button = tk.Button(add_stock_window, text="Back", command=add_stock_window.destroy, **buttonStyle)
                back_button.pack(pady=10)

            def remove_stock(selected_branch_info):
                remove_stock_window = tk.Toplevel(window)
                remove_stock_window.title("Remove Stock")
                remove_stock_window.state('zoomed')
                # remove_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

                # Fetch stock details from the database
                stock_query = """
                    SELECT StockID, StockType
                    FROM Stock
                    WHERE BranchID = (
                        SELECT BranchID
                        FROM Branch
                        WHERE BranchID = %s
                    )
                """
                cursor = db.cursor()
                cursor.execute(stock_query, (branch_id,))
                stock_results = cursor.fetchall()

                # Create a list of stock for the dropdown
                stock_list = [f"{row[0]}: {row[1]}" for row in stock_results] if stock_results else []

                if stock_list:
                    stock_var = tk.StringVar(remove_stock_window)
                    stock_var.set(stock_list[0])
                    stock_dropdown = tk.OptionMenu(remove_stock_window, stock_var, *stock_list)
                    stock_dropdown.pack()
            
                    def remove_selected_stock():
                        selected = stock_var.get().split(":")[0]
                        delete_query = "DELETE FROM Stock WHERE StockID = %s"
                        try:
                            cursor.execute(delete_query, (selected,))
                            db.commit()
                            messagebox.showinfo("Success", f"Stock {selected} has been removed.")
                            remove_stock_window.destroy()
                        except Exception as e:
                            messagebox.showerror("Error", f"An error occurred: {e}")
                    
                    remove_button = tk.Button(remove_stock_window, text="Remove Stock", command=remove_selected_stock, **buttonStyle)
                    remove_button.pack()
                    back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)

                    #separator
                    ttk.Separator(remove_stock_window, orient='horizontal').pack(fill='x', pady=10)

                    #dropdown list of all available stock
                    def get_available_stock(branch_id):
                        cursor = db.cursor()
                        cursor.execute("SELECT StockID, StockType FROM Stock WHERE BranchID = %s", (branch_id,))
                        return cursor.fetchall()
                    
                    available_stock = get_available_stock(branch_id)

                    stock_var = tk.StringVar(remove_stock_window)
                    stock_var.set("Select stock")
                    stock_dropdown_label = tk.Label(remove_stock_window, text="Select Stock:", font=fontStyle)
                    stock_dropdown_label.pack()
                    stock_dropdown = tk.OptionMenu(remove_stock_window, stock_var, *[f"{stock[0]} - {stock[1]}" for stock in available_stock])
                    stock_dropdown.pack()

                    # add ammoount to stock text box
                    amount_to_remove_label = tk.Label(remove_stock_window, text="Amount to Remove:", font=fontStyle)
                    amount_to_remove_label.pack()
                    amount_to_remove_entry = tk.Entry(remove_stock_window, font=fontStyle)
                    amount_to_remove_entry.pack()

                    #function to add stock
                    def remove_stock():
                        selected_stock_id = stock_var.get().split(" - ")[0]
                        amount_to_remove = amount_to_remove_entry.get()

                        if selected_stock_id.startswith("Select"):
                            messagebox.showerror("Error", "You must select a valid stock.")
                            return

                        cursor = db.cursor()
                        try:
                            #update the stock amount
                            update_stock_query = "UPDATE Stock SET AmountInStock = AmountInStock - %s WHERE StockID = %s"
                            cursor.execute(update_stock_query, (amount_to_remove, selected_stock_id))
                            db.commit()
                            messagebox.showinfo("Success", f"{amount_to_remove} of stock {selected_stock_id} successfully removed.")
                        except Exception as e:
                            messagebox.showerror("Error", f"An error occurred: {e}")
                        finally:
                            remove_stock_window.destroy()
                            update_stock(selected_branch_info)

                    remove_button = tk.Button(remove_stock_window, text="Remove Stock", command=remove_stock, **buttonStyle)
                    remove_button.pack()

                    #back button to go back to the previous window
                    back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)
                else:
                    tk.Label(remove_stock_window, text="No stock found to remove.", font=fontStyle).pack()
                    back_button = tk.Button(remove_stock_window, text="Back", command=remove_stock_window.destroy, **buttonStyle)
                    back_button.pack(pady=10)
            
            # Create buttons
            view_orders_button = tk.Button(center_frame, text="View Orders", command=view_orders, font=('Helvetica', 12, 'bold'), height=2, width=15)
            update_stock_button = tk.Button(center_frame, text="Update Stock", command=update_stock, font=('Helvetica', 12, 'bold'), height=2, width=15)

            # Pack buttons in the center frame
            view_orders_button.grid(row=0, column=0, padx=10, pady=10)
            update_stock_button.grid(row=0, column=1, padx=10, pady=10)

            #back button to go to the previous window
            back_button = tk.Button(center_frame, text="Back", command=lambda: [kitchen_staff_window.destroy(), staff_roles_window], **buttonStyle)
            back_button.grid(row=1, column=0, columnspan=2, pady=10)

        else:
            show_staff(selected_branch_info, role, staff_roles_window)

    button_waiting_staff = tk.Button(center_frame, text="Waiting Staff", command=lambda: button_click("Waiting Staff"), font=('Helvetica', 12, 'bold'), height=2, width=15)
    button_manager = tk.Button(center_frame, text="Manager", command=lambda: button_click("Manager"), font=('Helvetica', 12, 'bold'), height=2, width=15)
    button_kitchen_staff = tk.Button(center_frame, text="Kitchen Staff", command=lambda: button_click("Kitchen Staff"), font=('Helvetica', 12, 'bold'), height=2, width=15)
    
    show_all_staff_button = tk.Button(center_frame, text="Show all staff", command = show_all_staff, font=('Helvetica', 12, 'bold'), height=2, width=15)
    add_staff_button = tk.Button(center_frame, text="Add staff", command=add_staff, font=('Helvetica', 12, 'bold'), height=2, width=15)
    remove_staff_button = tk.Button(center_frame, text="Remove staff", command=remove_staff, font=('Helvetica', 12, 'bold'), height=2, width=15)

    button_manager.grid(row=0, column=0, padx=10, pady=10)
    button_waiting_staff.grid(row=0, column=1, padx=10, pady=10)
    button_kitchen_staff.grid(row=0, column=2, padx=10, pady=10)
    show_all_staff_button.grid(row=1, column=0, padx=10, pady=10)
    add_staff_button.grid(row=1, column=1, padx=10, pady=10)
    remove_staff_button.grid(row=1, column=2, padx=10, pady=10)

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
            elif role == 'Waiting Staff':
                waiting_staff_Login(username_entry, password_entry)
            elif role == 'Kitchen Staff':
                Kitchen_Staff_Login(username_entry, password_entry)
            elif role == 'Manager':
                manager_Login(username_entry, password_entry)
            else:
                print(f"Login successful! Role: {role}")
                # Here, you would redirect to other role-specific interfaces
        else:
            invalid_screen()

    window.title("Login")
    window.state('zoomed')
    # window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac
    def on_enter(e):
        login_button.config(bg='lightgrey')

    # Function to revert the button style on leave
    def on_leave(e):
        login_button.config(bg='SystemButtonFace')
    
    def help_on_enter(e):
            help_button.config(bg='gray')  # Change color on hover

    def help_on_leave(e):
        help_button.config(bg='lightgrey') 
    def open_help():
        help_window = tk.Toplevel(window)
        help_window.title("Help")
        help_window.geometry("400x300")  # Adjust size as needed

        # Text area for comments
        comment_text = tk.Text(help_window, height=10, width=40)
        comment_text.pack(pady=10)
        def submit_comment():
            comment = comment_text.get("1.0", "end-1c")
            print("Comment submitted:", comment)  # Replace with actual processing logic
            help_window.destroy()
        submit_button = tk.Button(help_window, text="Submit Comment", command=submit_comment)
        submit_button.pack(pady=10)
    window_width = 500
    window_height = 400
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    # Create a top border
    top_border = tk.Frame(window, bg='black', height=95)  # Reduced height
    top_border.pack(side='top', fill='x')
    top_border.pack_propagate(0)
    # Add a help button to the top border
    help_font = tkFont.Font(family="Arial", size=25, weight="bold")
    help_button = tk.Button(top_border, text="Help", command=open_help, font=help_font, bg='white', relief='groove', bd=2)
    help_button.pack(side='right', padx=10, pady=5)
    help_button.bind("<Enter>", help_on_enter)
    help_button.bind("<Leave>", help_on_leave)

    # Load and add a logo to the top border
    logo_image = Image.open("restt.png")  # Replace with your logo path
    logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)  # Resize logo
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(top_border, image=logo_photo, bg='gray')
    logo_label.image = logo_photo  # Keep a reference
    logo_label.pack(side='left', padx=10, pady=5)

    
    title_font = tkFont.Font(family="Arial", size=22, weight="bold")
    title_label = tk.Label(window, text="Horizon Restaurant", font=title_font)
    title_label.pack(pady=(5, 20))  # Adjust padding as needed

    # Adjusted font sizes
    customFont = tkFont.Font(family="Helvetica", size=16, weight="bold")
    labelFont = tkFont.Font(family="Arial", size=14)

    # Create a frame for the login box with increased padding and size
    login_frame = tk.Frame(window, bg='white', bd=5, relief="groove", highlightthickness=0)
    login_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=300)  # Centered with specific size

    # Configure grid layout inside login_frame
    login_frame.columnconfigure(0, weight=1)
    login_frame.rowconfigure([0, 1, 2, 3], weight=1)

    # Username label and entry with adjusted padding
    username_label = tk.Label(login_frame, text="Email:", bg='white', font=labelFont)
    username_label.grid(row=0, column=0, pady=(15, 5), padx=20, sticky='ew')
    username_entry = tk.Entry(login_frame, font=customFont, bd=3, relief="groove")
    username_entry.grid(row=1, column=0, pady=5, padx=20, sticky='ew')

    # Password label and entry with adjusted padding
    password_label = tk.Label(login_frame, text="Password:", bg='white', font=labelFont)
    password_label.grid(row=2, column=0, pady=5, padx=20, sticky='ew')
    password_entry = tk.Entry(login_frame, show="*", font=customFont, bd=3, relief="groove")
    password_entry.grid(row=3, column=0, pady=5, padx=20, sticky='ew')

    # Login button with hover effect and adjusted padding
    login_button = tk.Button(login_frame, text="Login", command=login, font=customFont, bd=3, relief="raised")
    login_button.grid(row=4, column=0, pady=15, padx=20, sticky='ew')
    login_button.bind("<Enter>", on_enter)
    login_button.bind("<Leave>", on_leave)

    window.mainloop()

# Run the login screen
login_screen()

# Close the database connection when the window is closed
db.close()