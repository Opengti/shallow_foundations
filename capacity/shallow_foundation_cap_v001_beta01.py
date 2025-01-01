import os
import logging
from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from bearing_formula import *
from savepdf import *


logging.basicConfig(filename='error.log', level=logging.DEBUG)

class BearingCalculation(Frame):
    """PURPOSE:
    Create a tkinter framework to get parameters from users and call bearing_formula module to calculate the
    ultimate bearing capacity.  Form 4 pandas series: Dimensions series, soil series, geometry series and load series.
    Pass these 4 series to bearing_formula and obtain the calculation results.
    Display the calculation results in text box.
    """

    def __init__(self, master):
        """Initialize Frame"""
        super(BearingCalculation, self).__init__(master)
        self.grid()
        self.foundation_parameter()



    def foundation_parameter(self):
        # Create title for the frame
        Label(self, text="Ultimate Bearing Capacity").grid(row=0, column=0, padx=10, sticky=W)
        Label(self, text="\t").grid(row=1, column=0, sticky=W)
        Label(self, text="\t").grid(row=1, column=1, sticky=W)
        Label(self, text="\t").grid(row=1, column=2, sticky=W)
        Label(self, text="\t").grid(row=1, column=3, sticky=W)
        Label(self, text="\t").grid(row=1, column=4, sticky=W)
        Label(self, text="\t").grid(row=1, column=6, sticky=W)

        self.project = Label(self, text="Project Name:")
        self.project.grid(row=2, column=0, padx=10, sticky=W)
        self.project_ent = Entry(self, width=60)
        self.project_ent.grid(row=2, column=1, columnspan=4, padx=10, sticky=W)

        self.projectID = Label(self, text="Project No.:")
        self.projectID.grid(row=3, column=0, padx=10, sticky=W)
        self.projectID_ent = Entry(self, width=60)
        self.projectID_ent.grid(row=3, column=1, columnspan=4, padx=10, sticky=W)

        self.foundationID = Label(self, text="Foundation ID:")
        self.foundationID.grid(row=4, column=0, padx=10, sticky=W)
        self.foundationID_ent = Entry(self, width=60)
        self.foundationID_ent.grid(row=4, column=1, columnspan=4, padx=10, sticky=W)

        Label(self, text=" ").grid(row=5, column=0, sticky=W)

        row_i = 6

        # Input footing dimensions
        Label(self, text="Footing dimensions:").grid(row=row_i, column=0, padx=10, sticky=W)

        self.item_w = Label(self, text="Width, W (m)")
        self.item_w.grid(row=row_i+1, column=0, padx=10, sticky=W)
        self.item_w_ent = Entry(self, width=20)
        self.item_w_ent.grid(row=row_i+2, column=0, padx=10, sticky=W)
        self.item_w_ent.insert(2, "2")

        self.item_l = Label(self, text="Length, L (m)")
        self.item_l.grid(row=row_i+1, column=2, padx=10, sticky=W)
        self.item_l_ent = Entry(self)
        self.item_l_ent.grid(row=row_i+2, column=2, padx=10, sticky=W)
        self.item_l_ent.insert(3, "3")

        self.item_th = Label(self, text="Thickness, df (m)")
        self.item_th.grid(row=row_i+1, column=4, padx=10, sticky=W)
        self.item_th_ent = Entry(self)
        self.item_th_ent.grid(row=row_i+2, column=4, padx=10, sticky=W)
        self.item_th_ent.insert(0, "0")

        Label(self, text=" ").grid(row=row_i+3, column=0, sticky=W)

        # Input shear strength parameters of the founding soil
        row_j = row_i+4
        Label(self, text="Soil parameters:").grid(row=row_j, column=0, padx=10, sticky=W)

        self.item_c = Label(self, text="Cohesion, c'/Su (kPa)")
        self.item_c.grid(row=row_j+1, column=0, padx=10, sticky=W)
        self.item_c_ent = Entry(self)
        self.item_c_ent.grid(row=row_j+2, column=0, padx=10, sticky=W)
        self.item_c_ent.insert(0, "0")

        self.item_f = Label(self, text="Friction Angle (deg)")
        self.item_f.grid(row=row_j+1, column=2, padx=10, sticky=W)
        self.item_f_ent = Entry(self)
        self.item_f_ent.grid(row=row_j+2, column=2, padx=10, sticky=W)
        self.item_f_ent.insert(30, "30")

        self.item_g = Label(self, text="Bulk Unit Weight (kN/m3)")
        self.item_g.grid(row=row_j+1, column=4, padx=10, sticky=W)
        self.item_g_ent = Entry(self)
        self.item_g_ent.grid(row=row_j+2, column=4, padx=10, sticky=W)
        self.item_g_ent.insert(20, "20")

        Label(self, text="").grid(row=row_j+3, column=0, padx=10, sticky=W)

        self.item_sh = Label(self, text="Shear Modulus (kPa)")
        self.item_sh.grid(row=row_j+4, column=0, padx=10, sticky=W)
        self.item_sh_ent = Entry(self)
        self.item_sh_ent.grid(row=row_j+5, column=0, padx=10, sticky=W)
        self.item_sh_ent.insert(12000, "12000")

        # Create a drop down list for undrained or drained analysis
        self.item_analysis = Label(self, text="Drainage condition")
        self.item_analysis.grid(row=row_j+4, column=2, padx=10, sticky=W)
        self.dropdown_var = tk.StringVar(self)
        self.items = ["Drained analysis", "Undrained Analysis"]
        self.dropdown = ttk.Combobox(self, textvariable=self.dropdown_var, values=self.items)
        self.dropdown.set("Choose condition")
        self.dropdown.bind("<<ComboboxSelected>>", self.on_select)
        self.dropdown.grid(row=row_j+5, column=2, padx=10, pady=0)

        Label(self, text=" ").grid(row=row_j+6, column=0, padx=10, sticky=W)

        # Input geometry
        row_k = row_j + 7
        Label(self, text="Geometry:").grid(row=row_k, column=0, padx=10, sticky=W)

        self.item_d = Label(self, text="Embedment depth, Df (m)")
        self.item_d.grid(row=row_k+1, column=0, padx=10, sticky=W)
        self.item_d_ent = Entry(self)
        self.item_d_ent.grid(row=row_k+2, column=0, padx=10, sticky=W)
        self.item_d_ent.insert(0, "0")

        self.item_slope = Label(self, text="Ground sloping angle (deg)")
        self.item_slope.grid(row=row_k+1, column=2, padx=10, sticky=W)
        self.item_slope_ent = Entry(self)
        self.item_slope_ent.grid(row=row_k+2, column=2, padx=10, sticky=W)
        self.item_slope_ent.insert(0, "0")

        self.item_tilt = Label(self, text="Base tilt angle (deg)")
        self.item_tilt.grid(row=row_k+1, column=4, padx=10, sticky=W)
        self.item_tilt_ent = Entry(self)
        self.item_tilt_ent.grid(row=row_k+2, column=4, padx=10, sticky=W)
        self.item_tilt_ent.insert(0, "0")

        Label(self, text=" ").grid(row=row_k + 3, column=0, sticky=W)

        self.item_water = Label(self, text="Water depth, Dw (m)")
        self.item_water.grid(row=row_k+4, column=0, padx=10, sticky=W)
        self.item_water_ent = Entry(self)
        self.item_water_ent.grid(row=row_k+5, column=0, padx=10, sticky=W)
        self.item_water_ent.insert(0, "0")

        # Create a drop down list for roughness
        self.item_base = Label(self, text="Base roughness")
        self.item_base.grid(row=row_k+4, column=2, padx=10, sticky=W)
        self.dropdown_var1 = tk.StringVar(self)
        self.item1 = ["Rough", "Smooth"]
        self.dropdown = ttk.Combobox(self, textvariable=self.dropdown_var1, values=self.item1)
        self.dropdown.set("Choose roughness")
        self.dropdown.bind("<<ComboboxSelected>>", self.on_select)
        self.dropdown.grid(row=row_k+5, column=2, padx=0, pady=0)

        Label(self, text=" ").grid(row=row_k+6, column=0, sticky=W)

        # Input loading including lateral loads and moments

        row_l = row_k+7
        Label(self, text="Loadings:").grid(row=row_l, column=0, padx=10, sticky=W)
        self.item_N = Label(self, text="Vertical Load, N (kN)")
        self.item_N.grid(row=row_l+1, column=0, padx=10, sticky=W)
        self.item_N_ent = Entry(self)
        self.item_N_ent.grid(row=row_l+2, column=0, padx=10, sticky=W)
        self.item_N_ent.insert(0, "0")

        self.item_H_W = Label(self, text="Horizontal Load along width, \nHx (kN)", anchor="w", justify="left")
        self.item_H_W.grid(row=row_l + 1, column=2, padx=10, sticky=W)
        self.item_H_W_ent = Entry(self)
        self.item_H_W_ent.grid(row=row_l + 2, column=2, padx=10, sticky=W)
        self.item_H_W_ent.insert(0, "0")

        self.item_H_L = Label(self, text="Horizontal Load along length, \nHy (kN)", anchor="w", justify="left")
        self.item_H_L.grid(row=row_l + 1, column=4, padx=10, sticky=W)
        self.item_H_L_ent = Entry(self)
        self.item_H_L_ent.grid(row=row_l + 2, column=4, padx=10, sticky=W)
        self.item_H_L_ent.insert(0, "0")

        Label(self, text=" ").grid(row=row_l + 3, column=0, sticky=W)

        self.item_q = Label(self, text="Surface Surcharge, Q (kPa)")
        self.item_q.grid(row=row_l+4, column=0, padx=10, sticky=W)
        self.item_q_ent = Entry(self)
        self.item_q_ent.grid(row=row_l+5, column=0, padx=10, sticky=W)
        self.item_q_ent.insert(0, "0")

        self.item_M_W = Label(self, text="Moment about L axis, \nMy (kNm)", anchor="w", justify="left")
        self.item_M_W.grid(row=row_l + 4, column=2, padx=10, sticky=W)
        self.item_M_W_ent = Entry(self)
        self.item_M_W_ent.grid(row=row_l + 5, column=2, padx=10, sticky=W)
        self.item_M_W_ent.insert(0, "0")

        self.item_M_L = Label(self, text="Moment about W axis, \nMx (kNm)", anchor="w", justify="left")
        self.item_M_L.grid(row=row_l + 4, column=4, padx=10, sticky=W)
        self.item_M_L_ent = Entry(self)
        self.item_M_L_ent.grid(row=row_l + 5, column=4, padx=10, sticky=W)
        self.item_M_L_ent.insert(0, "0")


        row_n = row_l+6
        Label(self, text=" ").grid(row=row_n, column=0, sticky=W)

        self.calbttn = Button(self, text="Calculate", command=self.bearing_capacity)
        self.calbttn.grid(row=row_n+1, column=0, padx=10, sticky=W)

        self.pdf = Button(self, text="Print pdf", command=self.create_pdf)
        self.pdf.grid(row=row_n+1, column=2, padx=10, sticky=W)

        Label(self, text=" ").grid(row=row_n+2, column=0, sticky=W)
        Label(self, text=" ").grid(row=row_n+3, column=0, sticky=W)

        self.results_box1 = Text(self, width=60, height=15, wrap=WORD)
        self.results_box1.grid(row=1, column=6, rowspan=12, columnspan=4, padx=10, sticky=W)



        # Add images to explain the input parameters
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path1 = os.path.join(current_dir, "images", "footing_1.jpg")
        image_path2 = os.path.join(current_dir, "images", "footing_2.jpg")
        image_path3 = os.path.join(current_dir, "images", "icon.jpg")

        self.image1 = Image.open(image_path1)
        self.image2 = Image.open(image_path2)
        self.image3 = Image.open(image_path3)

        # Resize the image
        new_width = 400  # Set your desired width
        new_height = 200  # Set your desired height
        self.image1 = self.image1.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.image2 = self.image2.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.image3 = self.image3.resize((60, 50), Image.Resampling.LANCZOS)

        self.photo1 = ImageTk.PhotoImage(self.image1)
        self.image_label1 = Label(self, image=self.photo1)
        self.image_label1.grid(row=13, column=6, rowspan=12, padx=10, pady=0, sticky=W)
        #
        self.photo2 = ImageTk.PhotoImage(self.image2)
        self.image_label2 = Label(self, image=self.photo2)
        self.image_label2.grid(row=24, column=6, rowspan=12, padx=10, pady=0, sticky=W)
        #
        self.photo3 = ImageTk.PhotoImage(self.image3)
        self.image_label3 = Label(self, image=self.photo3)
        self.image_label3.grid(row=0, column=5, padx=5, pady=0)


    # Assign drop down selection
    def on_select(self, event):
        self.analysis_condition = self.dropdown_var.get()
        self.roughness = self.dropdown_var1.get()

    # Calculate the ultimate bearing capacity
    # Numpy series dimensions_series, soil_series, geometry_series, load_series, supplementary_series are prepared.

    def bearing_capacity(self):
        try:
            self.title_list = [self.project_ent.get(), self.projectID_ent.get(), self.foundationID_ent.get()]

            # Create dimensions series for the footing
            width = float(self.item_w_ent.get())
            length = float(self.item_l_ent.get())
            thickness = float(self.item_th_ent.get())

            values_d = [width, length, thickness]
            indices_d = ['Width, W (m)', 'Length, L (m)', 'Thickness, df (m)']
            self.dimensions_series = pd.Series(values_d, index=indices_d)

            # Create soil series for the founding soil
            cohesion = float(self.item_c_ent.get())
            friction = float(self.item_f_ent.get())
            gamma = float(self.item_g_ent.get())
            shear_modulus = float(self.item_sh_ent.get())

            values_s = [cohesion, friction, gamma, shear_modulus]
            indices_s = ['Cohesion, c or su (kPa)', 'Friction Angle (deg)', 'Bulk Unit Weight (kN/m3)', 'Shear Modulus (kPa)']
            self.soil_series = pd.Series(values_s, index=indices_s)

            # Create geometry series
            depth = float(self.item_d_ent.get())
            slope = float(self.item_slope_ent.get())
            tilt = float(self.item_tilt_ent.get())
            water_depth = float(self.item_water_ent.get())

            values_g = [depth, slope, tilt, water_depth]
            indices_g = ['Depth, Df (m)', 'Ground Slope (deg)', 'Tilt Angle (deg)', 'Water Depth, Dw (m)']
            self.geometry_series = pd.Series(values_g, index=indices_g)

            # Create load series
            vertical_load = float(self.item_N_ent.get())
            horizontal_load_W, horizontal_load_L = float(self.item_H_W_ent.get()), float(self.item_H_L_ent.get())
            moment_W, moment_L = float(self.item_M_W_ent.get()), float(self.item_M_L_ent.get())
            surcharge = float(self.item_q_ent.get())
            drainage = self.analysis_condition
            roughness =self.roughness

            values_l = [vertical_load, horizontal_load_W, horizontal_load_L, moment_W, moment_L]
            indices_l = ['Vertical Load, N (kN)', 'Horizontal load Hx (kN)', 'Horizontal Load Hy (kN)',
                        'Moment Mx (kNm)', 'Moment My (kNm)']
            self.load_series = pd.Series(values_l, index=indices_l)

            # Create supplementary series
            values_supple = [surcharge, drainage, roughness]
            indices_supple = ['Surface surcharge (kPa)', 'Drainage Condition',
                         'Base roughness']
            self.supplementary_series = pd.Series(values_supple, index=indices_supple)

            # get returns from the bearing functions

            display1, display2, display3, display4, self.factor_table = \
                bs_ultbearing(self.dimensions_series, self.soil_series, self.geometry_series, self.load_series, self.supplementary_series)

            self.message_0 = f"{display1}\n\n{display2}\n{display3}\n{display4}\n\n{self.factor_table}"
            self.message_1 = f"{display1}<br/><br/>{display2}<br/>{display3}<br/>{display4}"


            self.results_box1.delete(0.0, END)
            self.results_box1.insert(0.0, self.message_0)

        except Exception as e:
            logging.exception("An error occurred: ")



    def create_pdf(self):
        compile_content_page(self.dimensions_series, self.soil_series, self.geometry_series, self.load_series, self.factor_table, self.title_list, self.message_1)
        prepare_frontpage(self.title_list)
        filename = "bearing_report_"+str(self.title_list[2])
        combine_pdf(filename, "reports/temp_frontpage", "reports/content_page")





root = Tk()
root.title("Ultimate Bearing Capacity of Shallow Foundations according to BS 8004:2015")
root.geometry("1680x1024")
app = BearingCalculation(root)

root.mainloop()
