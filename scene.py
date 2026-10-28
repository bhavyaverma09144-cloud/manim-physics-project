from manim import *
import numpy as np
from scipy.integrate import solve_ivp

class DoublePendulumSimulation(Scene):
    def construct(self):
        # --- 1. PHYSICAL PARAMETERS & CONFIGURATION ---
        g = 9.81       # Acceleration due to gravity (m/s^2)
        L1 = 2.0       # Length of first pendulum rod
        L2 = 2.0       # Length of second pendulum rod
        m1 = 1.0       # Mass of first bob
        m2 = 1.0       # Mass of second bob

        # Initial conditions: 60 degrees (-pi/3 radians) from the downward vertical on the left
        theta1_init = -np.pi / 3
        theta2_init = -np.pi / 3
        omega1_init = 0.0
        omega2_init = 0.0

        t_max = 20.0   # Duration in seconds
        fps = 60       # Frames per second
        t_eval = np.linspace(0, t_max, int(t_max * fps))

        # --- 2. LAGRANGIAN EQUATIONS OF MOTION ---
        def derivatives(t, y):
            th1, w1, th2, w2 = y
            d = th2 - th1
            
            # Denominator for both angular accelerations
            den = L1 * (2 * m1 + m2 - m2 * np.cos(2 * th1 - 2 * th2))
            
            # Angular acceleration 1 (dw1/dt)
            num1 = (-g * (2 * m1 + m2) * np.sin(th1) 
                    - m2 * g * np.sin(th1 - 2 * th2) 
                    - 2 * np.sin(d) * m2 * (w2**2 * L2 + w1**2 * L1 * np.cos(d)))
            dw1 = num1 / den

            # Angular acceleration 2 (dw2/dt)
            num2 = (2 * np.sin(d) * (w1**2 * L1 * (m1 + m2) 
                    + g * (m1 + m2) * np.cos(th1) 
                    + w2**2 * L2 * m2 * np.cos(d)))
            dw2 = num2 / den

            return [w1, dw1, w2, dw2]

        # Solve ODEs numerically
        sol = solve_ivp(
            derivatives, 
            [0, t_max], 
            [theta1_init, omega1_init, theta2_init, omega2_init], 
            t_eval=t_eval,
            method='RK45',
            rtol=1e-9,
            atol=1e-9
        )
        
        theta1 = sol.y[0]
        theta2 = sol.y[2]

        # Convert polar coordinates to Cartesian coordinates
        x1 = L1 * np.sin(theta1)
        y1 = -L1 * np.cos(theta1)
        x2 = x1 + L2 * np.sin(theta2)
        y2 = y1 - L2 * np.cos(theta2)

        # --- 3. MANIM SCENE SETUP ---
        pivot = ORIGIN
        
        # Initial positions
        p1_init = np.array([x1[0], y1[0], 0])
        p2_init = np.array([x2[0], y2[0], 0])

        # Create pendulum graphical elements
        rod1 = Line(pivot, p1_init, stroke_width=5, color=BLUE_C)
        rod2 = Line(p1_init, p2_init, stroke_width=5, color=TEAL_C)
        
        ball1 = Circle(radius=0.15, color=BLUE_E, fill_opacity=1).move_to(p1_init)
        ball2 = Circle(radius=0.18, color=YELLOW_C, fill_opacity=1).move_to(p2_init)
        pivot_dot = Circle(radius=0.08, color=WHITE, fill_opacity=1).move_to(pivot)

        pendulum_group = VGroup(rod1, rod2, ball1, ball2, pivot_dot)

        # Glowing trailing path for the tip mass (ball2)
        traced_path = TracedPath(
            ball2.get_center, 
            stroke_color=YELLOW_E, 
            stroke_width=3, 
            stroke_opacity=[0, 0.8], 
            dissipating_time=3.0
        )

        # Title / Info overlay
        title = Text("Chaos: Double Pendulum", font_size=28, color=LIGHT_GRAY).to_corner(UL)
        self.add(title)

        # --- 4. ANIMATION & UPDATER LOGIC ---
        time_tracker = ValueTracker(0.0)

        def update_pendulum(mob):
            t = time_tracker.get_value()
            # Map time to pre-computed trajectory index
            idx = int(t * fps)
            if idx >= len(t_eval):
                idx = len(t_eval) - 1
            
            curr_p1 = np.array([x1[idx], y1[idx], 0])
            curr_p2 = np.array([x2[idx], y2[idx], 0])
            
            rod1.put_start_and_end_on(pivot, curr_p1)
            rod2.put_start_and_end_on(curr_p1, curr_p2)
            ball1.move_to(curr_p1)
            ball2.move_to(curr_p2)

        pendulum_group.add_updater(update_pendulum)

        # Add objects to scene
        self.add(traced_path, pendulum_group)

        # Play animation for exactly 20 seconds
        self.play(
            time_tracker.animate.set_value(t_max), 
            run_time=t_max, 
            rate_func=linear
        )
        
        pendulum_group.remove_updater(update_pendulum)
        self.wait(1)
        
