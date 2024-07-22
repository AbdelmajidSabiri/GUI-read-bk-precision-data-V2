from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage
import customtkinter as ctk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\dell\GUI-read-Bk-precision-data-V2\build\assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def update_progress():
    global progress
    if progress < 1:
        progress += 0.01
        progress_bar.set(progress)
        progress_label.configure(text=f"{int(progress * 100)}%")
        root.after(100, update_progress)  # Update progress every 100 milliseconds
    else:
        progress_label.configure(text="100%")
        status_label.configure(text="Pass", text_color="green")
        plot_graph()

def run_test():
    global progress
    progress = 0
    progress_bar.set(progress)
    status_label.configure(text="Running...", text_color="orange")
    update_progress()

def plot_graph():
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

    canvas = FigureCanvasTkAgg(fig, master=dashboard_frame)
    canvas.draw()
    canvas.get_tk_widget().grid(row=1, column=3, rowspan=6, columnspan=4, padx=10, pady=10, sticky="nsew")

def show_dashboard():
    dashboard_frame.pack(fill="both", expand=True)
    bk_profiles_frame.pack_forget()

def show_bk_profiles():
    bk_profiles_frame.pack(fill="both", expand=True)
    dashboard_frame.pack_forget()

window = ctk.CTk()
window.geometry("1377x743")
window.title("Agamine Solar LAMINATE TESTING V 1.0")
window.configure(bg = "#0C0028")

left_frame = ctk.CTkFrame(master=window, width=200, corner_radius=0, fg_color='#0C0028')
left_frame.pack(side="left", fill="y")

# Load images
image_dashboard = PhotoImage(file=relative_to_assets("image_2.png"))
image_bk_profiles = PhotoImage(file=relative_to_assets("image_3.png"))

# Create buttons with images
dashboard_button = ctk.CTkButton(master=left_frame, image=image_dashboard, text="DASHBOARD", compound="top", command=show_dashboard, fg_color='#0C0028', text_color='#FFFFFF')
dashboard_button.pack(pady=10, padx=10, anchor='w')

bk_profiles_button = ctk.CTkButton(master=left_frame, image=image_bk_profiles, text="BK PROFILES", compound="top", command=show_bk_profiles, fg_color='#0C0028', text_color='#FFFFFF')
bk_profiles_button.pack(pady=10, padx=10, anchor='w')

# Create a frame for the main content
main_frame = ctk.CTkFrame(master=window, fg_color='#47289b')
main_frame.pack(side="right", expand=True, fill="both", padx=0, pady=0)

dashboard_frame = ctk.CTkFrame(master=main_frame, fg_color='#47289b')
bk_profiles_frame = ctk.CTkFrame(master=main_frame, fg_color='#47289b')

# Initial display
dashboard_frame.pack(fill="both", expand=True)

# Dashboard content
serial_label = ctk.CTkLabel(master=dashboard_frame, text="INSERT", font=("Arial", 12), text_color='#FFFFFF')
serial_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

serial_entry = ctk.CTkEntry(master=dashboard_frame, placeholder_text="Serial Number: 0215841210")
serial_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

run_button = ctk.CTkButton(master=dashboard_frame, text="RUN TEST", command=run_test, fg_color='#0C0028', text_color='#FFFFFF')
run_button.grid(row=0, column=2, padx=10, pady=10, sticky="w")

progress = 0
progress_bar = ctk.CTkProgressBar(master=dashboard_frame)
progress_bar.set(progress)
progress_bar.grid(row=0, column=3, padx=10, pady=10, sticky="w")

progress_label = ctk.CTkLabel(master=dashboard_frame, text="0%", font=("Arial", 12, "bold"), text_color='#FFFFFF')
progress_label.grid(row=0, column=4, padx=10, pady=10, sticky="w")

status_label = ctk.CTkLabel(master=dashboard_frame, text="Waiting", text_color="orange", font=("Arial", 12, "bold"))
status_label.grid(row=0, column=5, padx=10, pady=10, sticky="w")

