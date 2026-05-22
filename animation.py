"""
Анимация ЛР2: Прозрачное шифрование минифильтр-драйвером Windows.

Рендер всех сцен:
  manim render -ql animation.py          (preview, 480p)
  manim render -qh animation.py          (HD 1080p)

Рендер одной сцены:
  manim render -ql animation.py Scene1Architecture
"""

from manim import *
from helpers import *

config.background_color = BG_COLOR


# ═══════════════════════════════════════════════════════════
#  Сцена 1 — Архитектура + Операция записи (Write)
# ═══════════════════════════════════════════════════════════
class Scene1ArchAndWrite(Scene):

    # ── Общий layout (используется и Scene3Read) ─────────
    @staticmethod
    def build_layout() -> dict:
        BH = 0.4
        BW = 4.8
        FS = 16
        boundary = create_boundary_line()
        boundary.move_to(ORIGIN + UP * 0.55)

        def block(name, color, extra_text=None):
            rect = RoundedRectangle(
                corner_radius=0.09,
                width=BW,
                height=BH,
                fill_color=color,
                fill_opacity=0.25,
                stroke_color=color,
                stroke_width=2,
            )

            label = Text(name, font=FONT, font_size=FS, color=WHITE)
            label.move_to(rect.get_center())
            label.align_to(rect, LEFT)
            label.shift(RIGHT * 0.30)

            group = VGroup(rect, label)

            if extra_text:
                extra = Text(extra_text, font=FONT, font_size=12, color=PLAINTEXT_COLOR)
                extra.move_to(rect.get_center())
                extra.align_to(rect, RIGHT)
                extra.shift(LEFT * 0.25)
                group.add(extra)

            return group

        # ── User Mode ──────────────────────────────────
        um = VGroup(
            block("test_app.exe",    USER_MODE_COLORS["app"]),
            block("msvcrt.dll",      USER_MODE_COLORS["crt"]),
            block("kernel32.dll",    USER_MODE_COLORS["kernel32"]),
            block("kernelbase.dll",  USER_MODE_COLORS["kernelbase"]),
            block("ntdll.dll",       USER_MODE_COLORS["ntdll"]),
        ).arrange(DOWN, buff=0.05)
        um.next_to(boundary, UP, buff=0.10)
        um.shift(LEFT * 2.4)

        # ── Kernel Mode стек ───────────────────────────
        io_mgr = block("I/O Manager", KERNEL_MODE_COLORS["io_manager"])
        fltmgr = block("fltmgr.sys",  KERNEL_MODE_COLORS["fltmgr"])
        ntfs   = block("NTFS.sys",    KERNEL_MODE_COLORS["ntfs"])
        volmgr = block("volmgr.sys",  KERNEL_MODE_COLORS["volmgr"])
        disk   = block("disk.sys",    KERNEL_MODE_COLORS["disk"])

        km_stack = VGroup(io_mgr, fltmgr, ntfs, volmgr, disk).arrange(DOWN, buff=0.05)
        km_stack.next_to(boundary, DOWN, buff=0.10)
        km_stack.shift(LEFT * 2.4)

        # ── Мини-стек вокруг PassThrough ─────────────
        # Высота 0.56 — достаточно для названия + alt-метки внутри
        def mini_block(name, color, fs=16):
            rect = RoundedRectangle(
                corner_radius=0.09, width=2.9, height=0.52,
                fill_color=color, fill_opacity=0.25,
                stroke_color=color, stroke_width=2,
            )
            lbl = Text(name, font=FONT, font_size=fs, color=WHITE)
            # текст прижат вправо
            lbl.move_to(rect.get_center())
            lbl.align_to(rect, LEFT)
            lbl.shift(RIGHT * 0.25 + UP * 0.08)
            return VGroup(rect, lbl)

        upper1 = mini_block("WdFilter.sys",  "#5a7ab8")
        upper2 = mini_block("CryptoPro.sys", "#7a5a9a")
        minifilter = mini_block("PassThrough.sys", KERNEL_MODE_COLORS["minifilter"], fs=17)
        minifilter[0].set_stroke(color=CIPHERTEXT_COLOR, width=3)
        lower1 = mini_block("luafv.sys", "#4a6a4a")

        mini_stack = VGroup(upper1, upper2, minifilter, lower1).arrange(DOWN, buff=0.05)
        mini_stack.next_to(fltmgr, RIGHT, buff=0.9).move_to(DOWN + RIGHT*1.8)

        # Метки altitude внутри блока, под названием
        def add_alt(blk, txt):
            lbl = Text(txt, font=FONT, font_size=10, color=GRAY_C)
            lbl.move_to(blk[0].get_center() + DOWN * 0.15)
            blk.add(lbl)

        add_alt(upper1,     "alt: 328010")
        add_alt(upper2,     "alt: 262144")
        add_alt(minifilter, "alt: 145000")
        add_alt(lower1,     "alt: 140010")

        dash = DashedLine(
            fltmgr.get_right(), mini_stack.get_left(),
            dash_length=0.10, color=CIPHERTEXT_COLOR, stroke_width=1.8,
        )

        # ── Диск (цилиндр) — уменьшен чтобы не залезать на подпись ──
        disk_2d = create_disk_2d(width=1.3, height=0.6)
        disk_2d.next_to(km_stack, DOWN, buff=0.12)

        return {
            "boundary":      boundary,
            "um_blocks":     um,
            "km_stack":      km_stack,
            "minifilter":    minifilter,
            "mini_stack":    mini_stack,
            "upper_filters": VGroup(upper1, upper2),
            "lower_filters": VGroup(lower1),
            "disk":          disk_2d,
            "dash":          dash,
        }

    # ── construct ────────────────────────────────────────
    def construct(self):
        layout = self.build_layout()
        boundary = layout["boundary"]
        um = layout["um_blocks"]
        km_stack = layout["km_stack"]
        minifilter = layout["minifilter"]
        mini_stack = layout["mini_stack"]
        disk_2d = layout["disk"]
        dash = layout["dash"]

        # # ═══ ЧАСТЬ 1: Обработка данных ══════════════════
        # title = Text(
        #     "Обработка данных: User Mode → Kernel Mode → Disk",
        #     font=FONT, font_size=20, color=WHITE,
        # ).to_edge(UP, buff=0.2)
        # self.play(FadeIn(title, run_time=0.5))

        # # Граница
        # self.play(GrowFromCenter(boundary[0]), FadeIn(boundary[1], boundary[2]), run_time=0.8)

        # # User Mode — блоки по одному
        # for block in um:
        #     self.play(FadeIn(block, shift=DOWN * 0.12), run_time=0.25)

        # # Kernel Mode — стек по одному
        # for block in km_stack:
        #     self.play(FadeIn(block, shift=UP * 0.12), run_time=0.25)

        # # Стек минифильтров (верхние + наш + нижние) + связь
        # self.play(FadeIn(mini_stack, shift=LEFT * 0.2), Create(dash), run_time=0.6)

        # # Диск
        # self.play(FadeIn(disk_2d, shift=UP * 0.1), run_time=0.3)

        # # Подписи архитектуры
        # cap = show_caption(
        #     self,
        #     "IRP содержит массив IO_STACK_LOCATION — по одному для каждого драйвера в стеке",
        # )
        # self.wait(2)
        # hide_caption(self, cap)

        # cap2 = show_caption(
        #     self,
        #     "Минифильтр регистрирует callback-и через FltRegisterFilter(),\n "
        #     "fltmgr.sys вызывает их при прохождении IRP",
        # )
        # self.wait(2)
        # hide_caption(self, cap2)

        # # Смена заголовка
        # title2 = Text(
        #     "Операция ЗАПИСИ (Write) — полный путь",
        #     font=FONT, font_size=20, color=WHITE,
        # ).to_edge(UP, buff=0.2)
        # self.play(Transform(title, title2), run_time=0.5)
        # self.wait(0.3)

        # # ═══ ЧАСТЬ 2: Write flow ════════════════════════

        # # Фаза: fwrite()
        # code_label = Text(
        #     'fwrite(buf, 1, size, f);',
        #     font=FONT, font_size=16, color=PLAINTEXT_COLOR,
        # ).next_to(um[0], RIGHT, buff=0.15)
        # self.play(FadeIn(code_label, run_time=0.4))

        # # Пакет — слева в блоке, прозрачность уменьшена (fill_opacity=0.05)
        # packet = create_data_packet('"Hello, World!"', PLAINTEXT_COLOR, font_size=13)
        # # Двигаем пакет к левому краю блоков, чтобы не перекрывал текст
        # packet.move_to(um[0][0].get_right() + LEFT * 1.05)
        # self.play(FadeIn(packet, run_time=0.3))

        # cap = show_caption(self, "Вызов библиотечной функции fwrite()")
        # self.wait(0.8)

        # # Фаза: User mode chain — пакет движется по левому краю блоков
        # for i in range(len(um) - 1):
        #     self.play(packet.animate.move_to(um[i + 1][0].get_right() + LEFT * 1.05), run_time=0.35)
        #     highlight_block(self, um[i + 1], YELLOW, duration=0.15)

        # hide_caption(self, cap)

        # # Asm
        # asm = VGroup(
        #     Text("mov eax, <NtWriteFile>", font=FONT, font_size=14, color=YELLOW),
        #     Text("syscall  ; Ring 3 -> Ring 0", font=FONT, font_size=14, color=YELLOW),
        # ).arrange(DOWN, aligned_edge=LEFT, buff=0.04)
        # asm.next_to(um[-1], RIGHT, buff=0.3)
        # self.play(FadeIn(asm, run_time=0.4))
        # self.wait(0.4)

        # # Пересечение границы — пакет движется по левому краю
        # cap2 = show_caption(self, "SYSCALL — переход из User Mode (Ring 3) в Kernel Mode (Ring 0)")
        # animate_boundary_cross(self, boundary, packet, km_stack[0].get_right() + LEFT * 1.05)
        # self.play(FadeOut(asm), FadeOut(code_label), run_time=0.3)
        # hide_caption(self, cap2)

        # # Фаза: I/O Manager создаёт IRP
        # highlight_block(self, km_stack[0], KERNEL_MODE_COLORS["io_manager"], duration=0.3)
        # cap3 = show_caption(self, "I/O Manager создаёт IRP в NonPagedPool (невыгружаемая память ядра)")

        # irp_card = create_irp_card("IRP_MJ_WRITE", show_stack_locations=True,
        #                             level_label="I/O Manager (NonPagedPool)")
        # irp_card.scale(0.85)
        # # Позиция: правее от io_mgr, вертикально по центру экрана
        # irp_card.move_to(RIGHT * 2.8 + DOWN*0.4)

        # left_top = irp_card.get_corner(UL)
        # left_bottom = irp_card.get_corner(DL)
        # right_top = km_stack[0].get_corner(UR)
        # right_bottom = km_stack[0].get_corner(DR)
        # trapezoid = Polygon(
        #     left_bottom, right_bottom, right_top, left_top,
        #     color = "#ffcc00",fill_opacity=0.3, stroke_width=3
        # )
         
        # # Прячем стеки на время показа IRP
        # self.play(
        #     FadeOut(packet, run_time=0.2),
        #     FadeOut(mini_stack, run_time=0.3),
        #     FadeOut(dash, run_time=0.3),
        # )
        # self.play(
        #     # GrowArrow(trap_arrow),
        #     FadeIn(trapezoid),
        #     FadeIn(irp_card, shift=UP * 0.2, run_time=0.8),
        # )
        # self.wait(1.5)
        # hide_caption(self, cap3)

        # # Убираем IRP-карточку и стрелку, возвращаем стеки
        # self.play(
        #     FadeOut(irp_card, run_time=0.3),
        #     FadeOut(trapezoid, run_time=0.3),
        # )
        # self.play(
        #     FadeIn(mini_stack, run_time=0.4),
        #     FadeIn(dash, run_time=0.4),
        # )

        # irp_token = create_irp_token("IRP_MJ_WRITE")
        # #irp_token.move_to(km_stack[0].get_right() + LEFT * 1.05)
        # irp_token.move_to(km_stack[0][0].get_center())
        # irp_token.align_to(km_stack[0][0], RIGHT)
        # irp_token.shift(LEFT * 0.25)
        # self.play(FadeIn(irp_token, run_time=0.3))

        # # Фаза: IRP вниз по стеку — токен идёт по левому краю
        # self.play(irp_token.animate.move_to(km_stack[1].get_right() + LEFT * 1.05), run_time=0.5)
        # highlight_block(self, km_stack[1], KERNEL_MODE_COLORS["fltmgr"], duration=0.3)
        # cap4 = show_caption(self, "Filter Manager вызывает PreOperation callback минифильтра")
        # self.wait(0.5)

        # # PassThrough.sys — PreOperation
        # self.play(irp_token.animate.move_to(minifilter.get_right() + LEFT * 1.05), run_time=0.5)
        # highlight_block(self, minifilter, CIPHERTEXT_COLOR, duration=0.3)
        # hide_caption(self, cap4)

        # cap5 = show_caption(self, "PtPreOperationPassThrough() — проверка расширения файла")
        # # Зелёный блок — справа от minifilter со стрелкой (скрин 4, 9)
        # ext_check_pos = minifilter.get_right() + RIGHT * 1.9
        # ext_check = show_extension_check(self, ext_check_pos, "IRP_MJ_WRITE")
        # ext_arrow = Arrow(
        #     minifilter.get_right(), ext_check.get_left(),
        #     buff=0.08, stroke_width=2, color=PLAINTEXT_COLOR, tip_length=0.15,
        # )
        # self.play(GrowArrow(ext_arrow))
        # self.wait(0.5)
        # self.play(FadeOut(ext_check, ext_arrow))
        # hide_caption(self, cap5)

        # Шифрование — пакет справа от PassThrough (скрин 5)
        cap6 = show_caption(self, "Минифильтр шифрует WriteBuffer алгоритмом AES-256")
        plain_packet = create_data_packet('"Hello, World!"', PLAINTEXT_COLOR, font_size=13)
        plain_packet.next_to(minifilter, RIGHT, buff=0.2)
        self.play(FadeIn(plain_packet, run_time=1))

        animate_crypto(self, plain_packet, "encrypt", '"\\x8a\\x3c\\xff..."', CIPHERTEXT_COLOR)
        self.wait(0.5)
        hide_caption(self, cap6)

        # # Обратно в стек → NTFS → volmgr → disk — токен по левому краю
        # self.play(irp_token.animate.move_to(km_stack[1].get_right() + LEFT * 1.05), run_time=0.3)

        # self.play(irp_token.animate.move_to(km_stack[2].get_right() + LEFT * 1.05), run_time=0.4)
        # highlight_block(self, km_stack[2], GRAY, duration=0.2)
        # cap7 = show_caption(self, "NTFS.sys: файловое смещение -> кластеры MFT ($DATA -> Cluster Run)")
        # self.wait(0.8)
        # hide_caption(self, cap7)

        # self.play(irp_token.animate.move_to(km_stack[3].get_right() + LEFT * 1.05), run_time=0.4)
        # highlight_block(self, km_stack[3], GRAY, duration=0.2)
        # cap8 = show_caption(self, "volmgr.sys: кластер -> LBA")
        # self.wait(0.5)
        # hide_caption(self, cap8)

        # self.play(irp_token.animate.move_to(km_stack[4].get_right() + LEFT * 1.05), run_time=0.4)
        # highlight_block(self, km_stack[4], GRAY, duration=0.2)
        # cap9 = show_caption(self, "disk.sys: формирует SCSI WRITE(10)")
        # self.wait(0.5)
        # hide_caption(self, cap9)

        # # Фаза: Данные на диск
        # cipher_packet = plain_packet
        # self.play(
        #     irp_token.animate.move_to(disk_2d.get_center()),
        #     cipher_packet.animate.move_to(disk_2d.get_center()),
        #     run_time=0.6,
        # )
        # sectors = disk_2d[8]
        # self.play(
        #     *[s.animate.set_fill(color=CIPHERTEXT_COLOR, opacity=0.6) for s in sectors],
        #     run_time=0.5,
        # )
        # cap10 = show_caption(self, "На диске хранится шифротекст — недоступен без минифильтра")
        # self.wait(1.5)
        # self.play(FadeOut(cipher_packet, run_time=0.3))
        # hide_caption(self, cap10)

        # # Фаза: Completion — обратный путь по левому краю
        # cap11 = show_caption(self, "IRP Completion: обратный путь вверх по стеку")
        # for block in reversed(km_stack[1:]):
        #     self.play(irp_token.animate.move_to(block.get_right() + LEFT * 1.05), run_time=0.3)

        # self.play(irp_token.animate.move_to(minifilter.get_right() + LEFT * 1.05), run_time=0.3)

        # # PostOp — блок справа от minifilter со стрелкой (скрин 6)
        # postop_check = show_postop_write(self, minifilter.get_right() + RIGHT * 2.2)
        # postop_arrow = Arrow(
        #     minifilter.get_right(), postop_check.get_left(),
        #     buff=0.08, stroke_width=2, color=PLAINTEXT_COLOR, tip_length=0.15,
        # )
        # self.play(GrowArrow(postop_arrow))
        # self.wait(1.0)
        # self.play(FadeOut(postop_check, run_time=0.4), FadeOut(postop_arrow, run_time=0.4))
        # hide_caption(self, cap11)

        # # IoStatus = SUCCESS — стилизованный блок слева от I/O Manager (скрин 7)
        # self.play(irp_token.animate.move_to(km_stack[0].get_right() + LEFT * 1.05), run_time=0.3)

        # status_rect = RoundedRectangle(
        #     corner_radius=0.08, width=1.8, height=0.7,
        #     fill_color=PLAINTEXT_COLOR, fill_opacity=0.12,
        #     stroke_color=PLAINTEXT_COLOR, stroke_width=2,
        # )
        # status_text = VGroup(
        #     Text(
        #         "IoStatus =",
        #         font=FONT,
        #         font_size=12,
        #         color=PLAINTEXT_COLOR
        #     ),
        #     Text(
        #         "STATUS_SUCCESS",
        #         font=FONT,
        #         font_size=12,
        #         color=PLAINTEXT_COLOR
        #     ),
        # ).arrange(DOWN, buff=0.03)
        # status_text.move_to(status_rect.get_center())
        # status_block = VGroup(status_rect, status_text)
        # status_block.next_to(km_stack[0], LEFT + DOWN*0.2, buff=0.2)

        # self.play(FadeIn(status_block, run_time=0.4))

        # cap12 = show_caption(self, "fwrite() возвращает управление — запись завершена")
        # animate_boundary_cross(self, boundary, irp_token, um[-1].get_right() + LEFT * 1.05)

        # self.play(FadeOut(irp_token), FadeOut(status_block), run_time=0.3)
        # self.wait(0.5)
        # hide_caption(self, cap12)

        # # ═══ ЧАСТЬ 3: Read flow ═════════════════════════

        # # Смена заголовка
        # title3 = Text(
        #     "Операция ЧТЕНИЯ (Read) — обратный путь",
        #     font=FONT, font_size=20, color=WHITE,
        # ).to_edge(UP, buff=0.2)
        # self.play(Transform(title, title3), run_time=0.5)
        # self.wait(0.3)

        # # Фаза: fread() → SYSCALL → IRP (ускоренно)
        # code_label_r = Text(
        #     'fread(buf, 1, size, f);',
        #     font=FONT, font_size=16, color=PLAINTEXT_COLOR,
        # ).next_to(um[0], RIGHT, buff=0.15)
        # self.play(FadeIn(code_label_r, run_time=0.3))

        # cap_r1 = show_caption(self, "fread -> ReadFile -> NtReadFile -> SYSCALL -> I/O Manager создаёт IRP")

        # irp_token_r = create_irp_token("IRP_MJ_READ")
        # irp_token_r.move_to(um[0].get_right() + LEFT * 1.05)
        # self.play(FadeIn(irp_token_r, run_time=0.2))

        # for block in um[1:]:
        #     self.play(irp_token_r.animate.move_to(block.get_right() + LEFT * 1.05), run_time=0.15)

        # animate_boundary_cross(self, boundary, irp_token_r, km_stack[0].get_right() + LEFT * 1.05, duration=0.5)
        # self.play(FadeOut(code_label_r, run_time=0.2))
        # hide_caption(self, cap_r1)

        # # Фаза: IRP вниз (PreOperation)
        # cap_r2 = show_caption(self, "PreOperation для Read: минифильтр пропускает (расшифровка будет в Post)")

        # self.play(irp_token_r.animate.move_to(km_stack[1].get_right() + LEFT * 1.05), run_time=0.3)
        # highlight_block(self, km_stack[1], KERNEL_MODE_COLORS["fltmgr"], duration=0.2)

        # self.play(irp_token_r.animate.move_to(minifilter.get_right() + LEFT * 1.05), run_time=0.3)

        # # preflt_check справа от minifilter со стрелкой (скрин 8)
        # preflt_check = show_preflt_write(self, minifilter.get_right() + RIGHT * 2.2)
        # preflt_arrow = Arrow(
        #     minifilter.get_right(), preflt_check.get_left(),
        #     buff=0.08, stroke_width=2, color=PLAINTEXT_COLOR, tip_length=0.15,
        # )
        # self.play(GrowArrow(preflt_arrow))
        # self.wait(0.5)
        # self.play(FadeOut(preflt_check, run_time=0.4), FadeOut(preflt_arrow, run_time=0.4))

        # self.play(irp_token_r.animate.move_to(km_stack[1].get_right() + LEFT * 1.05), run_time=0.2)
        # for block in km_stack[2:]:
        #     self.play(irp_token_r.animate.move_to(block.get_right() + LEFT * 1.05), run_time=0.25)

        # hide_caption(self, cap_r2)

        # # Фаза: Диск возвращает шифротекст
        # self.play(irp_token_r.animate.move_to(disk_2d.get_center()), run_time=0.3)
        # cap_r3 = show_caption(self, "Диск возвращает зашифрованные данные")

        # cipher_packet_r = create_data_packet('"\\x8a\\x3c\\xff..."', CIPHERTEXT_COLOR, font_size=13)
        # cipher_packet_r.move_to(disk_2d.get_center())
        # self.play(FadeIn(cipher_packet_r, shift=UP * 0.2, run_time=0.4))
        # self.wait(0.5)
        # hide_caption(self, cap_r3)

        # # Фаза: IRP вверх → PostOperation в минифильтре — по левому краю
        # cap_r4 = show_caption(self, "IRP Completion: данные поднимаются вверх по стеку")

        # for block in reversed(km_stack[2:]):
        #     self.play(
        #         irp_token_r.animate.move_to(block.get_right() + LEFT * 1.05),
        #         cipher_packet_r.animate.move_to(block.get_right() + LEFT * 1.05),
        #         run_time=0.25,
        #     )
        # self.play(
        #     irp_token_r.animate.move_to(km_stack[1].get_right() + LEFT * 1.05),
        #     cipher_packet_r.animate.move_to(km_stack[1].get_right() + LEFT * 1.05),
        #     run_time=0.3,
        # )
        # hide_caption(self, cap_r4)

        # # → minifilter PostOperation — пакет справа от PassThrough (скрин 5)
        # self.play(
        #     irp_token_r.animate.move_to(minifilter.get_right() + LEFT * 1.05),
        #     cipher_packet_r.animate.next_to(minifilter, RIGHT, buff=0.2),
        #     run_time=0.4,
        # )
        # highlight_block(self, minifilter, CIPHERTEXT_COLOR, duration=0.3)
        # self.play(FadeOut(cipher_packet_r))

        # cap_r5 = show_caption(self, "PtPostOperationPassThrough() — расшифровка ReadBuffer")
        # # ext_check_r справа от minifilter со стрелкой (скрин 9)
        # ext_check_r = show_extension_check(self, minifilter.get_right() + RIGHT * 1.3, "IRP_MJ_READ")
        # ext_arrow_r = Arrow(
        #     minifilter.get_right(), ext_check_r.get_left(),
        #     buff=0.08, stroke_width=2, color=PLAINTEXT_COLOR, tip_length=0.15,
        # )
        # self.play(GrowArrow(ext_arrow_r))
        # self.wait(0.5)
        # self.play(FadeOut(ext_check_r, ext_arrow_r))
        # self.play(FadeIn(cipher_packet_r))


        # # Расшифровка
        # animate_crypto(self, cipher_packet_r, "decrypt", '"Hello, World!"', PLAINTEXT_COLOR)
        # self.wait(0.5)
        
        # hide_caption(self, cap_r5)

        # cap_r6 = show_caption(self, "Минифильтр расшифровал ReadBuffer — прозрачно для приложения")

        # # Фаза: Возврат приложению — по левому краю
        # self.play(irp_token_r.animate.move_to(km_stack[0].get_right() + LEFT * 1.05), run_time=0.3)
        # animate_boundary_cross(self, boundary, irp_token_r, um[-1].get_right() + LEFT * 1.05, duration=0.5)
        # self.play(cipher_packet_r.animate.move_to(um[-1].get_right() + LEFT * 1.05), run_time=0.3)

        # for block in reversed(um[:-1]):
        #     self.play(
        #         irp_token_r.animate.move_to(block.get_right() + LEFT * 1.05),
        #         cipher_packet_r.animate.move_to(block.get_right() + LEFT * 1.05),
        #         run_time=0.15,
        #     )
        # hide_caption(self, cap_r6)

        # # Результат
        # result = Text(
        #     '> Hello, World!',
        #     font=FONT, font_size=16, color=PLAINTEXT_COLOR,
        # ).next_to(um[0], RIGHT, buff=0.3)
        # self.play(FadeIn(result, run_time=0.4))

        # cap_r7 = show_caption(self, "Приложение получает расшифрованные данные, не зная о шифровании")
        # self.wait(2)
        # hide_caption(self, cap_r7)
        # self.play(FadeOut(irp_token_r), FadeOut(cipher_packet_r), FadeOut(result), run_time=0.3)



