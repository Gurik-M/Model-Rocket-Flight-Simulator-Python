#!/usr/bin/env python

#
# CLEAR SCREEN, IMPORT MODULES SECTION
#
#clear the screen and boast about the program
import subprocess as sp
tmp =sp.call('cls',shell=True)

#import modules needed for data manipulation
import ast
import pandas
from pandas import Series
import sys

#CONSTANTS SECTION
#
# conversion factor for pounds from newtons
pounds_per_newton = 0.224809

# acceleration due to gravity
Acc_Grav = 9.8101

#
# READ DATA SECTION
#
#open the data file
data_file = open('rocsim.dat','r')

#read in the engine thrust dictionary, use ast to put in proper format
data = data_file.readline()
engine_thrust_dictionary = ast.literal_eval(data)

#create a series of thrust curve lists in newtons indexed by engine type
thrust_curve=Series(engine_thrust_dictionary)

# create a list of engines from the data in thrust curve file
engine_type = list(thrust_curve.index)

#read in the propellant mass dictionary, use ast to put in proper format
data=data_file.readline()
propellant_mass_dictionary = ast.literal_eval(data)

#close the data file
data_file.close()

#
#FUNCTIONS SECTION
#
# function for truncating elements in a list to two digits after decimal - needed when converting pounds <> newtons
def trunc(p_list):
	q_list=[int(x*100.0) for x in p_list]
	q_list=[x/100.0 for x in q_list]
	return q_list

#
#function to display the current engine types
def display_engines():	
	print("Engines: "),
	for engine in engine_type:
		print(engine),


#
# user input function
def user_input():
	print
	print("***********************************************************************************************************")
	print("*********************************** ROCKET ASCENT SIMULATOR  *******************************************")
	print ("***********************************************************************************************************")
	print("")
	while True:
		opt=input("(U)pdate engine data, (R)un new simulation or (Q)uit: ")
		if (opt in ['U','u']):
			return 'update'
			break
		if(opt in ['R','r']):
			return 'run'
			break
		if(opt in ['Q','q']):
			return 'quit'
			break
		if(not(opt in ['U','u','R','r','U','u'])):
			print("Please enter 'U' or 'R'")

#

# UPDATE DATAFILES SECTION
def update_engine():
	print
	print("***********************************************************************************************************")
	print("*********************************** UPDATE ENGINE DATA **************************************************")
	print("***********************************************************************************************************")
	print("")
	engine = input("Enter engine type:")
	if (engine in engine_type):
		print(engine, "is currently defined")
		print("Thrust curves:")
		print(thrust_curve[engine],"newtons")
		print(trunc([x* pounds_per_newton for x in thrust_curve[engine]]), "pounds")
	else:
		print(engine, "is a new engine")
	print("Enter new thrust list for engine", engine)
	while True:
		thrust_list = input("Enter list in format '[val1, val2,...,valn]': ")
		thrust_list = ast.literal_eval(thrust_list)
		if (type(thrust_list) is list):
			break
		else:
			print("please use  format '[val1, val2,...,valn]'")
	while True:
		opt = input("(N)ewtons or (P)ounds?")
		if (opt in ['N','n','P','p']):
			break
		else:
			print("please type 'N' or 'P'")
	if (opt in ['P','p']):
		thrust_list = trunc([float(x/(pounds_per_newton)) for x in thrust_list])
#	extending engine thrust dictionary to hold thrust list for this engine
	engine_thrust_dictionary[engine]=thrust_list
	if (engine in engine_type):
		print("Current propellant weight for engine",engine, "is",propellant_mass_dictionary[engine],"grams")
	propellant_mass = float(input("Enter propellant mass in grams:"))
#	extending propellant mass dictionary to hold propellant mass for this engine
	propellant_mass_dictionary[engine]=propellant_mass
#
# write data
#
#open the data file
	data_file = open('rocsim.dat','w')

#write the engine thrust dictionary
	data_file.write(str(engine_thrust_dictionary))
	data_file.write('\n')
#write the propellant mass dictionary
	data_file.write(str(propellant_mass_dictionary))
	data_file.write('\n')

#close the data file
	data_file.close()

#
# SIMULATION SECTION
#
def simulation():
	print("***********************************************************************************************************")
	print("*************************************ROCKET FLIGHT SIMULATION******************************************")
	print("***********************************************************************************************************")
	print("")

#create a series of thrust curve lists in newtons indexed by engine type
	thrust_curve=Series(engine_thrust_dictionary)

# create a list of engines from the data in thrust curve file
	engine_type = list(thrust_curve.index)

# create a series of thrust durations in tenths of a second indexed by engine type
	thrust_duration = Series([ (len(thrust_curve[x])-1) for x in engine_type], index = engine_type)


#create a series of propellant masses in grams indexed by engine type
	propellant_mass_gms =Series(propellant_mass_dictionary)

