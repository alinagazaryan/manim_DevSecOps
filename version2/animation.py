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
        BH = 0.38
        boundary = create_boundary_line()
        boundary.move_to(ORIGIN + UP * 0.8)

        um = VGroup(
            create_driver_block("test_app.exe", USER_MODE_COLORS["app"], width=2.8, height=BH),
            create_driver_block("msvcrt.dll", USER_MODE_COLORS["crt"], width=2.8, height=BH),
            create_driver_block("kernel32.dll", USER_MODE_COLORS["kernel32"], width=2.8, height=BH),
            create_driver_block("kernelbase.dll", USER_MODE_COLORS["kernelbase"], width=2.8, height=BH),
            create_driver_block("ntdll.dll", USER_MODE_COLORS["ntdll"], width=2.8, height=BH),
        ).arrange(DOWN, buff=0.05)
        um.next_to(boundary, UP, buff=0.12)
        um.shift(LEFT * 3)

        io_mgr = create_driver_block("I/O Manager", KERNEL_MODE_COLORS["io_manager"], width=2.8, height=BH)
        fltmgr = create_driver_block("fltmgr.sys", KERNEL_MODE_COLORS["fltmgr"], width=2.8, height=BH)
        ntfs = create_driver_block("NTFS.sys", KERNEL_MODE_COLORS["ntfs"], width=2.8, height=BH)
        volmgr = create_driver_block("volmgr.sys", KERNEL_MODE_COLORS["volmgr"], width=2.8, height=BH)
        disk = create_driver_block("disk.sys", KERNEL_MODE_COLORS["disk"], width=2.8, height=BH)

        km_stack = VGroup(io_mgr, fltmgr, ntfs, volmgr, disk).arrange(DOWN, buff=0.05)
        km_stack.next_to(boundary, DOWN, buff=0.12)
        km_stack.shift(LEFT * 3)

        minifilter = create_driver_block(
            "PassThrough.sys", KERNEL_MODE_COLORS["minifilter"], width=2.6, height=0.42,
        )
        minifilter[0].set_stroke(color=CIPHERTEXT_COLOR, width=3)
        minifilter.next_to(fltmgr, RIGHT, buff=1.0)

        alt_label = Text("altitude 145000", font=FONT, font_size=9, color=GRAY_C)
        alt_label.next_to(minifilter, DOWN, buff=0.05)
        minifilter.add(alt_label)

        dash = DashedLine(
            fltmgr.get_right(), minifilter.get_left(),
            dash_length=0.08, color=CIPHERTEXT_COLOR, stroke_width=1.5,
        )

        disk_2d = create_disk_2d(width=2.0, height=0.4)
        disk_2d.next_to(km_stack, DOWN, buff=0.15)

        return {
            "boundary": boundary,
            "um_blocks": um,
            "km_stack": km_stack,
            "minifilter": minifilter,
            "disk": disk_2d,
            "dash": dash,
        }

    # ── construct ────────────────────────────────────────
    def construct(self):
        layout = self.build_layout()
        boundary = layout["boundary"]
        um = layout["um_blocks"]
        km_stack = layout["km_stack"]
        minifilter = layout["minifilter"]
        disk_2d = layout["disk"]
        dash = layout["dash"]

        # ═══ ЧАСТЬ 1: Архитектура ═══════════════════════
        title = Text(
            "Архитектура: User Mode → Kernel Mode → Disk",
            font=FONT, font_size=22, color=WHITE,
        ).to_edge(UP, buff=0.2)
        self.play(FadeIn(title, run_time=0.5))

        # Граница
        self.play(GrowFromCenter(boundary[0]), FadeIn(boundary[1], boundary[2]), run_time=0.8)

        # User Mode — блоки по одному
        for block in um:
            self.play(FadeIn(block, shift=DOWN * 0.12), run_time=0.25)

        # Kernel Mode — стек по одному
        for block in km_stack:
            self.play(FadeIn(block, shift=UP * 0.12), run_time=0.25)

        # Минифильтр + связь
        self.play(FadeIn(minifilter, shift=LEFT * 0.2), Create(dash), run_time=0.5)

        # Диск
        self.play(FadeIn(disk_2d, shift=UP * 0.1), run_time=0.3)

        # Подписи архитектуры
        cap = show_caption(
            self,
            "IRP содержит массив IO_STACK_LOCATION — по одному для каждого драйвера в стеке",
        )
        self.wait(2)
        hide_caption(self, cap)

        cap2 = show_caption(
            self,
            "Минифильтр регистрирует callback-и через FltRegisterFilter(),\n "
            "fltmgr.sys вызывает их при прохождении IRP",
        )
        self.wait(2)
        hide_caption(self, cap2)

        # Смена заголовка
        title2 = Text(
            "Операция ЗАПИСИ (Write) — полный путь",
            font=FONT, font_size=22, color=WHITE,
        ).to_edge(UP, buff=0.2)
        self.play(Transform(title, title2), run_time=0.5)
        self.wait(0.3)

        # ═══ ЧАСТЬ 2: Write flow ════════════════════════

        # Фаза: fwrite()
        code_label = Text(
            'fwrite(buf, 1, size, f);',
            font=FONT, font_size=12, color=PLAINTEXT_COLOR,
        ).next_to(um[0], RIGHT, buff=0.15)
        self.play(FadeIn(code_label, run_time=0.4))

        packet = create_data_packet('"Hello, World!"', PLAINTEXT_COLOR, font_size=13)
        packet.move_to(um[0].get_center())
        self.play(FadeIn(packet, run_time=0.3))

        cap = show_caption(self, "Вызов библиотечной функции fwrite()")
        self.wait(0.8)

        # Фаза: User mode chain — пакет движется по центрам блоков
        for i in range(len(um) - 1):
            self.play(packet.animate.move_to(um[i + 1].get_center()), run_time=0.35)
            highlight_block(self, um[i + 1], YELLOW, duration=0.15)

        hide_caption(self, cap)

        # Asm
        asm = VGroup(
            Text("mov eax, <NtWriteFile>", font=FONT, font_size=11, color=YELLOW),
            Text("syscall  ; Ring 3 -> Ring 0", font=FONT, font_size=11, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.04)
        asm.next_to(um[-1], RIGHT, buff=0.3)
        self.play(FadeIn(asm, run_time=0.4))
        self.wait(0.4)

        # Пересечение границы
        cap2 = show_caption(self, "SYSCALL — переход из User Mode (Ring 3) в Kernel Mode (Ring 0)")
        animate_boundary_cross(self, boundary, packet, km_stack[0].get_center())
        self.play(FadeOut(asm), FadeOut(code_label), run_time=0.3)
        hide_caption(self, cap2)

        # Фаза: I/O Manager создаёт IRP
        highlight_block(self, km_stack[0], KERNEL_MODE_COLORS["io_manager"], duration=0.3)
        cap3 = show_caption(self, "I/O Manager создаёт IRP в NonPagedPool (невыгружаемая память ядра)")

        irp_card = create_irp_card("IRP_MJ_WRITE", show_stack_locations=True)
        irp_card.scale(0.8).next_to(km_stack[0], RIGHT + UP*2, buff=0.6)
        
        # Возможно нужна стрелка!

        self.play(
            FadeOut(packet, run_time=0.3),
            FadeIn(irp_card, shift=UP * 0.2, run_time=0.8),
        )
        self.wait(1.5)
        hide_caption(self, cap3)

        irp_token = create_irp_token("IRP_MJ_WRITE")
        irp_token.move_to(km_stack[0].get_center())
        self.play(FadeOut(irp_card, run_time=0.3), FadeIn(irp_token, run_time=0.3))

        # Фаза: IRP вниз по стеку
        # fltmgr.sys
        self.play(irp_token.animate.move_to(km_stack[1].get_center()), run_time=0.5)
        highlight_block(self, km_stack[1], KERNEL_MODE_COLORS["fltmgr"], duration=0.3)
        cap4 = show_caption(self, "Filter Manager вызывает PreOperation callback минифильтра")
        self.wait(0.5)

        # PassThrough.sys — PreOperation
        self.play(irp_token.animate.move_to(minifilter.get_center()), run_time=0.5)
        highlight_block(self, minifilter, CIPHERTEXT_COLOR, duration=0.3)
        hide_caption(self, cap4)

        cap5 = show_caption(self, "PtPreOperationPassThrough() — проверка расширения файла")
        ext_check = show_extension_check(self, minifilter.get_center() + RIGHT + UP*2, "IRP_MJ_WRITE")
        self.wait(0.5)
        hide_caption(self, cap5)
        
        # Возможно нужна стрелка!

        # Шифрование
        cap6 = show_caption(self, "Минифильтр шифрует WriteBuffer алгоритмом AES-256")
        plain_packet = create_data_packet('"Hello, World!"', PLAINTEXT_COLOR, font_size=13)
        plain_packet.next_to(minifilter, DOWN, buff=0.2)
        self.play(FadeIn(plain_packet, run_time=1))

        animate_crypto(self, plain_packet, "encrypt", '"\\x8a\\x3c\\xff..."', CIPHERTEXT_COLOR)
        self.wait(0.5)
        self.play(FadeOut(ext_check, run_time=1))
        hide_caption(self, cap6)

        # Обратно в стек → NTFS → volmgr → disk
        self.play(irp_token.animate.move_to(km_stack[1].get_center()), run_time=0.3)

        self.play(irp_token.animate.move_to(km_stack[2].get_center()), run_time=0.4)
        highlight_block(self, km_stack[2], GRAY, duration=0.2)
        cap7 = show_caption(self, "NTFS.sys: файловое смещение -> кластеры MFT ($DATA -> Cluster Run)")
        self.wait(0.8)
        hide_caption(self, cap7)

        self.play(irp_token.animate.move_to(km_stack[3].get_center()), run_time=0.4)
        highlight_block(self, km_stack[3], GRAY, duration=0.2)
        cap8 = show_caption(self, "volmgr.sys: кластер -> LBA")
        self.wait(0.5)
        hide_caption(self, cap8)

        self.play(irp_token.animate.move_to(km_stack[4].get_center()), run_time=0.4)
        highlight_block(self, km_stack[4], GRAY, duration=0.2)
        cap9 = show_caption(self, "disk.sys: формирует SCSI WRITE(10)")
        self.wait(0.5)
        hide_caption(self, cap9)

        # Фаза: Данные на диск
        cipher_packet = plain_packet
        self.play(
            irp_token.animate.move_to(disk_2d.get_center()),
            cipher_packet.animate.move_to(disk_2d.get_center()),
            run_time=0.6,
        )
        sectors = disk_2d[4]
        self.play(
            *[s.animate.set_fill(color=CIPHERTEXT_COLOR, opacity=0.6) for s in sectors],
            run_time=0.5,
        )
        cap10 = show_caption(self, "На диске хранится шифротекст — недоступен без минифильтра")
        self.wait(1.5)
        self.play(FadeOut(cipher_packet, run_time=0.3))
        hide_caption(self, cap10)

        # Фаза: Completion — обратный путь
        cap11 = show_caption(self, "IRP Completion: обратный путь вверх по стеку")
        for block in reversed(km_stack[1:]):
            self.play(irp_token.animate.move_to(block.get_center()), run_time=0.3)

        self.play(irp_token.animate.move_to(minifilter.get_center()), run_time=0.3)
        postop_check = show_postop_write(self, minifilter.get_center() + RIGHT + UP*2)
        # post_label = Text(
        #     "PostOp Write: FLT_POSTOP_FINISHED_PROCESSING\n(шифрование уже выполнено в Pre)",
        #     font=FONT, font_size=11, color=GRAY_B,
        # ).next_to(minifilter, LEFT, buff=0.3)
        # self.play(FadeIn(post_label, run_time=0.4))
        # self.wait(0.8)
        self.play(FadeOut(postop_check, run_time=1))
        hide_caption(self, cap11)

        # IoStatus = SUCCESS, возврат в User Mode
        self.play(irp_token.animate.move_to(km_stack[0].get_center()), run_time=0.3)
        status_label = Text("IoStatus = STATUS_SUCCESS", font=FONT, font_size=12, color=PLAINTEXT_COLOR)
        status_label.next_to(km_stack[0], RIGHT, buff=0.3)
        self.play(FadeIn(status_label, run_time=0.3))

        cap12 = show_caption(self, "fwrite() возвращает управление — запись завершена")
        animate_boundary_cross(self, boundary, irp_token, um[-1].get_center())

        self.play(FadeOut(irp_token), FadeOut(status_label), run_time=0.3)
        self.wait(0.5)
        hide_caption(self, cap12)

        # ═══ ЧАСТЬ 3: Read flow ═════════════════════════

        # Смена заголовка
        title3 = Text(
            "Операция ЧТЕНИЯ (Read) — обратный путь",
            font=FONT, font_size=22, color=WHITE,
        ).to_edge(UP, buff=0.2)
        self.play(Transform(title, title3), run_time=0.5)
        self.wait(0.3)

        # Фаза: fread() → SYSCALL → IRP (ускоренно)
        code_label_r = Text(
            'fread(buf, 1, size, f);',
            font=FONT, font_size=12, color=PLAINTEXT_COLOR,
        ).next_to(um[0], RIGHT, buff=0.15)
        self.play(FadeIn(code_label_r, run_time=0.3))

        cap_r1 = show_caption(self, "fread -> ReadFile -> NtReadFile -> SYSCALL -> I/O Manager создаёт IRP")

        irp_token_r = create_irp_token("IRP_MJ_READ")
        irp_token_r.move_to(um[0].get_center())
        self.play(FadeIn(irp_token_r, run_time=0.2))

        for block in um[1:]:
            self.play(irp_token_r.animate.move_to(block.get_center()), run_time=0.15)

        animate_boundary_cross(self, boundary, irp_token_r, km_stack[0].get_center(), duration=0.5)
        self.play(FadeOut(code_label_r, run_time=0.2))
        hide_caption(self, cap_r1)

        # Фаза: IRP вниз (PreOperation)
        cap_r2 = show_caption(self, "PreOperation для Read: минифильтр пропускает (расшифровка будет в Post)")

        self.play(irp_token_r.animate.move_to(km_stack[1].get_center()), run_time=0.3)
        highlight_block(self, km_stack[1], KERNEL_MODE_COLORS["fltmgr"], duration=0.2)

        self.play(irp_token_r.animate.move_to(minifilter.get_center()), run_time=0.3)
        # pre_label = Text(
        #     "Pre: FLT_PREOP_SUCCESS_WITH_CALLBACK\n(расшифруем после чтения с диска)",
        #     font=FONT, font_size=10, color=GRAY_B,
        # ).next_to(minifilter, LEFT, buff=0.2)
        # self.play(FadeIn(pre_label, run_time=0.3))
        # self.wait(0.6)
        # self.play(FadeOut(pre_label, run_time=0.2))
        preflt_check = show_preflt_write(self, minifilter.get_center() + RIGHT + UP*2)
        self.play(FadeOut(preflt_check, run_time=1))

        self.play(irp_token_r.animate.move_to(km_stack[1].get_center()), run_time=0.2)
        for block in km_stack[2:]:
            self.play(irp_token_r.animate.move_to(block.get_center()), run_time=0.25)

        hide_caption(self, cap_r2)

        # Фаза: Диск возвращает шифротекст
        self.play(irp_token_r.animate.move_to(disk_2d.get_center()), run_time=0.3)
        cap_r3 = show_caption(self, "Диск возвращает зашифрованные данные")

        cipher_packet_r = create_data_packet('"\\x8a\\x3c\\xff..."', CIPHERTEXT_COLOR, font_size=13)
        cipher_packet_r.move_to(disk_2d.get_center())
        self.play(FadeIn(cipher_packet_r, shift=UP * 0.2, run_time=0.4))
        self.wait(0.5)
        hide_caption(self, cap_r3)

        # Фаза: IRP вверх → PostOperation в минифильтре
        cap_r4 = show_caption(self, "IRP Completion: данные поднимаются вверх по стеку")

        for block in reversed(km_stack[2:]):
            self.play(
                irp_token_r.animate.move_to(block.get_center()),
                cipher_packet_r.animate.move_to(block.get_center()),
                run_time=0.25,
            )
        self.play(
            irp_token_r.animate.move_to(km_stack[1].get_center()),
            cipher_packet_r.animate.move_to(km_stack[1].get_center()),
            run_time=0.3,
        )
        hide_caption(self, cap_r4)

        # → minifilter PostOperation
        self.play(
            irp_token_r.animate.move_to(minifilter.get_center()),
            cipher_packet_r.animate.next_to(minifilter, DOWN, buff=0.2),
            run_time=0.4,
        )
        highlight_block(self, minifilter, CIPHERTEXT_COLOR, duration=0.3)

        cap_r5 = show_caption(self, "PtPostOperationPassThrough() — расшифровка ReadBuffer")
        ext_check_r = show_extension_check(self, minifilter.get_center() + RIGHT + UP*2, "IRP_MJ_READ")
        self.wait(0.5)

        # Расшифровка
        animate_crypto(self, cipher_packet_r, "decrypt", '"Hello, World!"', PLAINTEXT_COLOR)
        self.wait(0.5)
        self.play(FadeOut(ext_check_r, run_time=1))
        hide_caption(self, cap_r5)

        cap_r6 = show_caption(self, "Минифильтр расшифровал ReadBuffer — прозрачно для приложения")

        # Фаза: Возврат приложению
        self.play(irp_token_r.animate.move_to(km_stack[0].get_center()), run_time=0.3)
        animate_boundary_cross(self, boundary, irp_token_r, um[-1].get_center(), duration=0.5)
        self.play(cipher_packet_r.animate.move_to(um[-1].get_center()), run_time=0.3)

        for block in reversed(um[:-1]):
            self.play(
                irp_token_r.animate.move_to(block.get_center()),
                cipher_packet_r.animate.move_to(block.get_center()),
                run_time=0.15,
            )
        hide_caption(self, cap_r6)

        # Результат
        result = Text(
            '> Hello, World!',
            font=FONT, font_size=16, color=PLAINTEXT_COLOR,
        ).next_to(um[0], RIGHT, buff=0.3)
        self.play(FadeIn(result, run_time=0.4))

        cap_r7 = show_caption(self, "Приложение получает расшифрованные данные, не зная о шифровании")
        self.wait(2)
        hide_caption(self, cap_r7)
        self.play(FadeOut(irp_token_r), FadeOut(cipher_packet_r), FadeOut(result), run_time=0.3)

        scene_transition(self)


# ═══════════════════════════════════════════════════════════
#  Сцена 4 — Демонстрация прозрачности (~10 сек)
# ═══════════════════════════════════════════════════════════
class Scene4Transparency(Scene):
    def construct(self):
        title = Text(
            "Прозрачное шифрование: с драйвером vs без",
            font=FONT, font_size=22, color=WHITE,
        ).to_edge(UP, buff=0.3)
        self.play(FadeIn(title, run_time=0.4))

        divider = Line(UP * 2.5, DOWN * 2, color=GRAY, stroke_width=1)
        self.play(Create(divider, run_time=0.3))

        # ── Левая сторона: с драйвером ──
        left_title = Text("С загруженным\nPassThrough.sys", font=FONT, font_size=16, color=PLAINTEXT_COLOR)
        left_title.move_to(LEFT * 3.5 + UP * 1.5)

        left_app = create_driver_block("test_app.exe", USER_MODE_COLORS["app"], width=3, height=0.4)
        left_app.move_to(LEFT * 3.5 + UP * 0.5)

        left_arrow = Arrow(left_app.get_bottom(), left_app.get_bottom() + DOWN * 0.6,
                           buff=0, stroke_width=1.5, color=GRAY_B)

        left_file = create_data_packet("test.lab2ext", GRAY, font_size=12)
        left_file.move_to(LEFT * 3.5 + DOWN * 0.5)

        left_arrow2 = Arrow(left_file.get_bottom(), left_file.get_bottom() + DOWN * 0.6,
                            buff=0, stroke_width=1.5, color=GRAY_B)

        left_result = Text(
            '> Hello, World!',
            font=FONT, font_size=18, color=PLAINTEXT_COLOR,
        ).move_to(LEFT * 3.5 + DOWN * 1.6)

        left_disk_label = Text(
            "На диске: зашифровано",
            font=FONT, font_size=11, color=GRAY_B,
        ).move_to(LEFT * 3.5 + DOWN * 2.3)

        # ── Правая сторона: без драйвера ──
        right_title = Text("Без драйвера /\nДругая машина", font=FONT, font_size=16, color=CIPHERTEXT_COLOR)
        right_title.move_to(RIGHT * 3.5 + UP * 1.5)

        right_app = create_driver_block("notepad.exe", "#888888", width=3, height=0.4)
        right_app.move_to(RIGHT * 3.5 + UP * 0.5)

        right_arrow = Arrow(right_app.get_bottom(), right_app.get_bottom() + DOWN * 0.6,
                            buff=0, stroke_width=1.5, color=GRAY_B)

        right_file = create_data_packet("test.lab2ext", GRAY, font_size=12)
        right_file.move_to(RIGHT * 3.5 + DOWN * 0.5)

        right_arrow2 = Arrow(right_file.get_bottom(), right_file.get_bottom() + DOWN * 0.6,
                             buff=0, stroke_width=1.5, color=GRAY_B)

        right_result = Text(
            '> \\x8a\\x3c\\xff\\xb1\\x90...',
            font=FONT, font_size=18, color=CIPHERTEXT_COLOR,
        ).move_to(RIGHT * 3.5 + DOWN * 1.6)

        right_disk_label = Text(
            "На диске: тот же шифротекст",
            font=FONT, font_size=11, color=GRAY_B,
        ).move_to(RIGHT * 3.5 + DOWN * 2.3)

        # Анимация
        left_group = VGroup(left_title, left_app, left_arrow, left_file, left_arrow2, left_result, left_disk_label)
        right_group = VGroup(right_title, right_app, right_arrow, right_file, right_arrow2, right_result, right_disk_label)

        self.play(FadeIn(left_group, shift=RIGHT * 0.3), run_time=0.8)
        self.wait(0.5)
        self.play(FadeIn(right_group, shift=LEFT * 0.3), run_time=0.8)

        # Рамки акцента
        left_box = SurroundingRectangle(left_result, color=PLAINTEXT_COLOR, buff=0.15, stroke_width=2)
        right_box = SurroundingRectangle(right_result, color=CIPHERTEXT_COLOR, buff=0.15, stroke_width=2)
        self.play(Create(left_box), Create(right_box), run_time=0.5)

        cap = show_caption(self, "Данные доступны только при загруженном минифильтре с правильным ключом AES-256")
        self.wait(3)
        hide_caption(self, cap)

        scene_transition(self)


# ═══════════════════════════════════════════════════════════
#  Сцена 5 — fltmc и WinObj (~10 сек)
# ═══════════════════════════════════════════════════════════
class Scene5Fltmc(Scene):
    def construct(self):
        title = Text(
            "Место минифильтра в стеке — fltmc и WinObj",
            font=FONT, font_size=22, color=WHITE,
        ).to_edge(UP, buff=0.3)
        self.play(FadeIn(title, run_time=0.4))

        # ── fltmc вывод ──
        fltmc_header = Text("C:\\> fltmc", font=FONT, font_size=16, color=GRAY_A)
        fltmc_header.move_to(LEFT * 3 + UP * 2)

        table_header = Text(
            "Filter Name      Num Instances  Altitude  Frame",
            font=FONT, font_size=12, color=GRAY_B,
        )
        table_sep = Text(
            "─────────────    ─────────────  ────────  ─────",
            font=FONT, font_size=12, color=GRAY_C,
        )
        table_row = Text(
            "PassThrough            3        145000      0",
            font=FONT, font_size=12, color=PLAINTEXT_COLOR,
        )

        fltmc_table = VGroup(fltmc_header, table_header, table_sep, table_row)
        fltmc_table.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        fltmc_table.move_to(LEFT * 2.5 + UP * 0.8)

        fltmc_bg = SurroundingRectangle(
            fltmc_table, buff=0.2,
            fill_color="#0c0c0c", fill_opacity=0.8,
            stroke_color=GRAY, stroke_width=1,
            corner_radius=0.05,
        )

        self.play(FadeIn(fltmc_bg), run_time=0.3)
        for line in fltmc_table:
            self.play(FadeIn(line, run_time=0.3))
        self.wait(1)

        # ── Схема связи fltmgr ↔ minifilter ──
        fltmgr_block = create_driver_block("fltmgr.sys", KERNEL_MODE_COLORS["fltmgr"], width=3, height=0.5)
        fltmgr_block.move_to(RIGHT * 2 + DOWN * 0.5)

        mini_block = create_driver_block("PassThrough.sys", KERNEL_MODE_COLORS["minifilter"], width=3, height=0.5)
        mini_block[0].set_stroke(color=CIPHERTEXT_COLOR, width=3)
        mini_block.move_to(RIGHT * 2 + DOWN * 1.5)

        dash = DashedLine(
            fltmgr_block.get_bottom(), mini_block.get_top(),
            dash_length=0.08, color=CIPHERTEXT_COLOR, stroke_width=2,
        )

        self.play(FadeIn(fltmgr_block), FadeIn(mini_block), Create(dash), run_time=0.5)

        # Пояснения
        labels = VGroup(
            Text("Legacy фильтр ФС (часть device stack)", font=FONT, font_size=10, color=GRAY_B),
            Text("Минифильтр: altitude 145000", font=FONT, font_size=10, color=GRAY_B),
            Text("(FSFilter Encryption: 140000-149999)", font=FONT, font_size=10, color=GRAY_C),
        )
        labels[0].next_to(fltmgr_block, RIGHT, buff=0.2)
        labels[1].next_to(mini_block, RIGHT, buff=0.2)
        labels[2].next_to(labels[1], DOWN, buff=0.04, aligned_edge=LEFT)
        self.play(FadeIn(labels, run_time=0.4))

        # Ключевое пояснение
        key_text = VGroup(
            Text("Минифильтр НЕ вставляется в device stack.", font=FONT, font_size=13, color=WHITE),
            Text("Он регистрирует Pre/Post callback-функции", font=FONT, font_size=13, color=WHITE),
            Text("через FltRegisterFilter(), а fltmgr.sys", font=FONT, font_size=13, color=WHITE),
            Text("вызывает их при прохождении IRP.", font=FONT, font_size=13, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        key_text.move_to(DOWN * 2.8)

        key_bg = SurroundingRectangle(
            key_text, buff=0.15,
            fill_color="#1a0000", fill_opacity=0.6,
            stroke_color=CIPHERTEXT_COLOR, stroke_width=1,
            corner_radius=0.06,
        )
        self.play(FadeIn(key_bg), FadeIn(key_text), run_time=0.6)
        self.wait(3)

        # Финальная надпись
        scene_transition(self)

        final = Text(
            "ЛР2: Прозрачное шифрование\nминифильтр-драйвером Windows",
            font=FONT, font_size=26, color=WHITE,
        )
        self.play(FadeIn(final, run_time=1))
        self.wait(2)
        self.play(FadeOut(final, run_time=0.8))
