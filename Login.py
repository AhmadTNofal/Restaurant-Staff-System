import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
import mysql.connector
from tkinter import messagebox
from PIL import Image, ImageTk
from PIL import Image, ImageEnhance
# Initialize the main window
window = tk.Tk()
window.state('zoomed')
# window.attributes('-fullscreen', True)  # Uncomment this for Linux/Mac

# Create font styles after initializing the main window
fontStyle = tkFont.Font(family="Arial", size=12)
buttonStyle = {"font": fontStyle, "bg": "darkgreen", "fg": "white", "bd": 2, "relief": "raised"}
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

    def show_reports():
        pass  # Implement the functionality
    
    def stock_options():
        # Close the previous window (manager options window)
        previous_window.destroy()
        
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

        # Extract city and postcode from the selected_branch_info
        city, postcode = selected_branch_info.split(", ")

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

    def remove_stock(selected_branch_info):
        # Close the previous window (stock options window)
        previous_window.destroy()

        remove_stock_window = tk.Toplevel(window)
        remove_stock_window.title("Remove Stock")
        remove_stock_window.state('zoomed')
        # remove_stock_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

        # Extract city and postcode from the selected_branch_info
        city, postcode = selected_branch_info.split(", ")

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

    back_button = tk.Button(manager_options_window, text="Back", command=lambda: [manager_options_window.destroy(), open_staff_roles_window(selected_branch_info)], **buttonStyle)
    back_button.pack(side=tk.BOTTOM, pady=10)

