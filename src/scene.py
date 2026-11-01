import numpy as np
from manim import *
from src.physics import simulate_pendulum

class AdvancedDoublePendulumScene(Scene):
    def construct(self):
        self.camera.background_color = "#0b1020"

        t_max = 12.0
        fps = 60
        t, y = simulate_pendulum(t_max=t_max, fps=fps)
        theta1, omega1, theta2, omega2 = y

        L1, L2 = 2.7, 2.7
        anchor = np.array([0.0, 2.5, 0.0])

        idx = ValueTracker(0)

        def current_index():
            return int(np.clip(idx.get_value(), 0, len(t) - 1))

        def get_p1():
            i = current_index()
            return anchor + np.array([
                L1 * np.sin(theta1[i]),
                -L1 * np.cos(theta1[i]),
                0.0
            ])

        def get_p2():
            i = current_index()
            p1 = get_p1()
            return p1 + np.array([
                L2 * np.sin(theta2[i]),
                -L2 * np.cos(theta2[i]),
                0.0
            ])

        # Background grid
        grid = NumberPlane(
            x_range=(-8, 8, 1),
            y_range=(-5, 6, 1),
            background_line_style={
                "stroke_color": BLUE_D,
                "stroke_width": 0.5,
                "stroke_opacity": 0.25
            }
        )
        grid.set_opacity(0.35)
        self.add(grid)

        # Pivot and rods
        pivot = Dot(anchor, radius=0.18, color=WHITE)
        bob1 = Dot(point=get_p1(), radius=0.18, color=BLUE)
        bob2 = Dot(point=get_p2(), radius=0.20, color=RED)

        rod1 = always_redraw(lambda: Line(anchor, bob1.get_center(), stroke_width=4, color=WHITE))
        rod2 = always_redraw(lambda: Line(bob1.get_center(), bob2.get_center(), stroke_width=4, color=WHITE))

        bob1.add_updater(lambda m: m.move_to(get_p1()))
        bob2.add_updater(lambda m: m.move_to(get_p2()))

        # Trail of the second bob
        trail_points = []
        trail = always_redraw(lambda: self._draw_trail(trail_points, current_index()))

        def record_trail():
            trail_points.append(get_p2().copy())
            if len(trail_points) > 120:
                trail_points.pop(0)

        # Dynamic angle labels
        theta1_label = DecimalNumber(
            0,
            num_decimal_places=2,
            include_sign=True
        ).to_corner(UL).shift(0.7 * RIGHT + 0.2 * DOWN)
        theta2_label = DecimalNumber(
            0,
            num_decimal_places=2,
            include_sign=True
        ).to_corner(UR).shift(0.7 * LEFT + 0.2 * DOWN)

        theta1_text = Text(r"$\theta_1$").next_to(theta1_label, LEFT, buff=0.2)
        theta2_text = Text(r"$\theta_2$").next_to(theta2_label, LEFT, buff=0.2)

        theta1_label.add_updater(lambda d: d.set_value(theta1[current_index()]))
        theta2_label.add_updater(lambda d: d.set_value(theta2[current_index()]))

        # Optional energy readout
        energy_label = DecimalNumber(
            0,
            num_decimal_places=2
        ).to_corner(UR).shift(0.7 * LEFT + 1.1 * DOWN)
        energy_label.set_color(YELLOW)

        def get_total_energy():
            i = current_index()
            th1, w1, th2, w2 = theta1[i], omega1[i], theta2[i], omega2[i]
            l1, l2 = L1, L2
            # approximate mechanical energy
            v1 = l1 * w1
            v2 = np.hypot(
                l1 * w1,
                l2 * w2
            )
            pe = 9.81 * (
                l1 * np.cos(th1) +
                l2 * np.cos(th2)
            )
            ke = 0.5 * (v1**2 + v2**2)
            return ke - pe

        energy_label.add_updater(lambda d: d.set_value(get_total_energy()))

        title = Tex("Advanced Double Pendulum").scale(0.9).to_edge(UP)
        self.add(title, pivot, rod1, rod2, bob1, bob2, theta1_label, theta2_label, theta1_text, theta2_text, energy_label)

        # Add the trail after main objects
        self.add(trail)

        self.play(
            idx.animate.set_value(len(t) - 1),
            run_time=t_max,
            rate_func=linear
        )

    def _draw_trail(self, trail_points, current_index):
        if len(trail_points) < 2:
            return VMobject()

        path = VMobject()
        path.set_points_as_corners([np.array(p) for p in trail_points])
        path.set_stroke(color=YELLOW, width=2.5, opacity=0.9)
        return path
