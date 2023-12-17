
# ====================== MAIN CLASS ====================== #
class Person:
    # ========== CONSTRUCTOR ========== #
    def __init__(self, Name, Phone_Num):
        self.__Name = Name
        self.__Phone_Num = Phone_Num
        
    # ========== SETTERS ========== #
    def setName(self, Name):
        self.__Name = Name
    
    def setPhone_Num(self, Phone_Num):
        self.__Phone_Num = Phone_Num
        
    # ========== GETTERS ========== #
    def getName(self):
        return self.__Name
    
    def getPhone_Num(self):
        return self.__Phone_Num
    
# ======================= SUBCLASS ======================= #
class Staff(Person):
    # ========== CONSTRUCTOR ========== #
    def __init__(self, Name, Phone_Num, Email, Age, Password, Role, Staff_Id):
        super().__init__(Name, Phone_Num)
        self.__Email = Email
        self.__Age = Age
        self.__Password = Password
        self.__Role = Role
        self.__Staff_Id = Staff_Id
        
    # ========== SETTERS ========== #
    def setEmail(self, Email):
        self.__Email = Email
        
    def setAge(self, Age):
        self.__Age = Age
        
    def setPassword(self, Password):
        self.__Password = Password
        
    def setRole(self, Role):
        self.__Role = Role
        
    def setStaff_Id(self, Staff_Id):
        self.__Staff_Id = Staff_Id
        
    # ========== GETTERS ========== #
    def getEmail(self):
        return self.__Email
    
    def getAge(self):
        return self.__Age
    
    def getPassword(self):
        return self.__Password
    
    def getRole(self):
        return self.__Role
    
    def getStaff_Id(self):
        return self.__Staff_Id

# ======================= SUBCLASS ======================= #
class Customer(Person):
    # ========== CONSTRUCTOR ========== #
    def __init__(self, Name, Phone_Num, Customer_Id):
        super().__init__(Name, Phone_Num)
        self.__Customer_Id = Customer_Id
        
    # ========== SETTERS ========== #
    def setCustomer_Id(self, Customer_Id):
        self.__Customer_Id = Customer_Id
        
    # ========== GETTERS ========== #
    def getCustomer_Id(self):
        return self.__Customer_Id
    
import tkinter as tk
import mysql.connector

# Connect to the database
db = mysql.connector.connect(
    host="mysqldevoyard.mysql.database.azure.com",
    user="admintest",
    password="P@ssw0rd",
    database="group1_asd")

        # Create the login screen
def login_screen():
    def login():
        email = username_entry.get()
        password = password_entry.get()

