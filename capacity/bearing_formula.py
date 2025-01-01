#!/usr/bin/env python3
# -*- coding:
# PROGRAMMER: WL Ng
# DATE CREATED: 13 July 2024
# REVISED DATE:
# v001 Alpha 02

"""
PURPOSE:
Create different functions that return the required parameters for general bearing capacity equation.
The return values include Nc, Ngamma, Nq and other factors considering the effects of shape, inclination,
depth, sloping ground and tilting base.

The returned parameters are primarily in form of np list or panda data frame that facilitate further
computing efficiently.

"""

# sloping ground effect has not been completed yet
# rigidity factors have not been included yet

import math
import numpy as np
import pandas as pd

# Define bearing capacity factors and compute Nc, Ngamma and Nq
def bearing_f(friction, base_roughness = "Rough", slope=0):
    """
    Compute Nc, Ngamma and Nq based on 2 inputs: friction angle phi and base roughness.

    Parameters:
        friction - float value in degree.
        base_roughness - string either rough or smooth

    Returns:
        bearing_factors -  1 x 6 np array containing 3 drained parameters and 3 undrained parameters
    """
    # when friction = 0, drained parameters are not relevant.
    # 0.00001 is introduced to avoid division by zero error
    if friction == 0:
        friction += 0.00001
    fric_ra = math.radians(friction)
    slope_ra = math.radians(slope)

    Nq = math.exp(math.pi * math.tan(fric_ra)) * math.tan(math.radians(45 + friction/2))**2
    Nc_d = (Nq - 1) / math.tan(fric_ra)
    Nc_ud = float(5.14)

    if base_roughness == "Rough":
        Ngamma_d = 0.1054 * math.exp(9.6 * fric_ra)
    else:
        Ngamma_d = 0.0663 * math.exp(9.3 * fric_ra)

    # For the sloping ground case where phi = 0, a non-zero value of the term N_gamma must be used.
    if slope_ra == 0:
        Ngamma_ud = 0
    else:
        Ngamma_ud = -2 * math.sin(slope_ra)

    factor_arrays = [Nc_d, Ngamma_d, Nq, Nc_ud, Ngamma_ud, Nq]
    bearing_factors = np.round(factor_arrays,2)
    return bearing_factors

# Define rigidity factors
def rigidity_f(cohesion, friction, width, length, depth, gamma, surcharge, shear_modulus=12000):
    """
        Compute rigidity factors based on various inputs:

        Parameters:
            friction - float value in degree
            width, length, depth - float value in m
            gamma - float value in kN/m3
            surcharge - float value in kPa
            shear_modulus - float value in kPa (default value is set to 12,000 kPa)

        Returns:
            rigidity_factors -  1 x 6 np array containing 3 drained parameters and 3 undrained parameters
        """
    Nc_d = bearing_f(friction)[0]
    fric_ra = math.radians(friction)

    q_equi = surcharge + (depth+width/2) * gamma
    I_r = shear_modulus / (cohesion + q_equi * math.tan(fric_ra))
    I_rc = 0.5 * math.exp((0.33-0.45*width/length)/math.tan(math.pi/2-fric_ra/2))
    if I_r < I_rc:
        rigid_f_q = math.exp((-4.4 + 0.6 * width / length) * math.tan(fric_ra) +
                             3.07 * math.sin(fric_ra) * math.log10(2 * I_r) /
                             (1 + math.sin(fric_ra)))
        rigid_f_gamma = rigid_f_q
        rigid_f_c_d = rigid_f_q - (1 - rigid_f_q) / Nc_d / math.tan(fric_ra)
        rigid_f_c_ud = 0.32 + 0.12 * width / length + 0.6 * math.log10(I_r)
    else:
        rigid_f_q = rigid_f_gamma = rigid_f_c_d = rigid_f_c_ud = 1

    factor_arrays = [rigid_f_c_d, rigid_f_gamma, rigid_f_q, rigid_f_c_ud, rigid_f_gamma, rigid_f_q]
    rigidity_factors = np.round(factor_arrays, 3)[np.newaxis, :]
    return rigidity_factors