# user input for simulation
#
	empty_mass_gms=float(input("Enter rocket mass without fuel, in grams:"))

	dia_mm = float(input("Enter rocket's maximum body tube diameter, in mm:"))

# input the drag coefficient (unitless number), almost always use 0.75
	Coefficient_drag = float(input("Enter drag coefficient:"))

# input the temperature , if centigrade convert to Fahrenheit
	Temperature = int(input("Enter launch temperature: "))
	while True:
		opt = input("(F)ahrenheit or (C)entigrade: ")
		if (opt in ['F','C','f','c']):
			break
		else:
			print("Please enter 'F' or 'C'")
	if (opt in ['C','c']):
       		Temperature = int(Temperature*1.8 + 32.0)

# The following lines obtain the density of air at Temperature in Fahrenheit
	tempindex = (Temperature/5) - 6
	density_temp = [1.0590, 1.0486, 1.0380, 1.0277, 1.0177, 1.0078, 0.9980, 0.9885, 0.9792, 0.9700, 0.9610, 0.9522, 0.9435, 0.9350, 0.9266]
	#Rho = 1.2062 *density_temp[tempindex]
	Rho = 1.2062*1.2

# display engines and input the engine type
	display_engines()
	while True:

		engine = input("Enter engine type:")
		if (engine in engine_type):
			break
		else:
			print(engine, "is not an engine type.  Re-enter.")

# enable charting for engine clusters
	Engine_quantity = int(input("Enter number of engines:"))
#
# SIMULATION SETUP
#
	Thrust_curve = [(x * Engine_quantity) for x in thrust_curve[engine]]

# total propellant mass in kg, note must multiply by number of engines
	Propellant_mass_kg = Engine_quantity * 0.001 * propellant_mass_gms[engine]

# thrust duration in 1/10 seconds
	Thrust_duration = thrust_duration[engine]

# mass of rocket plus empty engine casing in kilograms
	Empty_mass_kg = 0.001 * empty_mass_gms

# total mass of rocket with propellant in kilograms
	Total_mass_kg = Empty_mass_kg + Propellant_mass_kg 


# diameter of rocket in meters
	Dia_meters = 0.001 * dia_mm

# incremental loss of mass, in kg, in one tenth second
	Mass_dec = Propellant_mass_kg / Thrust_duration

# aerodynamic drag value, proportional to air density and cross-sectional area of rocket
	Drag_Value = 0.5 * Rho * 3.1416 * Coefficient_drag*((Dia_meters/2.0)**2)

#
# INITIALIZE SIMULATION LOOP VARIABLES
#
	Acceleration = 0.0
	Velocity = 0.0
	Altitude = 0.0
	interval = 0
	g = 0
	Max_velocity = 0.0
	print('Time\tHeight\tSpeed\tdelta-V\tGees\tMass')
#

# simulation main loop
#
	while(Velocity >= 0):
		g = Acceleration/Acc_Grav
		Time=interval * 0.1
		interval +=1
		if (interval<=Thrust_duration):
			FwdForce = Thrust_curve[interval]
		else:
			FwdForce = 0
		NetForce = FwdForce-(Acc_Grav*Total_mass_kg)-(Drag_Value*(Velocity**2))
		Acceleration = NetForce/Total_mass_kg
		Velocity += Acceleration * 0.1
		if (Velocity > Max_velocity):
			Max_velocity = Velocity
		Altitude += Velocity * 0.1
		if (interval <= Thrust_duration):
			Total_mass_kg -=  Mass_dec
		else:
			Total_mass_kg= Empty_mass_kg

#-1.0002839875624807
#
# simulation report summary

	rocket_mass_kg = empty_mass_gms/1000
	print("")
	print('For vehicle weighing', empty_mass_gms, 'grams,', 'diameter', dia_mm, 'millimeters, at', Temperature,'degrees F,')
	print('using', Engine_quantity, engine,'engine(s), assuming a', Coefficient_drag, 'coefficient of drag:')
	print('\tMaximum altitude = %.2f meters, = %.2f feet'%(Altitude, 3.2808*Altitude))
	print('\tMaximum velocity = %.2f m/s, = %.2f mi/hr'%(Max_velocity, 2.237*Max_velocity))
	print('\tRecommended delay = %.2f seconds'%(Time - Thrust_duration/10.0))
	print('\tGravitational Force(N) = ', rocket_mass_kg*9.81)

	print('\tUpward Force(N) = ', rocket_mass_kg*(Max_velocity/Thrust_duration))
	print('\tNet Force(N) = ', (rocket_mass_kg*(Max_velocity/Time))- rocket_mass_kg*9.81)
	print('\tAerodynamic Drag Value = ', Drag_Value)

	print("")
#
# MAIN LOOP SECTION

user_selection=user_input()
if user_selection == 'update':
	update_engine()
if user_selection=='run':
	simulation()
if user_selection=='quit':
    sys.exit()

