"""
This is a slightly more complex Aviary example of running a coupled aircraft design-mission optimization.
It runs the same mission as the `run_basic_aviary_example.py` script, but it uses the AviaryProblem class to set up the problem.
This exposes more options and flexibility to the user and uses the "Level 2" API within Aviary.

We define a `phase_info` object, which tells Aviary how to model the mission.
Here we have climb, cruise, and descent phases.
We then call the correct methods in order to set up and run an Aviary optimization problem.
This performs a coupled design-mission optimization and outputs the results from Aviary into the `reports` folder.
"""
import aviary.api as av


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



prob = av.AviaryProblem()

# Load aircraft and options data from user
# Allow for user overrides here
prob.load_inputs('dornier_aircraft.csv', phase_info)

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

prob.run_aviary_problem(record_filename='do228_level2.db', suppress_solver_print=True, make_plots=True)