# Define shape factors
def shape_f(friction, width, length):
    """
        Compute shape factors based on 3 inputs: friction angle phi, width and length.

        Parameters:
            friction - float value in degree
            width - float value in m
            length - float value in m

        Returns:
            shape_factors -  1 x 6 np array containing 3 drained parameters and 3 undrained parameters
        """

    Nc_d, Nc_ud, Nq = bearing_f(friction)[0],bearing_f(friction)[3],bearing_f(friction)[2]

    # transform degrees into radians
    fric_ra = math.radians(friction)

    shape_f_c = 1 + (width / length) * (Nq / Nc_d)
    shape_f_gamma = 1 - 0.4 * (width / length)
    shape_f_q = 1 + (width / length) * math.tan(fric_ra)

    factor_arrays = [shape_f_c, shape_f_gamma, shape_f_q, shape_f_c, shape_f_gamma, shape_f_q]
    shape_factors = np.round(factor_arrays, 2)[np.newaxis, :]

    return shape_factors

# Define inclination factors
def inclination_f(vertical_load, horizontal_load_W, horizontal_load_L,
                  moment_W, moment_L, cohesion, friction, width, length):
    """
        Compute inclination factors based on 9 inputs.

        Parameters:
            vertical load - float value in kN
            horizontal_load_W - c
            horizontal_load_L - float value in kN which the load in length direction
            moment_W - float value in kNm which the moment about the axis in length direction
            moment_L - float value in kNm which the moment about the axis in width direction
            cohesion - float value in kPa
            friction - float value in degree
            width - float value in m
            length - float value in m

        Returns:
            inclination_factors -  1 x 6 np array containing 3 drained parameters and 3 undrained parameters
        """

    Nc_d, Nc_ud = bearing_f(friction)[0],bearing_f(friction)[3]

    # when friction = 0, drained parameters are not relevant.
    # 0.001 is introduced to avoid division by zero error
    if friction == 0:
        friction += 0.001

    # 0.001 is introduced to avoid division by zero error
    if vertical_load == 0:
        vertical_load += 0.001

    # transform degrees into radians
    fric_ra = math.radians(friction)

    H_load = math.sqrt(horizontal_load_L**2 + horizontal_load_W**2)

    ecc_w = round(moment_W / vertical_load, 2)
    ecc_l = round(moment_L / vertical_load,2)
    eff_width = round(width - 2 * ecc_w, 2)
    eff_length = round(length - 2 * ecc_l,2)
    eff_area = eff_width * eff_length

    # define nB and nL, note that width and length should be used instead of effective width and effective length
    if horizontal_load_L == 0:
        theta = math.pi / 2
    else:
        theta = math.atan(horizontal_load_W / horizontal_load_L)  # theta is in radians

    n_W = (2 + width / length) / (1 + width / length)
    n_L = (2 + length / width) / (1 + length / width)
    n_theta = n_L * math.cos(theta)**2 + n_W * math.sin(theta)**2

    # define inclination factors
    incl_f_q = (1 - H_load / (vertical_load + eff_area * cohesion / math.tan(fric_ra))) ** n_theta
    incl_f_gamma = (1 - H_load / (vertical_load + eff_area * cohesion / math.tan(fric_ra))) ** (n_theta + 1)

    incl_f_c_d = incl_f_q - (1 - incl_f_q) / Nc_d / math.tan(fric_ra)

    # when cohesion =0, undrained analysis is not relevant.  9999 is introduced to avoid division by zero error.
    if cohesion == 0:
        incl_f_c_ud = 9999
    else:
        incl_f_c_ud = 1 - n_theta * H_load / cohesion / Nc_ud / eff_area

    factor_arrays = [incl_f_c_d, incl_f_gamma, incl_f_q, incl_f_c_ud, incl_f_gamma, incl_f_q]
    inclination_factors = np.round(factor_arrays, 3)[np.newaxis, :]

    eff_dimensions = [eff_width, eff_length]

    return inclination_factors, eff_dimensions

