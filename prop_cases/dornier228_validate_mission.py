# -*- coding: utf-8 -*-
"""
Dornier228
"""

from aviary.api import Aircraft, Mission
import aviary.api as av
import numpy as np
import math

# Since I was getting NAN values, I adjusted rounding function to handle NaN and infinite values
def round_it(x):
    if math.isnan(x) or math.isinf(x):
        return 'NaN'  # Handle NaN and infinity gracefully
    sig = len(str(int(x))) + 2
    return round(x, sig)

# Phase information for mission setup from opensource data as in csv
phase_info = {
    "pre_mission": {"include_takeoff": False, "optimize_mass": True},
    "climb_1": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "optimize_mach": False,
            "optimize_altitude": False,
            "polynomial_control_order": 1,
            "use_polynomial_control": True,
            "num_segments": 3,
            "order": 3,
            "solve_for_distance": False,
            "initial_mach": (0.1, "unitless"),
            "final_mach": (0.38, "unitless"),
            "mach_bounds": ((0.08, 0.4), "unitless"),
            "initial_altitude": (0.0, "ft"),
            "final_altitude": (25000.0, "ft"),
            "altitude_bounds": ((0.0, 25500.0), "ft"),
            "throttle_enforcement": "path_constraint",
            "fix_initial": True,
            "constrain_final": False,
            "fix_duration": False,
            "initial_bounds": ((0.0, 0.0), "min"),
            "duration_bounds": ((10.0, 30.0), "min"),
        },
        "initial_guesses": {"time": ([0.0, 20.0], "min")},
    },
    "cruise_1": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "optimize_mach": False,
            "optimize_altitude": False,
            "polynomial_control_order": 1,
            "use_polynomial_control": True,
            "num_segments": 3,
            "order": 3,
            "solve_for_distance": False,
            "initial_mach": (0.38, "unitless"),
            "final_mach": (0.38, "unitless"),
            "mach_bounds": ((0.36, 0.4), "unitless"),
            "initial_altitude": (25000.0, "ft"),
            "final_altitude": (25000.0, "ft"),
            "altitude_bounds": ((24500.0, 25500.0), "ft"),
            "throttle_enforcement": "boundary_constraint",
            "fix_initial": False,
            "constrain_final": False,
            "fix_duration": False,
            "initial_bounds": ((10.0, 30.0), "min"),
            "duration_bounds": ((100.0, 300.0), "min"),
        },
        "initial_guesses": {"time": ([20.0, 200.0], "min")},
    },
    "descent_1": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "optimize_mach": False,
            "optimize_altitude": False,
            "polynomial_control_order": 1,
            "use_polynomial_control": True,
            "num_segments": 3,
            "order": 3,
            "solve_for_distance": False,
            "initial_mach": (0.38, "unitless"),
            "final_mach": (0.1, "unitless"),
            "mach_bounds": ((0.08, 0.4), "unitless"),
            "initial_altitude": (25000.0, "ft"),
            "final_altitude": (1500.0, "ft"),
            "altitude_bounds": ((1000.0, 25500.0), "ft"),
            "throttle_enforcement": "path_constraint",
            "fix_initial": False,
            "constrain_final": True,
            "fix_duration": False,
            "initial_bounds": ((110.0, 330.0), "min"),
            "duration_bounds": ((10.0, 30.0), "min"),
        },
        "initial_guesses": {"time": ([220.0, 20.0], "min")},
    },
    "post_mission": {
        "include_landing": False,
        "constrain_range": True,
        "target_range": (214, "nmi"),
    },
}



aircraft_filename = "dornier_aircraft.csv"
optimizer = "IPOPT"
analysis_scheme = av.AnalysisScheme.COLLOCATION
objective_type = "fuel_burned"
record_filename = 'aviary_history.db'
restart_filename = None
max_iter = 500


prob = av.AviaryProblem(analysis_scheme)


prob.load_inputs(aircraft_filename, phase_info)
prob.check_and_preprocess_inputs()


prob.add_pre_mission_systems()
prob.add_phases()
prob.add_post_mission_systems()

# Link phases and set up driver and design variables
prob.link_phases()
prob.add_driver(optimizer, max_iter=max_iter)
prob.add_design_variables()


prob.add_objective(objective_type=objective_type)


prob.setup()
prob.set_initial_guesses()


# Debug NaN/Inf values in inputs/outputs
print("Checking for NaN/Inf in inputs and outputs...")
for name, meta in prob.model.list_inputs(val=True):
    val = meta['val']
    if np.any(np.isnan(val)) or np.any(np.isinf(val)):
        print(f"NaN or Inf detected in input: {name} - {val}")

for name, meta in prob.model.list_outputs(val=True):
    val = meta['val']
    if np.any(np.isnan(val)) or np.any(np.isinf(val)):
        print(f"NaN or Inf detected in output: {name} - {val}")


# Run the model without optimizer to verify no NaN values are propagated
print("Running model without optimizer to check for NaN propagation.")
prob.run_model()

# Check for NaN values in outputs after running the model
print("Checking outputs for NaN values:")
outputs = prob.model.list_outputs(val=True)
for name, meta in outputs:
    val = meta['val']
    if np.any(np.isnan(val)):
        print(f"NaN detected in output: {name} - {val}")

# Run the optimization problem with recording enabled
try:
    prob.run_aviary_problem(record_filename, restart_filename=restart_filename, make_plots=True)
except ValueError as e:
    print("Error during optimization run:", e)

# Output results if available
try:
    print("Fuel Mass:", prob.get_val(Mission.Design.FUEL_MASS, units='lbm'))
    print("Total Fuel Mass:", prob.get_val(Mission.Summary.TOTAL_FUEL_MASS, units='lbm'))

    # Check fuel burned in various units
    fuel_burned_kg = prob.get_val(Mission.Summary.FUEL_BURNED, units='kg')[0]
    fuel_burned_lb = prob.get_val(Mission.Summary.FUEL_BURNED, units='lb')[0]
    print(f'The optimization objective "fuel burned" is: {fuel_burned_kg} kg / {fuel_burned_lb} lb')
except Exception as e:
    print("Error retrieving final values:", e)
