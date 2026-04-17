from manim import *


class SelfChecksumScene(Scene):
    def construct(self):
        self.show_title()
        self.build_segments()
        self.animate_scanning()
        self.compute_hash()
        self.show_comparison()
        self.show_match()
        self.show_mismatch()

    def show_title(self):
        title = Text("Самопроверка контрольной суммы", font_size=40)
        self.play(Write(title), run_time=2)
        self.wait(1)
        self.play(FadeOut(title))

    def build_segments(self):
        # Hex
        self.hex_data = [
            "55", "48", "89", "E5", "48", "83", "EC", "20",
            "48", "89", "7D", "E8", "48", "89", "75", "F0",
            "8B", "45", "E8", "83", "C0", "01", "89", "45",
            "FC", "48", "8B", "45", "F0", "48", "8D", "50",
            "08", "48", "89", "55", "F0", "8B", "00", "01",
            "45", "FC", "8B", "45", "FC", "5D", "C3", "90",
        ]

        # ---сегмент .text--------------------------------------------------
        self.segment_rect = Rectangle(
            width=5.5, height=3.2,
            color=BLUE_D, fill_opacity=0.1,
            stroke_width=2,
        ).shift(LEFT * 3.5 + UP * 1.3)

        self.segment_label = Text(
            "Сегмент .text", font_size=22, color=BLUE_C
        ).next_to(self.segment_rect, UP, buff=0.15)

        #self.segment_icon = ImageMobject("pic/Screenshot_1.png").scale_to_fit_height(0.5)
        #self.segment_icon.next_to(self.segment_label, RIGHT, buff=0.15)

        # текстовые объекты hex-байтов
        self.hex_mobjects = VGroup(*[
            Text(b, font="Monospace", font_size=18, color=WHITE)
            for b in self.hex_data
        ])
        self.hex_mobjects.arrange_in_grid(rows=6, cols=8, buff=0.2)
        self.hex_mobjects.move_to(self.segment_rect.get_center())

        # ---секция .rsrc-------------------------------------------------
        self.rsrc_rect = Rectangle(
            width=5.5, height=1.6,
            color=TEAL, fill_opacity=0.1,
            stroke_width=2,
        ).next_to(self.segment_rect, DOWN, buff=0.6)

        # метка внутри прямоугольника, сверху
        self.rsrc_label = Text(
            "Секция .rsrc", font_size=18, color=TEAL
        ).move_to(self.rsrc_rect.get_top() + DOWN * 0.25)

        # эталонный хеш
        self.rsrc_hash_label = Text(
            "Эталон SHA-256:", font_size=16, color=GREY_B
        ).move_to(self.rsrc_rect.get_center() + UP * 0.1)

        self.ref_value = Text(
            '"a3b2c1d0e4f56789...38fe"', font="Monospace", font_size=20, color=WHITE
        ).move_to(self.rsrc_rect.get_center() + DOWN * 0.3)

        # анимация появления
        self.play(
            FadeIn(self.segment_rect),
            Write(self.segment_label),
            #FadeIn(self.segment_icon),
            run_time=1,
        )
        self.play(
            LaggedStart(*[FadeIn(h, shift=UP * 0.2) for h in self.hex_mobjects],
                         lag_ratio=0.03),
            run_time=2,
        )

        # показать .rsrc
        self.play(
            FadeIn(self.rsrc_rect),
            Write(self.rsrc_label),
            run_time=0.8,
        )
        self.play(
            Write(self.rsrc_hash_label),
            Write(self.ref_value),
            run_time=1,
        )
        self.wait(0.5)

        # ---блок SHA-256 появляется здесь, до сканирования------------------
        self.hash_rect = Rectangle(
            width=4.0, height=1.8,
            color=ORANGE, fill_opacity=0.1,
            stroke_width=2,
        ).shift(RIGHT * 3.2 + UP * 1.3)

        self.hash_label_text = Text("SHA-256", font_size=24, color=ORANGE).next_to(
            self.hash_rect, UP, buff=0.15
        )

        self.seg_to_hash_arrow = Arrow(
            self.segment_rect.get_right(),
            self.hash_rect.get_left(),
            color=ORANGE, stroke_width=2, buff=0.1,
        )

        self.play(
            FadeIn(self.hash_rect),
            Write(self.hash_label_text),
            GrowArrow(self.seg_to_hash_arrow),
            run_time=1,
        )

    def animate_scanning(self):
        # создание курсора сканирования
        cursor = SurroundingRectangle(
            self.hex_mobjects[0], color=YELLOW, buff=0.06, stroke_width=3
        )
        self.play(Create(cursor), run_time=0.3)

        # сканирование побайтово
        for i in range(48):
            byte_mob = self.hex_mobjects[i]
            new_cursor = SurroundingRectangle(
                byte_mob, color=YELLOW, buff=0.06, stroke_width=3
            )
            self.play(
                Transform(cursor, new_cursor),
                byte_mob.animate.set_color(GREEN_C),
                run_time=0.15,
            )

        self.play(FadeOut(cursor), run_time=0.3)
        self.wait(0.3)

    def compute_hash(self):
        # блок SHA-256 уже создан в build_segments — просто показываем результат

        # отображение вычисленного хеша
        self.hash_value = Text(
            '"a3b2c1d0e4f56789...38fe"', font="Monospace", font_size=20, color=YELLOW
        ).move_to(self.hash_rect.get_center() + DOWN * 0.15)

        computed_label = Text(
            "Вычислено:", font_size=18, color=GREY_B
        ).move_to(self.hash_rect.get_center() + UP * 0.45)

        self.play(Write(computed_label), run_time=0.5)
        self.play(Write(self.hash_value), run_time=1)
        self.wait(0.5)

    def show_comparison(self):
        # изогнутая стрелка от вычисленного хеша к эталону в .rsrc
        arrow = CurvedArrow(
            self.hash_rect.get_left() + DOWN * 0.5,
            self.rsrc_rect.get_right(),
            color=GREY_B,
            angle=-TAU / 4,
            stroke_width=2,
        )
        compare_text = Text(
            "Сравнение", font_size=24, color=GREY_B
        ).move_to(arrow.point_from_proportion(0.5) + LEFT * 1.0 + UP * 0.2)

        self.play(Create(arrow), Write(compare_text), run_time=0.8)
        self.wait(0.5)

        self.arrow = arrow
        self.compare_text = compare_text

    def show_match(self):
        # подсветка обоих хешей зелёным
        self.play(
            self.hash_value.animate.set_color(GREEN),
            self.ref_value.animate.set_color(GREEN),
            run_time=0.6,
        )

        # галочка
        check = VGroup(
            Line(ORIGIN, DOWN * 0.3 + RIGHT * 0.2, color=GREEN, stroke_width=5),
            Line(DOWN * 0.3 + RIGHT * 0.2, UP * 0.4 + RIGHT * 0.7, color=GREEN, stroke_width=5),
        ).scale(1.5).shift(RIGHT * 3.2 + DOWN * 1.5)

        result_text = Text(
            "Приложение не модифицировано", font_size=22, color=GREEN
        ).next_to(check, DOWN, buff=0.3)

        self.play(Create(check), run_time=0.5)
        self.play(Write(result_text), run_time=1)
        self.play(Flash(check, color=GREEN, flash_radius=0.6), run_time=0.5)
        self.wait(1.5)

        # скрытие
        self.play(
            FadeOut(check), FadeOut(result_text),
            self.hash_value.animate.set_color(YELLOW),
            self.ref_value.animate.set_color(WHITE),
            run_time=0.8,
        )

    def show_mismatch(self):
        # Патч одного байта
        patched_byte = self.hex_mobjects[6]
        new_byte = Text("FF", font="Monospace", font_size=18, color=RED)
        new_byte.move_to(patched_byte.get_center())

        patch_label = Text(
            "Патч!", font_size=20, color=RED
        ).next_to(patched_byte, UP, buff=0.15)

        patch_icon = ImageMobject("pic/Screenshot_1.png").scale_to_fit_height(1.5)
        patch_icon.next_to(patch_label, RIGHT, buff=0.5)

        self.play(
            Transform(patched_byte, new_byte),
            FadeIn(patch_label, shift=DOWN * 0.2),
            FadeIn(patch_icon, shift=DOWN * 0.2),
            run_time=0.8,
        )
        self.wait(0.5)

        # вспышка только по пропатченному байту
        flash_rect = SurroundingRectangle(
            patched_byte, color=YELLOW, buff=0.08, stroke_width=3
        )
        self.play(
            ShowPassingFlash(flash_rect, time_width=0.4),
            run_time=1.5,
        )

        # новое значение хеша
        new_hash = Text(
            "7f1e9a42bc8d3017...bca4", font="Monospace", font_size=20, color=RED
        ).move_to(self.hash_value.get_center())

        self.play(Transform(self.hash_value, new_hash), run_time=0.8)

        # подсветка несовпадения
        self.play(
            Indicate(self.hash_value, color=RED, scale_factor=1.2),
            Indicate(self.ref_value, color=RED, scale_factor=1.2),
            run_time=1,
        )

        # крестик
        cross = VGroup(
            Line(UL * 0.3, DR * 0.3, color=RED, stroke_width=5),
            Line(DL * 0.3, UR * 0.3, color=RED, stroke_width=5),
        ).scale(1.5).shift(RIGHT * 3.2 + DOWN * 1.5)

        warning_text = VGroup(
            Text("ВНИМАНИЕ: Приложение модифицировано!", font_size=22, color=RED),
            Text(
                "Предотвращение ввода ПИН-кода в скомпрометированное приложение",
                font_size=16, color=RED,
            ),
        ).arrange(DOWN, buff=0.15).next_to(cross, DOWN, buff=0.3)

        self.play(Create(cross), run_time=0.5)
        self.play(Write(warning_text), run_time=1.2)
        self.play(Flash(cross, color=RED, flash_radius=0.6), run_time=0.5)
        self.wait(2)