# Define foundation tilt factors
def foundation_tilt_f(friction, tilt=0):
    """
        Compute foundation tilt factors based on 2 inputs: friction angle phi, tilt angle.

        Parameters:
            friction - float value in degree
            tilt - float value in degree which is the tilting angle between the base slab and the horizontal.

        Returns:
            foundation_tilt_factors -  1 x 6 np array containing 3 drained parameters and 3 undrained parameters
        """

    Nc_d = bearing_f(friction)[0]

    # when friction = 0, drained parameters are not relevant.
    # 0.001 is introduced to avoid division by zero error
    if friction == 0:
        friction += 0.001

    # transform degrees into radians
    fric_ra = math.radians(friction)
    tilt_ra = math.radians(tilt)

    tilt_f_gamma_d = (1 - tilt_ra * math.tan(fric_ra)) ** 2
    tilt_f_gamma_ud, tilt_f_q_d, tilt_f_q_ud = tilt_f_gamma_d, tilt_f_gamma_d, tilt_f_gamma_d

    tilt_f_c_d = tilt_f_q_d - (1 - tilt_f_q_d) / Nc_d / math.tan(fric_ra)
    tilt_f_c_ud = 1 - (2 * tilt_ra / 5.14)

    factor_arrays = [tilt_f_c_d, tilt_f_gamma_d, tilt_f_q_d, tilt_f_c_ud, tilt_f_gamma_ud, tilt_f_q_ud]
    foundation_tilt_factors = np.round(factor_arrays, 2)[np.newaxis, :]

    return foundation_tilt_factors

# Define surface inclination factors
def surface_slope_f(friction, slope=0):
    """
        Compute sloping ground factors based on 2 inputs: friction angle phi, slope angle.

        Parameters:
            friction - float value in degree
            slope - float value in degree which is the sloping angle of the ground surface

        Returns:
            surface_slope_factors -  1 x 6 np array containing 3 drained parameters and 3 undrained parameters
        """

    Nc_d = bearing_f(friction)[0]

    # when friction = 0, drained parameters are not relevant.
    # 0.001 is introduced to avoid division by zero error
    if friction == 0:
        friction += 0.001

    # transform degrees into radians
    fric_ra = math.radians(friction)
    slope_ra = math.radians(slope)

    slope_f_q_d = (1 - math.tan(slope_ra)) ** 2
    slope_f_q_ud = 1

    slope_f_gamma_d = slope_f_q_d
    slope_f_gamma_ud = 1

    slope_f_c_d = slope_f_q_d - (1 - slope_f_q_d) / Nc_d / math.tan(fric_ra)
    slope_f_c_ud = 1 - (2 * slope_ra / 5.14)

    factor_arrays = [slope_f_c_d, slope_f_gamma_d, slope_f_q_d, slope_f_c_ud, slope_f_gamma_ud, slope_f_q_ud]
    surface_slope_factors = np.round(factor_arrays, 2)[np.newaxis, :]

    return surface_slope_factors

# Define depth factors
def depth_f(friction, width, depth):

    """
        Compute depth factors based on 3 inputs: friction angle phi, width and length.

        Parameters:
            friction - float value in degree
            width - float value in m
            length - float value in m

        Returns:
            depth_factors -  1 x 6 np array containing 3 drained parameters and 3 undrained parameters
        """

    Nc_d = bearing_f(friction)[0]

    # when friction = 0, drained parameters are not relevant.
    # 0.001 is introduced to avoid division by zero error
    if friction == 0:
        friction += 0.001

    # transform degrees into radians
    fric_ra = math.radians(friction)

    depth_f_q = 1 + 2*math.tan(fric_ra) * (1-math.sin(fric_ra))**2 * math.atan(depth/width)
    depth_f_gamma = 1

    depth_f_c_d = depth_f_q - (1 - depth_f_q) / Nc_d / math.tan(fric_ra)
    depth_f_c_ud = 1 + 0.33 * math.atan(depth/width)

    factor_arrays = [depth_f_c_d, depth_f_gamma, depth_f_q, depth_f_c_ud, depth_f_gamma, depth_f_q]
    depth_factors = np.round(factor_arrays, 2)[np.newaxis, :]

    return depth_factors



