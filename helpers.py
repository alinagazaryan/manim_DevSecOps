"""
Переиспользуемые визуальные компоненты для анимации ЛР2.
"""

from manim import *
import random

# ── Цвета ────────────────────────────────────────────────
BG_COLOR = "#1e1e1e"
USER_MODE_COLORS = {
    "app": "#4a90d9",
    "crt": "#5bb8e8",
    "kernel32": "#50c878",
    "kernelbase": "#8fbc5a",
    "ntdll": "#e8c840",
}
KERNEL_MODE_COLORS = {
    "io_manager": "#e8943a",
    "fltmgr": "#2d8a4e",
    "minifilter": "#d94040",
    "ntfs": "#888888",
    "volmgr": "#777777",
    "disk": "#666666",
}
IRP_COLOR = "#ffcc00"
PLAINTEXT_COLOR = "#00ff00"
CIPHERTEXT_COLOR = "#ff4444"
BOUNDARY_COLOR = "#ff2222"
FONT = "Monospace"


# ── Фабрика блока драйвера ──────────────────────────────
def create_driver_block(name: str, color: str, width=3.2, height=0.55) -> VGroup:
    rect = RoundedRectangle(
        corner_radius=0.08,
        width=width,
        height=height,
        fill_color=color,
        fill_opacity=0.25,
        stroke_color=color,
        stroke_width=2,
    )
    label = Text(name, font=FONT, font_size=18, color=WHITE)
    label.move_to(rect.get_center())
    return VGroup(rect, label)


def create_wide_block(name: str, color: str, desc: str, width=5.0, height=0.55) -> VGroup:
    rect = RoundedRectangle(
        corner_radius=0.08,
        width=width,
        height=height,
        fill_color=color,
        fill_opacity=0.25,
        stroke_color=color,
        stroke_width=2,
    )
    label = Text(name, font=FONT, font_size=16, color=WHITE)
    desc_text = Text(desc, font=FONT, font_size=11, color=GRAY_B)
    content = VGroup(label, desc_text).arrange(RIGHT, buff=0.3)
    content.move_to(rect.get_center())
    return VGroup(rect, content)


# ── Посылка с данными ────────────────────────────────────
def create_data_packet(text: str, color: str, font_size=16) -> VGroup:
    label = Text(text, font=FONT, font_size=font_size, color=color)
    rect = SurroundingRectangle(
        label, buff=0.12,
        fill_color=color, fill_opacity=0.12,
        stroke_color=color, stroke_width=1.5,
        corner_radius=0.06,
    )
    return VGroup(rect, label)


# ── IRP-карточка ─────────────────────────────────────────
def create_irp_card(major_function: str, show_stack_locations=False) -> VGroup:
    lines = [
        f"MajorFunction: {major_function}",
        "IoStatus: STATUS_PENDING",
        "UserBuffer: 0xFFFFFA80`1234",
    ]
    if show_stack_locations:
        lines += [
            "IO_STACK_LOCATION[0]: (fltmgr)",
            "IO_STACK_LOCATION[1]: (NTFS)",
            "IO_STACK_LOCATION[2]: (disk)",
        ]

    header = Text("IRP", font=FONT, font_size=18, color=IRP_COLOR, weight=BOLD)
    body_texts = [Text(l, font=FONT, font_size=12, color=WHITE) for l in lines]
    body = VGroup(*body_texts).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    content = VGroup(header, body).arrange(DOWN, buff=0.15, aligned_edge=LEFT)

    bg = SurroundingRectangle(
        content, buff=0.18,
        fill_color="#2a2000", fill_opacity=0.7,
        stroke_color=IRP_COLOR, stroke_width=2,
        corner_radius=0.08,
    )
    return VGroup(bg, content)


# ── Мини IRP-метка (для движения по стеку) ───────────────
def create_irp_token(major: str) -> VGroup:
    label = Text(f"IRP: {major}", font=FONT, font_size=13, color=IRP_COLOR)
    rect = SurroundingRectangle(
        label, buff=0.08,
        fill_color="#2a2000", fill_opacity=0.8,
        stroke_color=IRP_COLOR, stroke_width=1.5,
        corner_radius=0.05,
    )
    return VGroup(rect, label)


# ── Граница User/Kernel ──────────────────────────────────
def create_boundary_line() -> VGroup:
    line = DashedLine(
        LEFT * 7, RIGHT * 7,
        dash_length=0.15, dashed_ratio=0.5,
        color=BOUNDARY_COLOR, stroke_width=2,
    )
    label_left = Text(
        "User Mode (Ring 3)", font=FONT, font_size=13, color=BOUNDARY_COLOR
    ).next_to(line, UP, buff=0.08).to_edge(LEFT, buff=0.5)
    label_right = Text(
        "Kernel Mode (Ring 0)", font=FONT, font_size=13, color=BOUNDARY_COLOR
    ).next_to(line, DOWN, buff=0.08).to_edge(LEFT, buff=0.5)
    return VGroup(line, label_left, label_right)