canvas = Canvas(
    dashboard_frame,
    bg = "#0C0028",
    height = 930,
    width = 1721,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    351.0,
    66.0,
    image=image_image_1
)

canvas.create_text(
    56.0,
    50.0,
    anchor="nw",
    text="INSERT",
    fill="#FFFFFF",
    font=("Poppins SemiBold", 22 * -1)
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

image_image_4 = PhotoImage(
    file=relative_to_assets("image_4.png"))
image_4 = canvas.create_image(
    0.0,
    72.0,
    image=image_image_4
)

image_image_5 = PhotoImage(
    file=relative_to_assets("image_5.png"))
image_5 = canvas.create_image(
    1459.0,
    62.0,
    image=image_image_5
)

image_image_6 = PhotoImage(
    file=relative_to_assets("image_6.png"))
image_6 = canvas.create_image(
    1379.0,
    62.0,
    image=image_image_6
)

image_image_7 = PhotoImage(
    file=relative_to_assets("image_7.png"))
image_7 = canvas.create_image(
    145.0,
    304.0,
    image=image_image_7
)


image_image_8 = PhotoImage(
    file=relative_to_assets("image_8.png"))
image_8 = canvas.create_image(
    145.0,
    548.0,
    image=image_image_8
)

image_image_9 = PhotoImage(
    file=relative_to_assets("image_9.png"))
image_9 = canvas.create_image(
    377.0,
    304.0,
    image=image_image_9
)

image_image_10 = PhotoImage(
    file=relative_to_assets("image_10.png"))
image_10 = canvas.create_image(
    377.0,
    548.0,
    image=image_image_10
)

image_image_11 = PhotoImage(
    file=relative_to_assets("image_11.png"))
image_11 = canvas.create_image(
    608.0,
    304.0,
    image=image_image_11
)

image_image_12 = PhotoImage(
    file=relative_to_assets("image_12.png"))
image_12 = canvas.create_image(
    608.0,
    548.0,
    image=image_image_12
)

image_image_13 = PhotoImage(
    file=relative_to_assets("image_13.png"))
image_13 = canvas.create_image(
    1135.0,
    793.0,
    image=image_image_13
)

image_image_14 = PhotoImage(
    file=relative_to_assets("image_14.png"))
image_14 = canvas.create_image(
    145.0,
    303.0,
    image=image_image_14
)

image_image_15 = PhotoImage(
    file=relative_to_assets("image_15.png"))
image_15 = canvas.create_image(
    145.0,
    548.0,
    image=image_image_15
)

image_image_16 = PhotoImage(
    file=relative_to_assets("image_16.png"))
image_16 = canvas.create_image(
    377.0,
    303.0,
    image=image_image_16
)

image_image_17 = PhotoImage(
    file=relative_to_assets("image_17.png"))
image_17 = canvas.create_image(
    377.0,
    548.0,
    image=image_image_17
)

image_image_18 = PhotoImage(
    file=relative_to_assets("image_18.png"))
image_18 = canvas.create_image(
    609.0,
    303.0,
    image=image_image_18
)

image_image_19 = PhotoImage(
    file=relative_to_assets("image_19.png"))
image_19 = canvas.create_image(
    609.0,
    548.0,
    image=image_image_19
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

image_image_20 = PhotoImage(
    file=relative_to_assets("image_20.png"))
image_20 = canvas.create_image(
    767.0,
    126.9999999999996,
    image=image_image_20
)

image_image_21 = PhotoImage(
    file=relative_to_assets("image_21.png"))
image_21 = canvas.create_image(
    0.0,
    469.0,
    image=image_image_21
)

image_image_22 = PhotoImage(
    file=relative_to_assets("image_22.png"))
image_22 = canvas.create_image(
    672.0,
    62.0,
    image=image_image_22
)

image_image_23 = PhotoImage(
    file=relative_to_assets("image_23.png"))
image_23 = canvas.create_image(
    1142.0,
    789.0,
    image=image_image_23
)
window.resizable(False, False)
window.mainloop()
