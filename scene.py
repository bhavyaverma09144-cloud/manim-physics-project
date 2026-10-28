from manim import *

class MechanicalLinkage(Scene):
    def construct(self):
        # Title and labels representing mechanics
        title = Text("Mechanical System Simulation", font_size=32).to_edge(UP)
        self.play(Write(title))

        # Draw a circle representing a mass/wheel (m2, R)
        wheel = Circle(radius=1.5, color=BLUE, fill_opacity=0.4).shift(LEFT * 2)
        center_dot = Dot(wheel.get_center(), color=WHITE)
        label_m2 = MathTex("m_2, R").move_to(wheel.get_center())

        # Draw a connecting rod/link
        rod = Line(wheel.get_center(), RIGHT * 2, color=WHITE)
        pivot = Triangle(color=YELLOW).scale(0.3).rotate(PI).move_to(RIGHT * 0.5 + DOWN * 0.2)
        
        # Group them together
        group = VGroup(wheel, center_dot, label_m2, rod)
        
        self.play(Create(group), FadeIn(pivot))
        
        # Animate rotation to simulate mechanical movement
        self.play(Rotate(wheel, angle=PI/2, about_point=wheel.get_center()), run_time=2)
        self.play(Rotate(wheel, angle=-PI/2, about_point=wheel.get_center()), run_time=2)
        
        self.wait(1)

