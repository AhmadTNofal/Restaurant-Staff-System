# 

import tkinter as tk

def button_click(role):
    print(f"Button clicked for {role}!")

# Create the main window
window = tk.Tk()
window.title("Staff Roles")

# Heading frame for "Staff Roles"
heading_roles_frame = tk.Frame(window)
heading_roles_frame.pack(side=tk.TOP, pady=10)

# Heading label for "Staff Roles"
heading_roles_label = tk.Label(heading_roles_frame, text="Staff Roles", font=('Helvetica', 16, 'bold'))
heading_roles_label.pack(side=tk.LEFT, padx=10)

# Buttons frame for the buttons
buttons_frame = tk.Frame(window)
buttons_frame.pack(side=tk.TOP, pady=10)

# Create buttons in the buttons frame
button_waiting_staff = tk.Button(buttons_frame, text="Waiting Staff", command=lambda: button_click("Waiting Staff"), font=('Helvetica', 12, 'bold'), height=2, width=15)
button_manager = tk.Button(buttons_frame, text="Manager", command=lambda: button_click("Manager"), font=('Helvetica', 12, 'bold'), height=2, width=15)
button_kitchen_staff = tk.Button(buttons_frame, text="Kitchen Staff", command=lambda: button_click("Kitchen Staff"), font=('Helvetica', 12, 'bold'), height=2, width=15)

# Pack buttons into the buttons frame and center them
button_waiting_staff.pack(side=tk.LEFT, padx=10)
button_manager.pack(side=tk.LEFT, padx=10)
button_kitchen_staff.pack(side=tk.LEFT, padx=10)

# Start the GUI event loop
window.mainloop()
