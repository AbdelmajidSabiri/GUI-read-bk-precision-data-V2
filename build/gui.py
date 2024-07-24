from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage,ttk, DoubleVar,Label,StringVar, BooleanVar
from tkinter.font import Font
import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import sys,time
import math
import random
sys.path.append('C:\\Users\\dell\\GUI-read-Bk-precision-data')
from readData import Add_current, Bkp8600, Add_voltage, Add_serialNum, CollectData
from PIL import Image, ImageTk
from datetime import datetime



class GUI:

    ASSETS_PATH = Path(r"C:\Users\dell\GUI-read-Bk-precision-data-V2\build\assets\frame0")
    def __init__(self):

        self.bk_device = Bkp8600()
        self.bk_device.initialize()
        self.data_list_current = []
        self.data_list_voltage = []
        self.data_list_power = []
        self.max_power = 0.0
        self.MPP = {"Vmpp" : 0 , "Impp" : 0}
        self.progress = 0

        self.window = ctk.CTk()
        self.window.geometry("1377x743")
        self.window.title("Agamine Solar LAMINATE TESTING V 1.0")
        self.window.configure(fg_color = "#0C0028")

        # Create variables for displaying max power and other parameters
        self.max_power_var = DoubleVar()
        self.Vmpp_var = StringVar()
        self.Impp_var = StringVar()
        self.Isc_var = StringVar()
        self.Voc_var = StringVar()
        self.temp_var = StringVar(value="25")


        self.left_frame = ctk.CTkFrame(master=self.window, width=200, corner_radius=0, fg_color='#0C0028')
        self.left_frame.pack(side="left", fill="y")

        # Load images
        self.image_dashboard = PhotoImage(file=self.relative_to_assets("image_2.png"))
        self.image_bk_profiles = PhotoImage(file=self.relative_to_assets("image_3.png"))

        # Create buttons with images
        self.dashboard_button = ctk.CTkButton(master=self.left_frame, image=self.image_dashboard, text="DASHBOARD", compound="top", command=self.show_dashboard, fg_color='#0C0028', text_color='#FFFFFF', font=("Arial Rounded MT Bold",14))
        self.dashboard_button.pack(pady=10, padx=10, anchor='w')

        self.bk_profiles_button = ctk.CTkButton(master=self.left_frame, image=self.image_bk_profiles, text="BK PROFILES", compound="top", command=self.show_bk_profiles, fg_color='#0C0028', text_color='#473F70', font=("Arial Rounded MT Bold",14))
        self.bk_profiles_button.pack(pady=10, padx=10, anchor='w')

        # Create a frame for the main content
        self.main_frame = ctk.CTkFrame(master=self.window, fg_color='#0C0028')
        self.main_frame.pack(side="right", expand=True, fill="both", padx=0, pady=0)

        self.dashboard_frame = ctk.CTkFrame(master=self.main_frame, fg_color='#0C0028')
        self.bk_profiles_frame = ctk.CTkFrame(master=self.main_frame, fg_color='#47289b')

        # Initial display
        self.dashboard_frame.pack(fill="both", expand=True)

        # Setup content of dashboard
        self.setup_dashboard_content()

        # Start update loop for maximum power and time
        self.update_max_power()
        self.update_time()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window closing event
        self.window.mainloop()

    @staticmethod
    def relative_to_assets(path: str) -> Path:
        return GUI.ASSETS_PATH / Path(path)

    # Funtion to Get Max power
    def GetMaxPower(self) :

        # Get current and voltage
        current, voltage = self.get_data()
        # Assign 0 to power if no data found
        if current and voltage :
            power = current * voltage
        else :
            power = 0

        # If other max power found, change the old one and return it
        if power > self.max_power:
            self.max_power = power

            # Take voltage and current of Max Power (Vmpp & Impp)
            self.MPP["Vmpp"] = voltage
            self.MPP["Impp"] = current
        return self.max_power,self.MPP

    # Function to update Max Power
    def update_max_power(self):
        # Get max power, Vmpp and Impp
        max_power, MPP = self.GetMaxPower()

        #Format Values
        max_power_formatted = "{:.8f} W".format(max_power)
        Vmpp_formatted = "{:.8f} V".format(MPP["Vmpp"])
        Impp_formatted = "{:.8f} A".format(MPP["Impp"])
        
        #Assign Values to Variables
        self.max_power_var.set(max_power_formatted)
        self.Vmpp_var.set(Vmpp_formatted)
        self.Impp_var.set(Impp_formatted)

        # Calculate and Update Isc and Voc
        self.calculate_isc_voc()

        # Update every sec
        self.window.after(1000, self.update_max_power)

    # Calculate Isc and Voc
    def calculate_isc_voc(self):

        # Get Value of Isc if it found if not make it 0
        Isc_found = False
        for v, i in zip(self.data_list_voltage, self.data_list_current):
            if v == 0:
                self.Isc_var.set("{:.8f} A".format(i))
                Isc_found = True
                break
        if not Isc_found :
            self.Isc_var.set("0.00000000 A")    

        # Get Value of Voc if it found if not make it 0
        Voc_found = False

        for v, i in zip(self.data_list_voltage, self.data_list_current):
            
            if i == 0:
                self.Voc_var.set("{:.8f} V".format(v))
                Voc_found = True
                break

        if not Voc_found :
            self.Voc_var.set("0.00000000 V")  

    # Funtion to update Time
    def update_time(self):
        current_time = datetime.now().strftime('%H:%M:%S')   
        current_date = datetime.now().strftime('%d/%m/%Y')        
        self.time_label.configure(text=current_time)  
        self.date_label.configure(text = current_date)                        
        self.dashboard_frame.after(1000, self.update_time)    

    # Funtion to Get data from Bk-precision
    def get_data(self):
        try:
            measured_current = self.bk_device.get_current()
            voltage = self.bk_device.get_voltage()
            return measured_current, voltage
        except Exception as e:
            print(f"Error retrieving data: {e}")
            return 0.0, 0.0

    # Animation function for updating Combined (current & voltage) plot
    def animate_combined(self, i, ax):
        # Simulated data
        current = 10 * math.sin(i * 0.1) + random.uniform(-1, 1)
        voltage = 20 * math.cos(i * 0.1) + random.uniform(-1, 1)

        self.data_list_current.append(current)
        self.data_list_voltage.append(voltage)
        self.data_list_current = self.data_list_current[-50:]  # Limit to the last 50 data points
        self.data_list_voltage = self.data_list_voltage[-50:]  # Limit to the last 50 data points
        
        ax.clear()

        ax.set_facecolor('#0C0028')
        
        # Plot the current data
        ax.plot(self.data_list_current,color='#C48BFF', linewidth=2.5)
        ax.fill_between(range(len(self.data_list_current)), self.data_list_current, color='#A260E8', alpha=0.5, edgecolor='none')

        # Plot the voltage data
        ax.plot(self.data_list_voltage, color='#FEB9FF', linewidth=2.5)
        ax.fill_between(range(len(self.data_list_voltage)), self.data_list_voltage, color='#4B237B', alpha=0.5, edgecolor='none')

        ax.set_ylim([0, 20]) 

        ax.set_xlabel("Current", color='#AD94FF')
        ax.set_ylabel("Voltage", color='#AD94FF')
        ax.set_title("Simulated Current and Voltage", color='#AD94FF', fontsize=16)

        ax.spines['left'].set_color('#FFFFFF')
        ax.spines['bottom'].set_color('#FFFFFF')
        ax.spines['top'].set_color('#47289b')
        ax.spines['right'].set_color('#47289b')

        ax.tick_params(axis='x', colors='#FFFFFF')
        ax.tick_params(axis='y', colors='#FFFFFF')

        ax.grid(True, color='#3A3A3A')
        ax.xaxis.label.set_color('#AD94FF')
        ax.yaxis.label.set_color('#AD94FF')
        
    # Method to get Serial Number
    def get_serialNum(self):
        serial_number = self.entry_serialNum.get()
        return serial_number

    # Function to Get Data and send it to CollectData function That Add it to excel file
    def SaveData(self) :

        current_date = datetime.now()
        formatted_date = current_date.strftime("%m/%d/%Y")
        formatted_time = current_date.strftime("%H:%M:%S")

        serial_number = self.get_serialNum()
        Voc = round(float(self.Voc_var.get().split()[0]),4)
        Isc = round(float(self.Isc_var.get().split()[0]),4)
        max_power = self.max_power
        Impp = round(float(self.Impp_var.get().split()[0]),4)
        Vmpp = round(float(self.Vmpp_var.get().split()[0]),4)
        
        CollectData(formatted_date,formatted_time,serial_number,max_power,Vmpp,Impp,Voc,Isc)
        
    # Keep Updating progress bar, and if it arrives 100%, it Will save data
    def update_progress(self):
        if self.progress < 1:
            self.progress += 0.01
            self.progress_bar.set(self.progress)
            self.progress_label.configure(text=f"{int(self.progress * 100)}%")
            self.window.after(100, self.update_progress)  # Update self.progress every 100 milliseconds
        else:
            self.progress_label.configure(text="100%")
            self.status_label.configure(text="Saved", text_color="#06F30B")
            self.SaveData()
            self.run_button.configure(state = 'normal')
            self.run_button.configure(image = self.image_image_22)


    # Function To Start Test if RUN TEST button is pressed
    def run_test(self):
        self.progress = 0
        self.progress_bar.set(self.progress)
        self.status_label.configure(text="Running...", text_color="orange")
        self.run_button.configure(state = 'disabled')
        self.run_button.configure(image = self.pause)
        self.update_progress()
    
    def ON_Lamps(self):
        self.ON_button.configure(text_color = "#06F30B")
        self.OFF_button.configure(text_color = "grey")

    def OFF_Lamps(self):
        self.OFF_button.configure(text_color = "red")
        self.ON_button.configure(text_color = "grey")

    
    # Function to show content of dashboard frame if DASHBOARD button is pressed
    def show_dashboard(self):
        self.dashboard_frame.pack(fill="both", expand=True)
        self.bk_profiles_frame.pack_forget()

    # Function to show content of Bk Profiles frame if BK PROFILES button is pressed
    def show_bk_profiles(self):
        self.bk_profiles_frame.pack(fill="both", expand=True)
        self.dashboard_frame.pack_forget()


    # Funtion to Setup content of Dashboard Frame
    def setup_dashboard_content(self):

        # initialis dashborad canvas
        canvas = Canvas(
            self.dashboard_frame,
            bg = "#0C0028",
            height = 930,
            width = 1721,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        # Add images and Text
        canvas.place(x = 0, y = 0)
        self.image_image_1 = PhotoImage(
            file=self.relative_to_assets("image_1.png"))
        image_1 = canvas.create_image(
            351.0,
            66.0,
            image=self.image_image_1
        )

        canvas.create_text(
            56.0,
            53.0,
            anchor="nw",
            text="INSERT",
            fill="#FFFFFF",
            font=("Arial Rounded MT Bold",18)
        )

        canvas.create_text(
            840.0,
            649.0,
            anchor="nw",
            text="TEST CONDITIONS",
            fill="#FFFFFF",
            font=("Arial Rounded MT Bold", 20)
        )

        self.image_image_4 = PhotoImage(
            file=self.relative_to_assets("image_4.png"))
        image_4 = canvas.create_image(
            2,
            62.0,
            image=self.image_image_4
        )

        self.image_image_5 = PhotoImage(
            file=self.relative_to_assets("image_5.png"))
        image_5 = canvas.create_image(
            1459.0,
            62.0,
            image=self.image_image_5
        )

        self.image_image_6 = PhotoImage(
            file=self.relative_to_assets("image_6.png"))
        image_6 = canvas.create_image(
            1379.0,
            62.0,
            image=self.image_image_6
        )

        self.image_image_7 = PhotoImage(
            file=self.relative_to_assets("image_7.png"))
        image_7 = canvas.create_image(
            145.0,
            304.0,
            image=self.image_image_7
        )


        self.image_image_8 = PhotoImage(
            file=self.relative_to_assets("image_8.png"))
        image_8 = canvas.create_image(
            145.0,
            548.0,
            image=self.image_image_8
        )

        self.image_image_9 = PhotoImage(
            file=self.relative_to_assets("image_9.png"))
        image_9 = canvas.create_image(
            377.0,
            304.0,
            image=self.image_image_9
        )

        self.image_image_10 = PhotoImage(
            file=self.relative_to_assets("image_10.png"))
        image_10 = canvas.create_image(
            377.0,
            548.0,
            image=self.image_image_10
        )

        self.image_image_11 = PhotoImage(
            file=self.relative_to_assets("image_11.png"))
        image_11 = canvas.create_image(
            608.0,
            304.0,
            image=self.image_image_11
        )

        self.image_image_12 = PhotoImage(
            file=self.relative_to_assets("image_12.png"))
        image_12 = canvas.create_image(
            608.0,
            548.0,
            image=self.image_image_12
        )

        self.image_image_13 = PhotoImage(
            file=self.relative_to_assets("image_13.png"))
        image_13 = canvas.create_image(
            1135.0,
            793.0,
            image=self.image_image_13
        )

        self.image_image_14 = PhotoImage(
            file=self.relative_to_assets("image_14.png"))
        image_14 = canvas.create_image(
            145.0,
            303.0,
            image=self.image_image_14
        )

        self.image_image_15 = PhotoImage(
            file=self.relative_to_assets("image_15.png"))
        image_15 = canvas.create_image(
            145.0,
            548.0,
            image=self.image_image_15
        )

        self.image_image_16 = PhotoImage(
            file=self.relative_to_assets("image_16.png"))
        image_16 = canvas.create_image(
            377.0,
            303.0,
            image=self.image_image_16
        )

        self.image_image_17 = PhotoImage(
            file=self.relative_to_assets("image_17.png"))
        image_17 = canvas.create_image(
            377.0,
            548.0,
            image=self.image_image_17
        )

        self.image_image_18 = PhotoImage(
            file=self.relative_to_assets("image_18.png"))
        image_18 = canvas.create_image(
            609.0,
            303.0,
            image=self.image_image_18
        )

        self.image_image_19 = PhotoImage(
            file=self.relative_to_assets("image_19.png"))
        image_19 = canvas.create_image(
            609.0,
            548.0,
            image=self.image_image_19
        )

        canvas.create_text(
            131.0,
            180.0,
            anchor="nw",
            text="Isc",
            fill="#FFFFFF",
            font=("Poppins Medium", 16)
        )

        canvas.create_text(
            354.0,
            180.0,
            anchor="nw",
            text="Voc",
            fill="#FFFFFF",
            font=("Poppins Medium", 16)
        )

        canvas.create_text(
            589.0,
            178.0,
            anchor="nw",
            text="Imp",
            fill="#FFFFFF",
            font=("Poppins Medium", 16)
        )

        canvas.create_text(
            579.0,
            426.0,
            anchor="nw",
            text="Status",
            fill="#FFFFFF",
            font=("Poppins Medium", 16)
        )

        canvas.create_text(
            347.0,
            422.0,
            anchor="nw",
            text="Pmpp",
            fill="#FFFFFF",
            font=("Poppins Medium",16)
        )

        canvas.create_text(
            125.0,
            422.0,
            anchor="nw",
            text="Vmp",
            fill="#FFFFFF",
            font=("Poppins Medium", 16)
        )

        canvas.create_text(
            844.0,
            726.0,
            anchor="nw",
            text="Lamps",
            fill="#FFFFFF",
            font=("Poppins Medium", 18)
        )

        canvas.create_text(
            1168.0,
            726.0,
            anchor="nw",
            text="Time",
            fill="#FFFFFF",
            font=("Poppins Medium", 18)
        )

        canvas.create_text(
            1168.0,
            815.0,
            anchor="nw",
            text="Date",
            fill="#FFFFFF",
            font=("Poppins Medium", 18)
        )

        canvas.create_text(
            844.0,
            815.0,
            anchor="nw",
            text="Temperature",
            fill="#FFFFFF",
            font=("David", 18)
        )
        canvas.create_text(
            900.0,
            575.0,
            anchor="nw",
            text="Current",
            fill="#FFFFFF",
            font=("David", 16)
        )
        canvas.create_text(
            1130.0,
            575.0,
            anchor="nw",
            text="Voltage",
            fill="#FFFFFF",
            font=("David", 16)
        )

        self.image_image_20 = PhotoImage(
            file=self.relative_to_assets("image_20.png"))
        image_20 = canvas.create_image(
            767.0,
            126.9999999999996,
            image=self.image_image_20
        )

        self.image_image_21 = PhotoImage(
            file=self.relative_to_assets("image_21.png"))
        image_21 = canvas.create_image(
            0.0,
            469.0,
            image=self.image_image_21
        )

        self.image_image_22 = PhotoImage(
            file=self.relative_to_assets("image_22.png"))


        self.image_image_23 = PhotoImage(
            file=self.relative_to_assets("image_23.png"))
        image_23 = canvas.create_image(
            1142.0,
            789.0,
            image=self.image_image_23
        )

        self.legendVol = PhotoImage(
            file=self.relative_to_assets("legendVol.png"))
        image_23 = canvas.create_image(
            1080.0,
            590.0,
            image=self.legendVol
        )

        self.legendCur = PhotoImage(
            file=self.relative_to_assets("legendCur.png"))
        image_23 = canvas.create_image(
            850.0,
            590.0,
            image=self.legendCur
        )

        self.pause = PhotoImage(
            file = self.relative_to_assets("Pause.png")
        )
        


        # Draw chart + animation
        fig_combined, ax_combined = plt.subplots(figsize=(6.5, 4))
        fig_combined.patch.set_facecolor("#0C0028")
        fig_combined.patch.set_edgecolor('#4522A1')
        fig_combined.patch.set_linewidth(2)
        canvas_combined = FigureCanvasTkAgg(fig_combined, master=self.dashboard_frame)
        canvas_combined.draw()
        canvas_combined.get_tk_widget().place(x=800, y=160)
        self.ani_combined = animation.FuncAnimation(
            fig_combined,
            self.animate_combined,
            fargs=(ax_combined,),
            interval=100
        )

        # Add labels to Display Data
        self.label_max_power_value = Label(
                self.dashboard_frame,
                textvariable=self.max_power_var,
                bg = "#281854",
                fg="#06F30B",
                font=("Arial Rounded MT Bold", 15)
            )
        self.label_max_power_value.place(x=305, y=528)

        self.label_Vmpp_value = Label(
                self.dashboard_frame,
                textvariable=self.Vmpp_var,
                bg="#281854",
                fg="#06F30B",
                font=("Arial Rounded MT Bold", 16)
            )
        self.label_Vmpp_value.place(x=80, y=528)

        self.label_Impp_value = Label(
                self.dashboard_frame,
                textvariable=self.Impp_var,
                bg="#281854",
                fg="#06F30B",
                font=("Arial Rounded MT Bold", 16)
            )
        self.label_Impp_value.place(x=530, y=285)
        
        self.label_Isc_value = Label(
                self.dashboard_frame,
                textvariable=self.Isc_var,
                bg="#281854",
                fg="#06F30B",
                font=("Arial Rounded MT Bold", 16)
            )
        self.label_Isc_value.place(x=80, y=285)

        self.label_Voc_value = Label(
                self.dashboard_frame,
                textvariable=self.Voc_var,
                bg="#281854",
                fg="#06F30B",
                font=("Arial Rounded MT Bold", 16)
            )
        self.label_Voc_value.place(x=305, y=285)


        # Entry Text for serial number of solar module
        self.entry_serialNum = ctk.CTkEntry(master=self.dashboard_frame, placeholder_text="Serial Number: 0215841210",border_width = 0, fg_color = "white", bg_color="white", width=200)
        self.entry_serialNum.place(x=150, y=40)

        # RUN TEST button to start test
        self.run_button = ctk.CTkButton(master=self.dashboard_frame, text = "RUN TEST" ,image=self.image_image_22, command=self.run_test, fg_color='#0C0028', text_color='#FFFFFF', font=("Arial Rounded MT Bold",18))
        self.run_button.place(x=500, y=25)

        # Progress bar to show the progress of the test
        self.progress_bar = ctk.CTkProgressBar(master=self.dashboard_frame)
        self.progress_bar.set(self.progress)
        self.progress_bar.place(x=680, y=45)

        # Progress label to display the percentage
        self.progress_label = ctk.CTkLabel(master=self.dashboard_frame, text="0%", font=("Arial", 16, "bold"), text_color='#FFFFFF', bg_color="#0C0028")
        self.progress_label.place(x=900,y=35)

        # Status Label to display the state of the test
        self.status_label = ctk.CTkLabel(master=self.dashboard_frame, text="Waiting", text_color="orange", font=("Arial", 18, "bold"), bg_color="#281854")
        self.status_label.place(x=450, y=425)

        # Time and Date Labels
        self.time_label = ctk.CTkLabel(master=self.dashboard_frame, text="", text_color="white", font=("David", 18))
        self.time_label.place(x=1010, y= 577)
        self.date_label = ctk.CTkLabel(master = self.dashboard_frame, text = "", text_color="White", font=("David", 18))
        self.date_label.place(x=1010, y=649)

        # Temperature Label
        self.temp_label = ctk.CTkLabel(master = self.dashboard_frame, textvariable = self.temp_var, text_color="#06F30B", font=("Arial Rounded MT Bold", 18))
        self.degree_label = ctk.CTkLabel(master = self.dashboard_frame, text = "°C", text_color="white", font=("Arial Rounded MT Bold", 18))
        self.temp_label.place(x=810, y=649)
        self.degree_label.place(x=840,y=649)

        # Lamps Button
        self.ON_button = ctk.CTkButton(master = self.dashboard_frame, text="ON", text_color="#06F30B", fg_color='#0C0028', command= self.ON_Lamps, width=20, font=("Arial Rounded MT Bold",18), hover_color='#0C0028')
        self.ON_button.place(x=770,y=579)
        self.OFF_button = ctk.CTkButton(master = self.dashboard_frame, text="OFF", text_color="grey", fg_color='#0C0028', command= self.OFF_Lamps, width=20, font=("Arial Rounded MT Bold",18), hover_color='#0C0028')
        self.OFF_button.place(x=820,y=579)

        

    # Funtion to close the application correctly
    def on_closing(self):
        self.bk_device.reset_to_manual()
        self.window.destroy()
        self.window.quit()

# Instantiate the GUI class to start the application
if __name__ == "__main__":
    GUI()

