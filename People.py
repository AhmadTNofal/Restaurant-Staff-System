
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