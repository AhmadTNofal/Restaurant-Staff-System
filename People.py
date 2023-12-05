
# ====================== MAIN CLASS ====================== #
class Person:
    # ========== CONSTRUCTOR ========== #
    def __init__ (self, Name, Phone_Num):
        self.__Name = Name
        self.__Phone_Num = Phone_Num
        
    # ========== SETTERS ========== #
    def setName (self, Name):
        self.__Name = Name
    
    def setPhone_Num (self, Phone_Num):
        self.__Phone_Num = Phone_Num
        
    # ========== GETTERS ========== #
    def getName (self):
        return self.__Name
    
    def getPhone_Num (self):
        return self.__Phone_Num
    
# ======================= SUBCLASS ======================= #
class Staff:
    # ========== CONSTRUCTOR ========== #
    def __init__ (self, Name, Phone_Num, Email, Age, Password, Role, Staff_Id):
        super().__init__ (Name, Phone_Num)
        self.__Email = Email
        self.__Age = Age
        self.__Password = Password
        self.__Role = Role
        self.__Staff_Id = Staff_Id
        
    # ========== SETTERS ========== #
    def setEmail (self, Email):
        self.__Email = Email
        
    def setAge (self, Age):
        self.__Age = Age
        
    def setPassword (self, Password):
        self.__Password = Password
        
    def setRole (self, Role):
        self.__Role = Role
        
    def setStaff (self, Staff_Id):
        self.__Staff_Id = Staff_Id
        
    # ========== GETTERS ========== #
    def getEmail (self):
        return self.__Email
    
    def getAge (self):
        return self.__Age
    
    def getPassword (self):
        return self.__Password
    
    def getRole (self):
        return self.__Role
    
    def getStaff_Id (self):
        return self.__Staff_Id

    # ========== STAFF REPORT METHOD ========== #
    def staff_report (self, Staff_Id):
        pass
    
# ======================= SUBCLASS ======================= #
class Customer:
    # ========== CONSTRUCTOR ========== #
    def __init__(self, Name, Phone_Num, Customer_Id):
        super().__init__ (Name, Phone_Num)
        self.__Customer_Id = Customer_Id
        
    # ========== SETTERS ========== #
    def setCustomer (self, Customer_Id):
        self.__Customer_Id = Customer_Id
        
    # ========== GETTERS ========== #
    def getCustomer (self):
        return self.__Customer_Id
    
import tkinter as tk
import mysql.connector

# Connect to the database
db = mysql.connector.connect(
    host="mysqldevoyard.mysql.database.azure.com",
    user="admintest",
    password="P@ssw0rd",
    database="group1_asd"
)

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
            # if role == 'HRDirector':
            #     # Load HRDirector interface
            # elif role == 'Staff':
            #     # Load Staff interface
            # elif role == 'Customer':
            #     # Load Customer interface
            # Add your role-based redirection or interface loading code here
        else:
            # Invalid credentials
            print("Invalid email or password")

    # Create the login window
    window = tk.Tk()
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
