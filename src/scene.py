import numpy as np
from manim import *
from src.physics import simulate_pendulum

class DoublePendulumScene(Scene):
    def construct(self):
        t_max = 10.0
        fps = 30
        t, y = simulate_pendulum(t_max=t_max, fps=fps)
        theta1, _, theta2, _ = y

        L1, L2 = 2.5, 2.5
        idx = ValueTracker(0)

        def get_p1():
            i = int(np.clip(idx.get_value(), 0, len(t) - 1))
            return np.array([L1 * np.sin(theta1[i]), -L1 * np.cos(theta1[i]), 0])

        def get_p2():
            i = int(np.clip(idx.get_value(), 0, len(t) - 1))
            p1 = get_p1()
            return p1 + np.array([L2 * np.sin(theta2[i]), -L2 * np.cos(theta2[i]), 0])

        dot1 = Dot(point=get_p1(), color=BLUE)
        dot2 = Dot(point=get_p2(), color=RED)

        line1 = always_redraw(lambda: Line(ORIGIN, dot1.get_center(), color=WHITE))
        line2 = always_redraw(lambda: Line(dot1.get_center(), dot2.get_center(), color=WHITE))

        dot1.add_updater(lambda d: d.move_to(get_p1()))
        dot2.add_updater(lambda d: d.move_to(get_p2()))

        trace = TracedPath(dot2.get_center, stroke_color=YELLOW, stroke_width=2)

        self.add(trace, line1, line2, dot1, dot2)

        self.play(
            idx.animate.set_value(len(t) - 1),
            run_time=t_max,
            rate_func=linear
        )

if __name__ == "__main__":
    from manim import config
    config.media_dir = "media"
    render_scene_as_movie(DoublePendulumScene())