def waiting_staff_options(selected_branch_info, previous_window):
    # Close the previous window
    previous_window.destroy()

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

        def take_order():
            pass    # Implement the functionality for taking orders

        def view_orders():
            pass # Implement the functionality for viewing orders

        def print_receipt():
            pass # Implement the functionality for printing receipts

        # 3 buttons for taking order, viewing orders, and print recipt
        take_order_button = tk.Button(order_window, text="Take Order", command=lambda: [order_window.destroy(), take_order()], font=('Helvetica', 12, 'bold'), height=2, width=15)
        view_orders_button = tk.Button(order_window, text="View Orders", command=lambda: [order_window.destroy(), view_orders()], font=('Helvetica', 12, 'bold'), height=2, width=15)
        print_receipt_button = tk.Button(order_window, text="Print Receipt", command=lambda: [order_window.destroy(), print_receipt()], font=('Helvetica', 12, 'bold'), height=2, width=15)

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

        def take_reservation():
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
            date_label = tk.Label(take_reservation_window, text="Date:", font=fontStyle)
            date_label.pack()
            date_entry = tk.Entry(take_reservation_window, font=fontStyle)
            date_entry.pack()

            #time entry
            time_label = tk.Label(take_reservation_window, text="Time:", font=fontStyle)
            time_label.pack()
            time_entry = tk.Entry(take_reservation_window, font=fontStyle)
            time_entry.pack()

            #get branch id from selected branch info
            city, postcode = selected_branch_info.split(", ")
            cursor = db.cursor(buffered=True)
            branch_query = "SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s"
            cursor.execute(branch_query, (city, postcode))
            branch_result = cursor.fetchone()
            branch_id = branch_result[0]

            #create unique reservation id
            reservation_id_prefix = 'R'
            find_last_id_query = f"SELECT MAX(ReservationID) FROM Reservation WHERE ReservationID LIKE '{reservation_id_prefix}%'"
            cursor = db.cursor()
            cursor.execute(find_last_id_query)
            last_id_row = cursor.fetchone()
            last_id = last_id_row[0] if last_id_row and last_id_row[0] else reservation_id_prefix + "0"
            new_id_number = int(last_id.lstrip(reservation_id_prefix)) + 1
            new_reservation_id = reservation_id_prefix + str(new_id_number)

            # Submit function
            def submit_reservation_details():
                customer_name = customer_name_entry.get()
                customer_phone = customer_phone_entry.get()
                date = date_entry.get()
                time = time_entry.get()

                # Insert into database
                insert_query = """
                    INSERT INTO Reservation (ReservationID, CustomerName, CustomerPhoneNO, Date, Time, BranchID)
                    SELECT %s, %s, %s, %s, %s, %s 
                """
                try:
                    cursor.execute(insert_query, (new_reservation_id, customer_name, customer_phone, date, time, branch_id))
                    db.commit()
                    messagebox.showinfo("Success", f"Reservation {new_reservation_id} successfully added.")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")

            submit_button = tk.Button(take_reservation_window, text="Submit", command=submit_reservation_details, **buttonStyle)
            submit_button.pack()
            back_button = tk.Button(take_reservation_window, text="Back", command=take_reservation_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

        def view_reservations():
            # Create a new window for viewing reservation
            view_reservation_window = tk.Toplevel(window)
            view_reservation_window.title("View Reservation")
            view_reservation_window.state('zoomed')
            # view_reservation_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

            #get branch id from selected branch info
            city, postcode = selected_branch_info.split(", ")
            cursor = db.cursor(buffered=True)
            branch_query = "SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s"
            cursor.execute(branch_query, (city, postcode))
            branch_result = cursor.fetchone()
            branch_id = branch_result[0]

            #fetch reservation details from the database
            reservation_query = """
                SELECT ReservationID, CustomerName, CustomerPhoneNO, Date, Time
                FROM Reservation
                WHERE BranchID = %s
            """
            cursor = db.cursor()
            cursor.execute(reservation_query, (branch_id,))
            reservation_results = cursor.fetchall()

            # show all the reservations in the window
            if reservation_results:
                for reservation_id, customer_name, customer_phone, date, time in reservation_results:
                    reservation_info = f"{reservation_id}: {customer_name} - {customer_phone} - {date} - {time}"
                    tk.Label(view_reservation_window, text=reservation_info, font=fontStyle).pack()
            else:
                tk.Label(view_reservation_window, text="No reservation found for this branch.", font=fontStyle).pack()

            back_button = tk.Button(view_reservation_window, text="Back", command=view_reservation_window.destroy, **buttonStyle)
            back_button.pack(pady=10)

        def cancel_reservation():
            # Create a new window for canceling reservation
            cancel_reservation_window = tk.Toplevel(window)
            cancel_reservation_window.title("Cancel Reservation")
            cancel_reservation_window.state('zoomed')
            # cancel_reservation_window.attributes('-fullscreen', True) # Uncomment this for Linux/Mac

            #get branch id from selected branch info
            city, postcode = selected_branch_info.split(", ")
            cursor = db.cursor(buffered=True)
            branch_query = "SELECT BranchID FROM Branch WHERE City = %s AND PostCode = %s"
            cursor.execute(branch_query, (city, postcode))
            branch_result = cursor.fetchone()
            branch_id = branch_result[0]

            #fetch reservation details from the database
            reservation_query = """
                SELECT ReservationID, CustomerName, CustomerPhoneNO, Date, Time
                FROM Reservation
                WHERE BranchID = %s
            """
            cursor = db.cursor()
            cursor.execute(reservation_query, (branch_id,))
            reservation_results = cursor.fetchall()

            # Create a list of reservations for the dropdown
            reservation_list = [f"{row[0]}: {row[1]} - {row[2]} - {row[3]} - {row[4]}" for row in reservation_results] if reservation_results else []

            if reservation_list:
                reservation_var = tk.StringVar(cancel_reservation_window)
                reservation_var.set(reservation_list[0])
                reservation_dropdown = tk.OptionMenu(cancel_reservation_window, reservation_var, *reservation_list)
                reservation_dropdown.pack()

                def cancel_selected_reservation():
                    selected = reservation_var.get().split(":")[0]
                    delete_query = "DELETE FROM Reservation WHERE ReservationID = %s"
                    try:
                        cursor.execute(delete_query, (selected,))
                        db.commit()
                        messagebox.showinfo("Success", f"Reservation {selected} has been canceled.")
                        cancel_reservation_window.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"An error occurred: {e}")

                cancel_button = tk.Button(cancel_reservation_window, text="Cancel Reservation", command=cancel_selected_reservation, **buttonStyle)
                cancel_button.pack()
                back_button = tk.Button(cancel_reservation_window, text="Back", command=cancel_reservation_window.destroy, **buttonStyle)
                back_button.pack(pady=10)
            else:
                tk.Label(cancel_reservation_window, text="No reservation found to cancel.", font=fontStyle).pack()
                back_button = tk.Button(cancel_reservation_window, text="Back", command=cancel_reservation_window.destroy, **buttonStyle)
                back_button.pack(pady=10)


        # 3 buttons for taking reservation, viewing reservations, and cancel reservation
        take_reservation_button = tk.Button(reservation_window, text="Take Reservation", command=lambda: [reservation_window.destroy(), take_reservation()], font=('Helvetica', 12, 'bold'), height=2, width=15)
        view_reservations_button = tk.Button(reservation_window, text="View Reservations", command=lambda: [reservation_window.destroy(), view_reservations()], font=('Helvetica', 12, 'bold'), height=2, width=15)
        cancel_reservation_button = tk.Button(reservation_window, text="Cancel Reservation", command=lambda: [reservation_window.destroy(), cancel_reservation()], font=('Helvetica', 12, 'bold'), height=2, width=15)

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
    pass  # Implement the functionality

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

    center_frame = tk.Frame(staff_roles_window)
    center_frame.pack(expand=True)

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

    def button_click(role):
        if role == "Manager":
            manager_options(selected_branch_info, staff_roles_window)
        elif role == "Waiting Staff":
            waiting_staff_options(selected_branch_info, staff_roles_window)
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
    def logout():
        hr_options_window.destroy()
        window.deiconify()

    logout_button = tk.Button(hr_options_window, text="Logout", command=logout, **buttonStyle)
    logout_button.pack(pady=10)

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