# ── 2D-диск ─────────────────────────────────────────────
def create_disk_2d(width=2.8, height=1.0) -> VGroup:
    top_ellipse = Ellipse(width=width, height=0.35, color=GRAY, fill_opacity=0.3, stroke_width=1.5)
    body = Rectangle(width=width, height=height, color=GRAY, fill_opacity=0.15, stroke_width=1.5)
    bottom_ellipse = Ellipse(width=width, height=0.35, color=GRAY, fill_opacity=0.15, stroke_width=1.5)

    body.next_to(top_ellipse, DOWN, buff=0)
    bottom_ellipse.move_to(body.get_bottom())

    label = Text("Disk (sectors)", font=FONT, font_size=13, color=GRAY_B)
    label.move_to(body.get_center())

    sectors = VGroup()
    for i in range(6):
        s = Square(side_length=0.22, stroke_color=GRAY, stroke_width=0.5, fill_opacity=0)
        sectors.add(s)
    sectors.arrange(RIGHT, buff=0.05)
    sectors.move_to(body.get_center() + DOWN * 0.25)

    return VGroup(top_ellipse, body, bottom_ellipse, label, sectors)


# ── Подсветка блока ──────────────────────────────────────
def highlight_block(scene: Scene, block: VGroup, color: str, duration=0.4):
    rect = block[0]
    scene.play(
        rect.animate.set_stroke(color=color, width=4).set_fill(color=color, opacity=0.35),
        run_time=duration,
    )


def unhighlight_block(scene: Scene, block: VGroup, original_color: str, duration=0.3):
    rect = block[0]
    scene.play(
        rect.animate.set_stroke(color=original_color, width=2).set_fill(color=original_color, opacity=0.25),
        run_time=duration,
    )


# ── Эффект пересечения границы ───────────────────────────
def animate_boundary_cross(scene: Scene, boundary: VGroup, packet: VGroup, target_pos, duration=0.8):
    line = boundary[0]
    flash = line.copy().set_stroke(color=YELLOW, width=6, opacity=1)
    scene.play(
        FadeIn(flash, run_time=0.2),
        packet.animate.move_to(target_pos),
        run_time=duration,
    )
    scene.play(FadeOut(flash, run_time=0.3))


# ── Анимация шифрования / расшифровки ────────────────────
def animate_crypto(scene: Scene, packet: VGroup, mode: str, new_text: str, new_color: str):
    old_label = packet[1]
    chars = VGroup(*[
        Text(c, font=FONT, font_size=old_label.font_size, color=old_label.color)
        for c in old_label.text
    ])
    for i, ch in enumerate(chars):
        ch.move_to(old_label.get_left() + RIGHT * i * 0.18 + RIGHT * 0.09)

    scene.play(FadeOut(old_label, run_time=0.2))
    scene.add(chars)

    if mode == "encrypt":
        anims = []
        for ch in chars:
            target = ch.get_center() + np.array([
                random.uniform(-0.3, 0.3),
                random.uniform(-0.2, 0.2),
                0
            ])
            anims.append(ch.animate.move_to(target).set_color(CIPHERTEXT_COLOR))
        scene.play(*anims, run_time=0.6)
        scene.play(*[FadeOut(ch) for ch in chars], run_time=0.2)
    else:
        scene.play(
            *[ch.animate.set_color(PLAINTEXT_COLOR) for ch in chars],
            run_time=0.4,
        )
        scene.play(*[FadeOut(ch) for ch in chars], run_time=0.2)

    new_label = Text(new_text, font=FONT, font_size=old_label.font_size, color=new_color)
    new_label.move_to(packet[0].get_center())
    packet.remove(old_label)
    packet.add(new_label)

    new_bg = SurroundingRectangle(
        new_label, buff=0.12,
        fill_color=new_color, fill_opacity=0.12,
        stroke_color=new_color, stroke_width=1.5,
        corner_radius=0.06,
    )
    old_bg = packet[0]
    scene.play(
        FadeIn(new_label, run_time=0.3),
        Transform(old_bg, new_bg, run_time=0.3),
    )


# ── Проверка расширения ──────────────────────────────────
def show_extension_check(scene: Scene, position, major: str) -> VGroup:
    lines = [
        'FltGetFileNameInformation() -> "test.lab2ext"',
        'RtlEqualUnicodeString("lab2ext") -> TRUE',
        f'MajorFunction == {major} -> TRUE',
    ]
    texts = VGroup(*[
        Text(l, font=FONT, font_size=11, color=PLAINTEXT_COLOR) for l in lines
    ]).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
    bg = SurroundingRectangle(
        texts, buff=0.12,
        fill_color="#002200", fill_opacity=0.7,
        stroke_color=PLAINTEXT_COLOR, stroke_width=1,
        corner_radius=0.06,
    )
    group = VGroup(bg, texts).move_to(position)
    scene.play(FadeIn(group, run_time=0.6))
    scene.wait(1.5)
    return group


# ── Переход между сценами ────────────────────────────────
def scene_transition(scene: Scene):
    scene.wait(0.8)
    scene.play(FadeOut(*scene.mobjects, run_time=0.6))
    scene.wait(0.3)


# ── Подпись внизу экрана ─────────────────────────────────
def show_caption(scene: Scene, text: str, position=None, duration=2.0) -> Text:
    caption = Text(text, font=FONT, font_size=14, color=GRAY_A)
    if position is None:
        caption.to_edge(DOWN, buff=0.3)
    else:
        caption.move_to(position)
    scene.play(FadeIn(caption, run_time=0.3))
    return caption


def hide_caption(scene: Scene, caption):
    scene.play(FadeOut(caption, run_time=0.2))