# Define general bearing capacity equation
def bs_ultbearing(dimensions_series, soil_series, geometry_series, load_series, supplementary_series):
    """
        Compute ultimate bearing capacity based on 4 panda series.  Each series contains data of the
        foundation conditions.  Dataframes are created for quicker computation.

        Parameters:
            dimensions_series - panda dataframe containing the properties of footing dimensions
            soil_series - panda dataframe containing the properties of founding soil
            geometry_series - panda dataframe containing the properties of ground geometry
            load_series - panda dataframe containing the properties of external loads

        Returns:
            ultimate bearing capacity - float value in kPa
            effective width - float value in kN
            effective length - float value in kN
            matrix of foundation factors -  6 x 6 panda dataframe containing all required factors
        """
    # get values for various variables from four pd series
    width, length, thickness = dimensions_series
    cohesion, friction, gamma, shear_modulus = soil_series
    depth, slope, tilt, water_depth = geometry_series
    vertical_load, horizontal_load_W, horizontal_load_L, moment_W, moment_L = load_series
    surcharge, drainage, roughness = supplementary_series

    # transform degrees into radians
    fric_ra = math.radians(friction)

    wedge_depth = 0.5 * width * math.tan(math.pi/4 + fric_ra / 2)

    if water_depth >= wedge_depth:
        eff_gamma = gamma
    else:
        eff_gamma = (2 * wedge_depth - water_depth) * water_depth * gamma / wedge_depth ** 2 + \
                    (gamma - 9.81) * (wedge_depth - water_depth)**2 / wedge_depth **2


    base_roughness = roughness
    q = surcharge + depth * gamma

    bearing_factors = bearing_f(friction, base_roughness, slope)[np.newaxis, :]
    rigidity_factors = rigidity_f(cohesion, friction, width, length, depth, gamma, surcharge, shear_modulus)
    shape_factors = shape_f(friction, width, length)
    inclination_factors, eff_dimensions = inclination_f(vertical_load, horizontal_load_W, horizontal_load_L,
                                        moment_W, moment_L, cohesion, friction, width, length)
    foundation_factors = foundation_tilt_f(friction, tilt)
    surface_factors = surface_slope_f(friction, slope)
    depth_factors = depth_f(friction, width, depth)

    combined_array = np.vstack((bearing_factors, rigidity_factors, shape_factors, inclination_factors, foundation_factors,
                                surface_factors, depth_factors))

    df = pd.DataFrame(combined_array,
                      index=['Bearing factors', 'Rigidity factors', 'Shape factors', 'Inclination factors', 'Foundation tilt factors',
                             'Surface slope factors', 'Depth factors'],
                      columns=['Nc_d', 'Ngamma_d', 'Nq_d', 'Nc_ud', 'Ngamma_ud', 'Nq_ud'])

    # Product of drained factors
    c_term_d_product = df['Nc_d'].prod()
    gamma_term_d_product = df['Ngamma_d'].prod()
    q_term_d_product = df['Nq_d'].prod()

    # Product of undrained factors
    c_term_ud_product = df['Nc_ud'].prod()
    gamma_term_ud_product = df['Ngamma_ud'].prod()
    q_term_ud_product = df['Nq_ud'].prod()

    # Summation of all terms
    ult_cap_d = cohesion * c_term_d_product + 0.5 * eff_gamma * eff_dimensions[0] * gamma_term_d_product + \
                q * q_term_d_product

    ult_cap_ud = cohesion * c_term_ud_product + 0.5 * eff_gamma * eff_dimensions[0] * gamma_term_ud_product + \
                 q * q_term_ud_product

    # drop irrelevant columns based on drained or undrained condition
    if drainage == "Drained analysis":
        ult_cap = np.round(ult_cap_d, 2)
        df_output = df.drop(df.columns[3:6], axis=1)
        error_check = lambda friction: "Warning: Drained analysis is not suitable for soil with friction angle = 0 \n" \
            if friction == 0 else ""
        warning1 = error_check(friction)

    else:
        ult_cap = np.round(ult_cap_ud, 2)
        df_output = df.drop(df.columns[0:3], axis=1)
        error_check = lambda friction: "Warning: Undrained analysis is not suitable for soil with cohesion = 0 \n" \
            if cohesion == 0 else ""
        warning1 = error_check(cohesion)

    dimension_check = lambda width, length: "Warning: Length should be greater than width" \
        if width > length else ""
    warning2 = dimension_check(width, length)

    warnings = warning1 + warning2
    if warnings == "":
        warnings = "No warning message."


    capacity = f"The ultimate bearing capacity is {ult_cap} kPa"
    eff_width = f"The effective width is {eff_dimensions[0]} m"
    eff_length = f"The effective length is {eff_dimensions[1]} m"

    return warnings, capacity, eff_width, eff_length, df_output