# Retrieve data from the hrdirector table
        cursor = db.cursor()
        query = "SELECT * FROM hrdirector WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        result = cursor.fetchone()

        if result:
                    # Successful login
            print("Login successful!")
        else:
                    # Invalid credentials
            print("Invalid email or password")

            # Create the login window
    window = tk.Tk()
    window.title("Login")

    # Username label and entry
    username_label = tk.Label(window, text="Email:")
    username_label.pack()
    username_entry = tk.Entry(window)
    username_entry.pack()

            # Password label and entry
    password_label = tk.Label(window, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(window, show="*")
    password_entry.pack()

            # Login button
    login_button = tk.Button(window, text="Login", command=login)
    login_button.pack()

            # Run the login window
    window.mainloop()

        # Run the login screen
login_screen()
# import tkinter as tk
# import tkinter.font as tkFont
# import mysql.connector
# from PIL import Image, ImageTk
# from PIL import Image, ImageEnhance
# # ====================== MAIN CLASS ====================== #
# class Person:
#     # ========== CONSTRUCTOR ========== #
#     def __init__(self, Name, Phone_Num):
#         self.__Name = Name
#         self.__Phone_Num = Phone_Num
        
#     # ========== SETTERS ========== #
#     def setName(self, Name):
#         self.__Name = Name
    
#     def setPhone_Num(self, Phone_Num):
#         self.__Phone_Num = Phone_Num
        
#     # ========== GETTERS ========== #
#     def getName(self):
#         return self.__Name
    
#     def getPhone_Num(self):
#         return self.__Phone_Num
    
# # ======================= SUBCLASS ======================= #
# class Staff(Person):
#     # ========== CONSTRUCTOR ========== #
#     def __init__(self, Name, Phone_Num, Email, Age, Password, Role, Staff_Id):
#         super().__init__(Name, Phone_Num)
#         self.__Email = Email
#         self.__Age = Age
#         self.__Password = Password
#         self.__Role = Role
#         self.__Staff_Id = Staff_Id
        
#     # ========== SETTERS ========== #
#     def setEmail(self, Email):
#         self.__Email = Email
        
#     def setAge(self, Age):
#         self.__Age = Age
        
#     def setPassword(self, Password):
#         self.__Password = Password
        
#     def setRole(self, Role):
#         self.__Role = Role
        
#     def setStaff_Id(self, Staff_Id):
#         self.__Staff_Id = Staff_Id
        
#     # ========== GETTERS ========== #
#     def getEmail(self):
#         return self.__Email
    
#     def getAge(self):
#         return self.__Age
    
#     def getPassword(self):
#         return self.__Password
    
#     def getRole(self):
#         return self.__Role
    
#     def getStaff_Id(self):
#         return self.__Staff_Id

# # ======================= SUBCLASS ======================= #
# class Customer(Person):
#     # ========== CONSTRUCTOR ========== #
#     def __init__(self, Name, Phone_Num, Customer_Id):
#         super().__init__(Name, Phone_Num)
#         self.__Customer_Id = Customer_Id
        
#     # ========== SETTERS ========== #
#     def setCustomer_Id(self, Customer_Id):
#         self.__Customer_Id = Customer_Id
        
#     # ========== GETTERS ========== #
#     def getCustomer_Id(self):
#         return self.__Customer_Id

# # ======================= GUI and Database Code ======================= #
# def login_screen():
#     # Database connection
#     db = mysql.connector.connect(
#         host="mysqldevoyard.mysql.database.azure.com",
#         user="admintest",
#         password="P@ssw0rd",
#         database="group1_asd")

#     def login():
#         email = username_entry.get()
#         password = password_entry.get()

#         cursor = db.cursor()
#         query = "SELECT * FROM hrdirector WHERE email = %s AND password = %s"
#         cursor.execute(query, (email, password))
#         result = cursor.fetchone()

#         if result:
#             print("Login successful!")
#         else:
#             print("Invalid email or password")

#     # Function to highlight the button on hover
#     def on_enter(e):
#         login_button.config(bg='lightgrey')

#     # Function to revert the button style on leave
#     def on_leave(e):
#         login_button.config(bg='SystemButtonFace')

#     # Initialize the window
#     window = tk.Tk()
#     window.title("Login")
#     window_width = window.winfo_screenwidth()
#     window_height = window.winfo_screenheight()
#     window.geometry(f"{window_width}x{window_height}")
#     background_image = Image.open("background.jpg")  # Replace with your image path
#     background_image = background_image.resize((window_width, window_height), Image.Resampling.LANCZOS)  # Resize the image to fit your window size

#     # Adjust the transparency of the image
#     enhancer = ImageEnhance.Brightness(background_image)
#     background_image_transparent = enhancer.enhance(0.5)  # Reduce brightness for transparency effect

#     # Convert the image to a format Tkinter can use and set as background
#     bg_image = ImageTk.PhotoImage(background_image_transparent)
    
#     background_label = tk.Label(window, image=bg_image)
#     background_label.place(x=0, y=0, relwidth=1, relheight=1)
#     image = Image.open("restt.png")  # Replace with your image path
#     image = image.resize((100, 100), Image.Resampling.LANCZOS)  # Resize if necessary
#     photo = ImageTk.PhotoImage(image)
#     image_label = tk.Label(window, image=photo, bg='white')
#     image_label.image = photo  # Keep a reference!
#     image_label.pack(side="right", anchor="ne", padx=10, pady=10)
#     # Define custom fonts
#     customFont = tkFont.Font(family="Helvetica", size=12, weight="bold")
#     labelFont = tkFont.Font(family="Arial", size=10)

#     # Create a frame for the login box
#     login_frame = tk.Frame(window, bg='white', bd=3, relief="groove", highlightthickness=0)
#     login_frame.pack(expand=True)  # Use 'expand' to center the frame in the window

#     # Configure grid layout inside login_frame
#     login_frame.columnconfigure(0, weight=1)  # Makes the column expandable
#     login_frame.rowconfigure([0, 1, 2, 3], weight=1)  # Makes the rows expandable

#     # Username label and entry
#     username_label = tk.Label(login_frame, text="Email:", bg='white', font=labelFont)
#     username_label.grid(row=0, column=0, pady=5, sticky='ew')
#     username_entry = tk.Entry(login_frame, font=customFont, bd=2, relief="groove")
#     username_entry.grid(row=1, column=0, pady=5, sticky='ew')

#     # Password label and entry
#     password_label = tk.Label(login_frame, text="Password:", bg='white', font=labelFont)
#     password_label.grid(row=2, column=0, pady=5, sticky='ew')
#     password_entry = tk.Entry(login_frame, show="*", font=customFont, bd=2, relief="groove")
#     password_entry.grid(row=3, column=0, pady=5, sticky='ew')

#     # Login button with hover effect
#     login_button = tk.Button(login_frame, text="Login", command=login, font=customFont, bd=2, relief="raised")
#     login_button.grid(row=4, column=0, pady=10, sticky='ew')
#     login_button.bind("<Enter>", on_enter)
#     login_button.bind("<Leave>", on_leave)

#     # Center the window on the screen
#     window_width = 300
#     window_height = 200
#     screen_width = window.winfo_screenwidth()
#     screen_height = window.winfo_screenheight()
#     center_x = int(screen_width / 2 - window_width / 2)
#     center_y = int(screen_height / 2 - window_height / 2)
#     window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

#     window.mainloop()

# # Run the login screen
# login_screen()