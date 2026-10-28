from manim import *
import numpy as np

class MechanicalLinkage(Scene):
    def construct(self):
        # --- 1. SIMULATION PARAMETERS ---
        g = 9.81         # Gravity
        L1 = 2.0         # Length of rod 1
        L2 = 2.0         # Length of rod 2
        m1 = 1.0         # Mass 1
        m2 = 1.0         # Mass 2

        # Initial positions: 60 degrees (-pi/3 radians) from the downward vertical on the left
        theta1 = -np.pi / 3
        theta2 = -np.pi / 3
        
        # Angular velocities and accelerations
        omega1 = 0.0
        omega2 = 0.0

        # Pivot point
        pivot = np.array([0.0, 1.0, 0.0])

        # Initial Cartesian positions of the bobs
        pos1 = pivot + np.array([L1 * np.sin(theta1), -L1 * np.cos(theta1), 0])
        pos2 = pos1 + np.array([L2 * np.sin(theta2), -L2 * np.cos(theta2), 0])

        # Velocities in Cartesian coordinates for step-by-step force updates
        v1 = np.array([0.0, 0.0, 0.0])
        v2 = np.array([0.0, 0.0, 0.0])

        # --- 2. MANIM GRAPHICAL OBJECTS ---
        rod1 = Line(pivot, pos1, stroke_width=5, color=BLUE_C)
        rod2 = Line(pos1, pos2, stroke_width=5, color=TEAL_C)
        
        ball1 = Circle(radius=0.15, color=BLUE_E, fill_opacity=1).move_to(pos1)
        ball2 = Circle(radius=0.18, color=YELLOW_C, fill_opacity=1).move_to(pos2)
        pivot_dot = Circle(radius=0.08, color=WHITE, fill_opacity=1).move_to(pivot)

        pendulum_group = VGroup(rod1, rod2, ball1, ball2, pivot_dot)

        traced_path = TracedPath(
            ball2.get_center, 
            stroke_color=YELLOW_E, 
            stroke_width=3, 
            stroke_opacity=[0, 0.9], 
            dissipating_time=4.0
        )

        title = Text("Frame-by-Frame True Physics Double Pendulum", font_size=24, color=LIGHT_GRAY).to_corner(UL)
        self.add(title, traced_path, pendulum_group)

        # --- 3. FRAME-BY-FRAME FORCE & CONSTRAINT SOLVER ---
        # We use a sub-stepping Verlet / Euler approach with constraint enforcement 
        # to ensure it strictly respects physical lengths and forces every single step.
        
        dt_frame = 1.0 / 60.0  # Time step per frame
        substeps = 20          # Sub-steps per frame for high stability

        state = {
            "p1": pos1.copy(),
            "p2": pos2.copy(),
            "v1": v1.copy(),
            "v2": v2.copy()
        }

        def update_physics(mob, dt):
            if dt == 0:
                return
            
            # Sub-stepping for numerical precision
            dt_sub = (dt_frame / substeps)
            
            p1 = state["p1"]
            p2 = state["p2"]
            v1 = state["v1"]
            v2 = state["v2"]

            for _ in range(substeps):
                # Forces on Bob 1: Gravity
                f1 = np.array([0.0, -m1 * g, 0.0])
                # Forces on Bob 2: Gravity
                f2 = np.array([0.0, -m2 * g, 0.0])

                # Accelerations from forces (a = F / m)
                a1 = f1 / m1
                a2 = f2 / m2

                # Update velocities (Euler integration step)
                v1 += a1 * dt_sub
                v2 += a2 * dt_sub

                # Update positions
                p1 += v1 * dt_sub
                p2 += v2 * dt_sub

                # --- RIGID ROD CONSTRAINT ENFORCEMENT (SHAKE-FREE VERLET STYLE) ---
                # Enforce Rod 1 length from pivot
                dir1 = p1 - pivot
                dist1 = np.linalg.norm(dir1)
                p1 = pivot + (dir1 / dist1) * L1

                # Enforce Rod 2 length from Bob 1
                dir2 = p2 - p1
                dist2 = np.linalg.norm(dir2)
                p2 = p1 + (dir2 / dist2) * L2

                # Correct velocities based on constrained position adjustments
                # (Simulates internal rod tension forces dynamically)
                v1 = (p1 - state["p1"]) / dt_sub
                v2 = (p2 - state["p2"]) / dt_sub
                
                state["p1"] = p1.copy()
                state["p2"] = p2.copy()

            state["v1"] = v1
            state["v2"] = v2

            # Update Manim visual elements to match true positions
            rod1.put_start_and_end_on(pivot, state["p1"])
            rod2.put_start_and_end_on(state["p1"], state["p2"])
            ball1.move_to(state["p1"])
            ball2.move_to(state["p2"])

        pendulum_group.add_updater(update_physics)

        # Run for 20 seconds
        self.wait(20.0)
        pendulum_group.remove_updater(update_physics)
        
