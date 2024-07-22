from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage,ttk, DoubleVar,Label,StringVar, BooleanVar
from tkinter.font import Font
import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import sys,time
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
        self.window.configure(bg = "#0C0028")

        # Create variables for displaying max power and other parameters
        self.max_power_var = DoubleVar()
        self.Vmpp_var = StringVar()
        self.Impp_var = StringVar()
        self.Isc_var = StringVar()
        self.Voc_var = StringVar()

        self.left_frame = ctk.CTkFrame(master=self.window, width=200, corner_radius=0, fg_color='#0C0028')
        self.left_frame.pack(side="left", fill="y")

        # Load images
        self.image_dashboard = PhotoImage(file=self.relative_to_assets("image_2.png"))
        self.image_bk_profiles = PhotoImage(file=self.relative_to_assets("image_3.png"))

        # Create buttons with images
        self.dashboard_button = ctk.CTkButton(master=self.left_frame, image=self.image_dashboard, text="DASHBOARD", compound="top", command=self.show_dashboard, fg_color='#0C0028', text_color='#FFFFFF')
        self.dashboard_button.pack(pady=10, padx=10, anchor='w')

        self.bk_profiles_button = ctk.CTkButton(master=self.left_frame, image=self.image_bk_profiles, text="BK PROFILES", compound="top", command=self.show_bk_profiles, fg_color='#0C0028', text_color='#FFFFFF')
        self.bk_profiles_button.pack(pady=10, padx=10, anchor='w')

        # Create a frame for the main content
        self.main_frame = ctk.CTkFrame(master=self.window, fg_color='#47289b')
        self.main_frame.pack(side="right", expand=True, fill="both", padx=0, pady=0)

        self.dashboard_frame = ctk.CTkFrame(master=self.main_frame, fg_color='#47289b')
        self.bk_profiles_frame = ctk.CTkFrame(master=self.main_frame, fg_color='#47289b')

        self.TextFont = ctk.CTkFont(
            family="Lucida Sans",
            size=20,
            weight="normal",
            slant="roman",
            underline=0,
            overstrike=0)

        # Initial display
        self.dashboard_frame.pack(fill="both", expand=True)

        self.setup_dashboard_content()

        # Start update loop for maximum power
        self.update_max_power()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window closing event
        self.window.mainloop()

    @staticmethod
    def relative_to_assets(path: str) -> Path:
        return GUI.ASSETS_PATH / Path(path)


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

    # Keep updatign Max Power
    def update_max_power(self):
        # Update displayed maximum power and MPP values periodically
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

    def calculate_isc_voc(self):

        # Get Value of Isc if it found if not make it 0
        Isc_found = False
        for v, i in zip(self.data_list_voltage, self.data_list_current):
            if v == 0:
                self.Isc_var.set("{:.8f} A".format(i))
                Isc_found = True
                break
        if not Isc_found :
            self.Isc_var.set("0.00 A")    

        # Get Value of Voc if it found if not make it 0
        Voc_found = False

        for v, i in zip(self.data_list_voltage, self.data_list_current):
            
            if i == 0:
                self.Voc_var.set("{:.8f} V".format(v))
                Voc_found = True
                break

        if not Voc_found :
            self.Voc_var.set("0.00 V")    
    
    def update_progress(self):
        if self.progress < 1:
            self.progress += 0.01
            self.progress_bar.set(self.progress)
            self.progress_label.configure(text=f"{int(self.progress * 100)}%")
            self.window.after(100, self.update_progress)  # Update self.progress every 100 milliseconds
        else:
            self.progress_label.configure(text="100%")
            self.status_label.configure(text="Saved", text_color="green")
            self.plot_graph()

    def run_test(self):
        self.progress = 0
        self.progress_bar.set(self.progress)
        self.status_label.configure(text="Running...", text_color="orange")
        self.update_progress()

    def plot_graph(self):
        current = np.linspace(0, 9.2, 100)
        voltage = 9.97 - (current / 9.2) * 9.97

        fig, ax = plt.subplots()
        fig.patch.set_facecolor('#47289b')  # Changed background color
        ax.set_facecolor('#47289b')  # Changed background color

        # Gradient fill for voltage
        ax.plot(current, voltage, label="Voltage", color='#C48BFF', linewidth=2.5)
        ax.fill_between(current, voltage, color='#A260E8', alpha=0.5, edgecolor='none')

        current_curve = 4.63 * np.exp(-current / 2.0)
        # Gradient fill for current
        ax.plot(current, current_curve, label="Current", color='#9254C8', linewidth=2.5)
        ax.fill_between(current, current_curve, color='#4B237B', alpha=0.5, edgecolor='none')

        ax.set_xlabel("Current", color='#AD94FF', fontsize=12)
        ax.set_ylabel("Voltage", color='#AD94FF', fontsize=12)
        ax.xaxis.label.set_color('#AD94FF')
        ax.yaxis.label.set_color('#AD94FF')

        ax.spines['left'].set_color('#FFFFFF')
        ax.spines['bottom'].set_color('#FFFFFF')
        ax.spines['top'].set_color('#47289b')  # Changed color
        ax.spines['right'].set_color('#47289b')  # Changed color

        ax.tick_params(axis='x', colors='#FFFFFF')
        ax.tick_params(axis='y', colors='#FFFFFF')

        ax.legend(facecolor='none', edgecolor='none', fontsize=12)
        ax.grid(True, color='#3A3A3A')

        # Customize labels position and color
        ax.xaxis.label.set_color('#AD94FF')
        ax.yaxis.label.set_color('#AD94FF')
        ax.set_title('Current vs Voltage', color='#AD94FF', fontsize=16)

        # Add custom label
        plt.text(4.5, 2.5, 'Current', color='#AD94FF', fontsize=12, ha='center')
        plt.text(8.5, 6, 'Voltage', color='#AD94FF', fontsize=12, ha='center')

        canvas = FigureCanvasTkAgg(fig, master=self.dashboard_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=3, rowspan=6, columnspan=4, padx=10, pady=10, sticky="nsew")

    def show_dashboard(self):
        self.dashboard_frame.pack(fill="both", expand=True)
        self.bk_profiles_frame.pack_forget()

    def show_bk_profiles(self):
        self.bk_profiles_frame.pack(fill="both", expand=True)
        self.dashboard_frame.pack_forget()

    def get_data(self):
        try:
            measured_current = self.bk_device.get_current()
            voltage = self.bk_device.get_voltage()
            return measured_current, voltage
        except Exception as e:
            print(f"Error retrieving data: {e}")
            return 0.0, 0.0

    # Animation function for updating current plot
    def animate_current(self, i, ax):
        current, _ = self.get_data()
        self.data_list_current.append(current)
        self.data_list_current = self.data_list_current[-50:]  # Limit to the last 50 data points
        ax.clear()
        ax.plot(self.data_list_current)
        ax.set_ylim([0.0001, 0.003])


    # Animation function for updating Voltage plot
    def animate_voltage(self, i, ax):
        _, voltage = self.get_data()
        self.data_list_voltage.append(voltage)
        self.data_list_voltage = self.data_list_voltage[-50:]  # Limit to the last 50 data points
        ax.clear()
        ax.plot(self.data_list_voltage)
        ax.set_ylim([0, 20])


    # Animation function for updating Power plot
    def animate_power(self,i,ax) :
        current, voltage = self.get_data()
        power = current * voltage
        self.data_list_power.append(power)
        self.data_list_power = self.data_list_power[-50:]  # Limit to the last 50 data points
        ax.clear()
        ax.plot(self.data_list_power)
        ax.set_ylim([0, 0.000005])


    # Animation function for updating Combined (current & voltage) plot
    def animate_combined(self, i, ax):
        current, voltage = self.get_data()
        self.data_list_current.append(current)
        self.data_list_voltage.append(voltage)
        self.data_list_current = self.data_list_current[-50:]  # Limit to the last 50 data points
        self.data_list_voltage = self.data_list_voltage[-50:]  # Limit to the last 50 data points
        ax.clear()
        ax.plot(self.data_list_current, label='Current')
        ax.plot(self.data_list_voltage, label='Voltage')
        ax.legend()
        ax.set_ylim([0, 20]) 


    # Method change CC
    def add_current(self):
        current_value = float(self.entry_current.get())
        self.bk_device.set_current(current_value)

    # Method change CV
    def add_voltage(self):
        voltage_value = float(self.entry_voltage.get())
        self.bk_device.set_voltage(voltage_value)

    # Method to get Serial Number
    def get_serialNum(self):
        serial_number = self.entry_serialNum.get()
        return serial_number

    def test(self) :

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
        

    def setup_dashboard_content(self):
        # Dashboard content
        canvas = Canvas(
            self.dashboard_frame,
            bg = "#0C0028",
            height = 930,
            width = 1721,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

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
            font=("normal",18)
        )

        canvas.create_text(
            703.0,
            50.0,
            anchor="nw",
            text="RUN TEST",
            fill="#FFFFFF",
            font=("Poppins SemiBold", 22 * -1)
        )

        canvas.create_text(
            840.0,
            649.0,
            anchor="nw",
            text="TEST CONDITIONS",
            fill="#FFFFFF",
            font=("Poppins Bold", 24 * -1)
        )

        self.image_image_4 = PhotoImage(
            file=self.relative_to_assets("image_4.png"))
        image_4 = canvas.create_image(
            0.0,
            72.0,
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
            font=("Poppins Medium", 20 * -1)
        )

        canvas.create_text(
            354.0,
            180.0,
            anchor="nw",
            text="Voc",
            fill="#FFFFFF",
            font=("Poppins Medium", 20 * -1)
        )

        canvas.create_text(
            589.0,
            178.0,
            anchor="nw",
            text="Imp",
            fill="#FFFFFF",
            font=("Poppins Medium", 20 * -1)
        )

        canvas.create_text(
            579.0,
            426.0,
            anchor="nw",
            text="Status",
            fill="#FFFFFF",
            font=("Poppins Medium", 20 * -1)
        )

        canvas.create_text(
            347.0,
            422.0,
            anchor="nw",
            text="Pmpp",
            fill="#FFFFFF",
            font=("Poppins Medium", 20 * -1)
        )

        canvas.create_text(
            125.0,
            422.0,
            anchor="nw",
            text="Vmp",
            fill="#FFFFFF",
            font=("Poppins Medium", 20 * -1)
        )

        canvas.create_text(
            844.0,
            726.0,
            anchor="nw",
            text="Lamps",
            fill="#FFFFFF",
            font=("Poppins Medium", 20 * -1)
        )

        canvas.create_text(
            1168.0,
            726.0,
            anchor="nw",
            text="Time",
            fill="#FFFFFF",
            font=("Poppins Medium", 20 * -1)
        )

        canvas.create_text(
            1168.0,
            815.0,
            anchor="nw",
            text="Date",
            fill="#FFFFFF",
            font=("Poppins Medium", 20 * -1)
        )

        canvas.create_text(
            844.0,
            815.0,
            anchor="nw",
            text="Temperature",
            fill="#FFFFFF",
            font=("Poppins Medium", 20 * -1)
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


        self.serial_entry = ctk.CTkEntry(master=self.dashboard_frame, placeholder_text="Serial Number: 0215841210",border_width = 0, fg_color = "white", bg_color="white", width=200)
        self.serial_entry.place(x=150, y=40)

        self.run_button = ctk.CTkButton(master=self.dashboard_frame, text = "RUN TEST" ,image=self.image_image_22, command=self.run_test, fg_color='#0C0028', text_color='#FFFFFF', bg_color="#0C0028", font=self.TextFont)
        self.run_button.place(x=500, y=25)


        self.progress_bar = ctk.CTkProgressBar(master=self.dashboard_frame)
        self.progress_bar.set(self.progress)
        self.progress_bar.place(x=680, y=45)

        self.progress_label = ctk.CTkLabel(master=self.dashboard_frame, text="0%", font=("Arial", 16, "bold"), text_color='#FFFFFF', bg_color="#0C0028")
        self.progress_label.place(x=900,y=35)

        self.status_label = ctk.CTkLabel(master=self.dashboard_frame, text="Waiting", text_color="orange", font=("Arial", 18, "bold"), bg_color="#281854")
        self.status_label.place(x=450, y=425)

    def on_closing(self):
        self.bk_device.reset_to_manual()
        self.window.destroy()
        self.window.quit()

# Instantiate the GUI class to start the application
if __name__ == "__main__":
    GUI()

