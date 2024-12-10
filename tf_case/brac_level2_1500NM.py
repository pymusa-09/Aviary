# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 15:10:07 2024

@author: umroot
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 22:26:24 2024

@author: User
"""

import aviary.api as av
#from brac_phase_info import phase_info
import openmdao.api as om
import sqlite3
import pandas as pd

# Define phase information, adding aerodynamic variables to output
phase_info = {
    "climb_1": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "optimize_mach": False,
            "optimize_altitude": False,
            "num_segments": 5,
            "order": 3,
            "solve_for_distance": False,
            "initial_altitude": (1500.0, "ft"),
            "final_altitude": (10000.0, "ft"),
            "altitude_bounds": ((1500.0, 12000.0), "ft"),
            "initial_mach": (0.387976423, "unitless"),
            "final_mach": (0.452235439, "unitless"),
            "mach_bounds": ((0.37, 0.46), "unitless"),
            "throttle_enforcement": "boundary_constraint",
            "fix_initial": False,
            "constrain_final": False,
            "fix_duration": False,
            "initial_bounds": ((0.0, 11.0), "min"),
            "duration_bounds": ((10.0, 13.0), "min"),
        },
        "initial_guesses": {"time": ([0.0, 11.0], "min")},
    },
    "climb_2": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "optimize_mach": False,
            "optimize_altitude": False,
            "num_segments": 7,
            "order": 3,
            "solve_for_distance": False,
            "initial_altitude": (10000.0, "ft"),
            "final_altitude": (41000.0, "ft"),
            "altitude_bounds": ((9500.0, 42000.0), "ft"),
            "initial_mach": (0.452235439, "unitless"),
            "final_mach": (0.75, "unitless"),
            "mach_bounds": ((0.45, 0.77), "unitless"),
            "throttle_enforcement": "boundary_constraint",
            "fix_initial": False,
            "constrain_final": False,
            "fix_duration": False,
            "initial_bounds": ((11.0, 20.0), "min"),
            "duration_bounds": ((20.0, 25.0), "min"),
        },
        "initial_guesses": {"time": ([11.0, 20.0], "min")},
    },
    "cruise_accel": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "optimize_mach": False,
            "optimize_altitude": False,
            "num_segments": 5,
            "order": 3,
            "solve_for_distance": False,
            "initial_altitude": (41000.0, "ft"),
            "final_altitude": (41000.0, "ft"),
            "altitude_bounds": ((40000.0, 42000.0), "ft"),
            "initial_mach": (0.75, "unitless"),
            "final_mach": (0.8, "unitless"),
            "mach_bounds": ((0.74, 0.82), "unitless"),
            "throttle_enforcement": "boundary_constraint",
            "fix_initial": False,
            "constrain_final": False,
            "fix_duration": False,
            "initial_bounds": ((20.0, 25.0), "min"),
            "duration_bounds": ((25.0, 30.0), "min"),
        },
        "initial_guesses": {"time": ([20.0, 25.0], "min")},
    },
    "cruise_1": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "optimize_mach": False,
            "optimize_altitude": False,
            "num_segments": 10,
            "order": 3,
            "solve_for_distance": True,
            "initial_altitude": (41000.0, "ft"),
            "final_altitude": (41000.0, "ft"),
            "altitude_bounds": ((40500.0, 41500.0), "ft"),
            "initial_mach": (0.8, "unitless"),
            "final_mach": (0.8, "unitless"),
            "mach_bounds": ((0.78, 0.82), "unitless"),
            "throttle_enforcement": "path_constraint",
            "fix_initial": False,
            "constrain_final": False,
            "fix_duration": False,
            "initial_bounds": ((30.0, 120.0), "min"),
            "duration_bounds": ((120.0, 240.0), "min"),  # Adjusted for ~3.24 hours
        },
        "initial_guesses": {"time": ([30.0, 120.0], "min")},
    },
    "descent_1": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "optimize_mach": False,
            "optimize_altitude": False,
            "num_segments": 7,
            "order": 3,
            "solve_for_distance": False,
            "initial_altitude": (41000.0, "ft"),
            "final_altitude": (10000.0, "ft"),
            "altitude_bounds": ((40500.0, 11000.0), "ft"),
            "initial_mach": (0.75, "unitless"),
            "final_mach": (0.452235439, "unitless"),
            "mach_bounds": ((0.45, 0.77), "unitless"),
            "throttle_enforcement": "path_constraint",
            "fix_initial": False,
            "constrain_final": False,
            "fix_duration": False,
            "initial_bounds": ((120.0, 150.0), "min"),
            "duration_bounds": ((150.0, 180.0), "min"),
        },
        "initial_guesses": {"time": ([120.0, 150.0], "min")},
    },
    "descent_2": {
        "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
        "user_options": {
            "optimize_mach": False,
            "optimize_altitude": False,
            "num_segments": 7,
            "order": 3,
            "solve_for_distance": False,
            "initial_altitude": (10000.0, "ft"),
            "final_altitude": (1500.0, "ft"),
            "altitude_bounds": ((9500.0, 2000.0), "ft"),
            "initial_mach": (0.387976423, "unitless"),
            "final_mach": (0.387976423, "unitless"),
            "mach_bounds": ((0.35, 0.41), "unitless"),
            "throttle_enforcement": "path_constraint",
            "fix_initial": False,
            "constrain_final": False,
            "fix_duration": False,
            "initial_bounds": ((180.0, 200.0), "min"),
            "duration_bounds": ((200.0, 220.0), "min"),
        },
        "initial_guesses": {"time": ([180.0, 200.0], "min")},
    },
    "post_mission": {
        "include_landing": False,
        "constrain_range": True,
        "target_range": (1500, "nmi"),
    },
}


prob = av.AviaryProblem()

# Load aircraft and options data from user
# Allow for user overrides here
prob.load_inputs('brac_aircraft.csv', phase_info)

prob.check_and_preprocess_inputs()

prob.add_pre_mission_systems()

prob.add_phases()

prob.add_post_mission_systems()

# Link phases and variables
prob.link_phases()

prob.add_driver("SLSQP", max_iter=1000)

prob.add_design_variables()

prob.add_objective(objective_type="mass", ref=-1e5)

prob.setup()

prob.set_initial_guesses()

prob.run_aviary_problem(record_filename='brac_level2.db', suppress_solver_print=True, make_plots=True)