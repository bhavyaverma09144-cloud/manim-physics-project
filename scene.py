from manim import *
import numpy as np

class MechanicalLinkage(Scene):
    def construct(self):
        # --- 1. PHYSICAL PARAMETERS ---
        g = 9.81         # Gravity
        l = 2.0          # Length of rod
        m1 = 1.0         # Mass of rod
        a = 1.2          # Distance to disk attachment
        R = 0.8          # Radius of disk
        m2 = 2.0         # Mass of disk
        
        I1 = (1.0 / 3.0) * m1 * (l**2)
        I2 = 0.5 * m2 * (R**2) + m2 * (a**2)
        total_inertia = I1 + I2

        # Initial conditions: 60 degrees from vertical on the left
        theta_init = -np.pi / 3
        omega_init = 0.0

        # Simulation time settings
        t_max = 20.0
        fps = 60
        dt = 1.0 / fps
        substeps = 20    # True physics sub-steps per frame for precision
        dt_sub = dt / substeps

        total_steps = int(t_max * fps)
        
        # --- 2. PRE-COMPUTE TRUE STEP-BY-STEP PHYSICS (Blazing Fast Execution) ---
        # We compute every single force/torque step upfront so playback has zero lag.
        theta_history = np.zeros(total_steps)
        th = theta_init
        w = omega_init

        for i in range(total_steps):
            for _ in range(substeps):
                # Newton-Euler Torque calculation from gravity
                torque_gravity_1 = -m1 * g * (l / 2.0) * np.sin(th)
                torque_gravity_2 = -m2 * g * a * np.sin(th)
                total_torque = torque_gravity_1 + torque_gravity_2
                
                # Angular acceleration alpha = Torque / Inertia
                alpha = total_torque / total_inertia

                # Step-by-step Euler/Verlet integration
                w += alpha * dt_sub
                th += w * dt_sub
            
            theta_history[i] = th

        # --- 3. MANIM GRAPHICAL SETUP ---
        pivot = np.array([0.0, 1.5, 0.0])
        
        support = Triangle(color=WHITE, stroke_width=3).scale(0.3).move_to(pivot + np.array([0, 0.2, 0]))
        
        rod_line = Line(pivot, pivot + np.array([l * np.sin(theta_init), -l * np.cos(theta_init), 0]), stroke_width=6, color=BLUE_C)
        
        disk_center_pos = pivot + np.array([a * np.sin(theta_init), -a * np.cos(theta_init), 0])
        disk = Circle(radius=R, color=TEAL_C, fill_opacity=0.3).move_to(disk_center_pos)
        disk_center_dot = Circle(radius=0.08, color=WHITE, fill_opacity=1).move_to(disk_center_pos)
        
        cross1 = Line(disk_center_pos + np.array([-R, 0, 0]), disk_center_pos + np.array([R, 0, 0]), color=TEAL_E, stroke_width=2)
        cross2 = Line(disk_center_pos + np.array([0, -R, 0]), disk_center_pos + np.array([0, R, 0]), color=TEAL_E, stroke_width=2)
        disk_group = VGroup(disk, disk_center_dot, cross1, cross2)

        linkage_group = VGroup(support, rod_line, disk_group)

        traced_path = TracedPath(
            lambda: rod_line.get_end(), 
            stroke_color=YELLOW_E, 
            stroke_width=3, 
            stroke_opacity=[0, 0.9], 
            dissipating_time=4.0
        )

        title = Text("Mechanical Linkage Dynamics (Optimized True Physics)", font_size=22, color=LIGHT_GRAY).to_corner(UL)
        self.add(title, traced_path, linkage_group)

        # --- 4. SMOOTH RENDER LOOP ---
        time_tracker = ValueTracker(0.0)

        def update_linkage(mob):
            t = time_tracker.get_value()
            idx = int(t * fps)
            if idx >= total_steps:
                idx = total_steps - 1
            
            th = theta_history[idx]
            
            new_rod_end = pivot + np.array([l * np.sin(th), -l * np.cos(th), 0])
            new_disk_pos = pivot + np.array([a * np.sin(th), -a * np.cos(th), 0])

            rod_line.put_start_and_end_on(pivot, new_rod_end)
            
            current_center = disk_group.get_center()
            displacement = new_disk_pos - current_center
            disk_group.shift(displacement)

        linkage_group.add_updater(update_linkage)

        # Play for 20 seconds smoothly without lagging
        self.play(
            time_tracker.animate.set_value(t_max), 
            run_time=t_max, 
            rate_func=linear
        )
        
        linkage_group.remove_updater(update_linkage)
        self.wait(1)
                
