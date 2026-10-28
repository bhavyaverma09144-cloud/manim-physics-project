from manim import *
import numpy as np
from scipy.integrate import solve_ivp

class MechanicalLinkage(Scene):
    def construct(self):
        # --- 1. PHYSICAL PARAMETERS (Rod + Disk Double Pendulum System) ---
        g = 9.81         # Gravity (m/s^2)
        
        # Link 1: Rod
        L1 = 1.5         # Length of rod
        m1 = 1.0         # Mass of rod
        
        # Link 2: Disk attached at distance 'a' with radius R
        L2 = 1.5         # Distance to disk center / second segment length
        R = 0.8          # Radius of the disk
        m2 = 2.0         # Mass of disk

        # Moments of Inertia
        I1 = (1.0 / 3.0) * m1 * (L1**2)
        I2 = 0.5 * m2 * (R**2)

        # Initial conditions: 60 degrees (-pi/3 radians) from vertical on the left for both links
        theta1_init = -np.pi / 3
        theta2_init = -np.pi / 3
        omega1_init = 0.0
        omega2_init = 0.0

        t_max = 20.0
        fps = 60
        t_eval = np.linspace(0, t_max, int(t_max * fps))

        # --- 2. TRUE 2-DOF LAGRANGIAN EQUATIONS OF MOTION ---
        def derivatives(t, y):
            th1, w1, th2, w2 = y
            d = th2 - th1
            
            # Coupled mass/inertia matrix components for the rod-disk linkage
            # Denominator determinant for 2-DOF articulated system
            den = (I1 + m2 * L1**2) * (I2 + m2 * L2**2) - (m2 * L1 * L2 * np.cos(d))**2
            if abs(den) < 1e-9:
                den = 1e-9

            # Torques and coupling terms from gravity and centrifugal/Coriolis forces
            torque1 = - (m1 * (L1/2.0) + m2 * L1) * g * np.sin(th1) - m2 * L1 * L2 * (w2**2) * np.sin(d)
            torque2 = - m2 * L2 * g * np.sin(th2) + m2 * L1 * L2 * (w1**2) * np.sin(d)

            dw1 = ((I2 + m2 * L2**2) * torque1 - (m2 * L1 * L2 * np.cos(d)) * torque2) / den
            dw2 = ((I1 + m2 * L1**2 + m2 * L1**2) * torque2 - (m2 * L1 * L2 * np.cos(d)) * torque1) / den

            return [w1, dw1, w2, dw2]

        # Solve coupled ODEs numerically
        sol = solve_ivp(
            derivatives, 
            [0, t_max], 
            [theta1_init, omega1_init, theta2_init, omega2_init], 
            t_eval=t_eval,
            method='RK45',
            rtol=1e-8,
            atol=1e-8
        )
        
        theta1 = sol.y[0]
        theta2 = sol.y[2]

        # --- 3. MANIM GRAPHICAL SETUP ---
        pivot = np.array([0.0, 1.5, 0.0])
        
        # Support bracket matching diagram style
        support = Triangle(color=WHITE, stroke_width=3).scale(0.3).move_to(pivot + np.array([0, 0.2, 0]))
        
        # Initial positions
        p1 = pivot + np.array([L1 * np.sin(theta1[0]), -L1 * np.cos(theta1[0]), 0])
        p2 = p1 + np.array([L2 * np.sin(theta2[0]), -L2 * np.cos(theta2[0]), 0])

        rod1 = Line(pivot, p1, stroke_width=6, color=BLUE_C)
        
        # Disk representing Link 2 with crosshairs matching your diagrams
        disk = Circle(radius=R, color=TEAL_C, fill_opacity=0.3).move_to(p2)
        disk_center_dot = Circle(radius=0.08, color=WHITE, fill_opacity=1).move_to(p2)
        cross1 = Line(p2 + np.array([-R, 0, 0]), p2 + np.array([R, 0, 0]), color=TEAL_E, stroke_width=2)
        cross2 = Line(p2 + np.array([0, -R, 0]), p2 + np.array([0, R, 0]), color=TEAL_E, stroke_width=2)
        
        disk_group = VGroup(disk, disk_center_dot, cross1, cross2)
        linkage_group = VGroup(support, rod1, disk_group)

        # Glowing trajectory trail for the disk center
        traced_path = TracedPath(
            disk_center_dot.get_center, 
            stroke_color=YELLOW_E, 
            stroke_width=3, 
            stroke_opacity=[0, 0.9], 
            dissipating_time=4.0
        )

        title = Text("Mechanical Linkage (True 2-DOF Double Pendulum)", font_size=22, color=LIGHT_GRAY).to_corner(UL)
        self.add(title, traced_path, linkage_group)

        # --- 4. SMOOTH ANIMATION UPDATER ---
        time_tracker = ValueTracker(0.0)
        total_steps = len(t_eval)

        def update_linkage(mob):
            t = time_tracker.get_value()
            idx = int(t * fps)
            if idx >= total_steps:
                idx = total_steps - 1
            
            th1 = theta1[idx]
            th2 = theta2[idx]
            
            curr_p1 = pivot + np.array([L1 * np.sin(th1), -L1 * np.cos(th1), 0])
            curr_p2 = curr_p1 + np.array([L2 * np.sin(th2), -L2 * np.cos(th2), 0])

            rod1.put_start_and_end_on(pivot, curr_p1)
            
            # Update disk group position and rotation to match authentic linkage kinematics
            current_center = disk_group.get_center()
            displacement = curr_p2 - current_center
            disk_group.shift(displacement)

        linkage_group.add_updater(update_linkage)

        # Play for 20 seconds
        self.play(
            time_tracker.animate.set_value(t_max), 
            run_time=t_max, 
            rate_func=linear
        )
        
        linkage_group.remove_updater(update_linkage)
        self.wait(1)
            
