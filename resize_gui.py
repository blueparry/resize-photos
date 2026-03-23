#!/usr/bin/env python3
"""
Interface grafica para redimensionar fotos.

Simples e facil de usar — texto grande, botoes claros.
Funciona no macOS, Windows e Linux via tkinter.
"""

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    from resize import (
        DEFAULT_HEIGHT,
        DEFAULT_QUALITY,
        DEFAULT_WIDTH,
        find_images,
        resize_all,
    )
    from icon import create_icon
    from updater import check_for_update, apply_update
    from version import __version__
except ImportError:
    print("Erro: resize.py, icon.py e updater.py devem estar na mesma pasta que resize_gui.py")
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
DESKTOP_DIR = Path.home() / "Desktop"

# Fonts
FONT_TITLE = ("Helvetica", 22, "bold")
FONT_LARGE = ("Helvetica", 15)
FONT_MEDIUM = ("Helvetica", 13)
FONT_BTN_BIG = ("Helvetica", 16, "bold")
FONT_BTN = ("Helvetica", 13, "bold")
FONT_SMALL = ("Helvetica", 11)
FONT_LOG = ("Courier", 11)

# Size presets (label, width, height)
SIZE_PRESETS = [
    ("1024 x 768  (padrao)", 1024, 768),
    ("1280 x 960", 1280, 960),
    ("1920 x 1080  (Full HD)", 1920, 1080),
    ("800 x 600  (pequeno)", 800, 600),
    ("640 x 480  (muito pequeno)", 640, 480),
    ("Personalizado...", 0, 0),
]

# Colors
BG = "#EEF2F7"
SECTION_BG = "#FFFFFF"
ACCENT_BLUE = "#3B82F6"
ACCENT_BLUE_HOVER = "#2563EB"
ACCENT_GREEN = "#22C55E"
ACCENT_GREEN_HOVER = "#16A34A"
TEXT_DARK = "#1E293B"
TEXT_MID = "#475569"
TEXT_LIGHT = "#94A3B8"
BORDER = "#CBD5E1"
PROGRESS_BG = "#E2E8F0"
PROGRESS_FILL = "#3B82F6"


def setup_styles():
    """Configure ttk styles using clam theme for cross-platform color support."""
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(".", background=BG, foreground=TEXT_DARK)

    style.configure("Title.TLabel", font=FONT_TITLE, background=BG, foreground=ACCENT_BLUE)

    style.configure("Section.TLabelframe", background=SECTION_BG, relief="solid",
                     borderwidth=1, bordercolor=BORDER)
    style.configure("Section.TLabelframe.Label", font=FONT_MEDIUM,
                     background=BG, foreground=TEXT_DARK)

    style.configure("FolderPath.TLabel", font=FONT_MEDIUM,
                     background=SECTION_BG, foreground=TEXT_DARK)
    style.configure("PhotoCount.TLabel", font=FONT_SMALL,
                     background=SECTION_BG, foreground=TEXT_MID)
    style.configure("Status.TLabel", font=FONT_MEDIUM,
                     background=BG, foreground=TEXT_MID)

    # Blue button (folder)
    style.configure("Blue.TButton", font=FONT_BTN, foreground="#FFFFFF",
                     background=ACCENT_BLUE, borderwidth=0, padding=(20, 10))
    style.map("Blue.TButton",
              background=[("active", ACCENT_BLUE_HOVER), ("disabled", BORDER)],
              foreground=[("disabled", TEXT_LIGHT)])

    # Green button (resize)
    style.configure("Green.TButton", font=FONT_BTN_BIG, foreground="#FFFFFF",
                     background=ACCENT_GREEN, borderwidth=0, padding=(40, 14))
    style.map("Green.TButton",
              background=[("active", ACCENT_GREEN_HOVER), ("disabled", "#94A3B8")],
              foreground=[("disabled", "#FFFFFF")])

    # Close button
    style.configure("Close.TButton", font=FONT_MEDIUM, foreground=TEXT_MID,
                     background="#E2E8F0", borderwidth=0, padding=(20, 10))
    style.map("Close.TButton",
              background=[("active", BORDER)])

    # Toggle link
    style.configure("Link.TButton", font=FONT_SMALL, foreground=ACCENT_BLUE,
                     background=BG, borderwidth=0, padding=(0, 4))
    style.map("Link.TButton",
              foreground=[("active", ACCENT_BLUE_HOVER)],
              background=[("active", BG)])

    # Update button (small blue link style)
    style.configure("Update.TButton", font=("Helvetica", 9), foreground=ACCENT_BLUE,
                     background=BG, borderwidth=0, padding=(0, 2))
    style.map("Update.TButton",
              foreground=[("active", ACCENT_BLUE_HOVER), ("disabled", BORDER)])

    # Checkbox
    style.configure("Backup.TCheckbutton", font=FONT_MEDIUM,
                     background=BG, foreground=TEXT_DARK)
    style.map("Backup.TCheckbutton", background=[("active", BG)])


def _pil_to_png_data(pil_image):
    """Convert a PIL Image to PNG bytes for tkinter PhotoImage."""
    import io
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return buffer.getvalue()


def create_app():
    """Build and return the main application window."""
    root = tk.Tk()
    root.title("Redimensionar Fotos")
    root.configure(bg=BG)
    root.resizable(False, False)

    # Set custom app icon
    icon_img = create_icon(256)
    icon_photo = tk.PhotoImage(data=_pil_to_png_data(icon_img))
    root.iconphoto(True, icon_photo)

    setup_styles()

    # State
    default_folder = str(DESKTOP_DIR) if DESKTOP_DIR.is_dir() else str(SCRIPT_DIR)
    folder_var = tk.StringVar(value=default_folder)
    preset_var = tk.StringVar(value=SIZE_PRESETS[0][0])
    custom_width_var = tk.StringVar(value=str(DEFAULT_WIDTH))
    custom_height_var = tk.StringVar(value=str(DEFAULT_HEIGHT))
    quality_var = tk.StringVar(value=str(DEFAULT_QUALITY))
    backup_var = tk.BooleanVar(value=False)
    is_running = {"value": False}

    # Main container
    main_frame = ttk.Frame(root, padding=(30, 20, 30, 3))
    main_frame.grid(row=0, column=0, sticky="nsew")

    # Title
    ttk.Label(
        main_frame, text="Redimensionar Fotos", style="Title.TLabel",
    ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

    # ============================================================
    # SECTION 1: Folder
    # ============================================================
    folder_section = ttk.LabelFrame(
        main_frame, text="  1. Escolha a pasta com as fotos  ",
        style="Section.TLabelframe", padding=(15, 15),
    )
    folder_section.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))

    ttk.Label(
        folder_section, textvariable=folder_var, style="FolderPath.TLabel",
        wraplength=420,
    ).grid(row=0, column=0, sticky="ew", padx=(0, 10))

    image_count_var = tk.StringVar(value="")
    ttk.Label(
        folder_section, textvariable=image_count_var, style="PhotoCount.TLabel",
    ).grid(row=1, column=0, sticky="w", pady=(5, 0))

    def update_image_count():
        folder = folder_var.get()
        if Path(folder).is_dir():
            count = len(find_images(folder))
            if count == 0:
                image_count_var.set("Nenhuma foto encontrada nesta pasta")
            elif count == 1:
                image_count_var.set("1 foto encontrada")
            else:
                image_count_var.set(f"{count} fotos encontradas")
        else:
            image_count_var.set("Pasta nao encontrada")

    def browse_folder():
        chosen = filedialog.askdirectory(
            initialdir=folder_var.get(),
            title="Selecione a pasta com as fotos",
        )
        if chosen:
            folder_var.set(chosen)
            update_image_count()

    ttk.Button(
        folder_section, text="Alterar Pasta", style="Blue.TButton",
        command=browse_folder,
    ).grid(row=0, column=1, rowspan=2, padx=(10, 0))

    folder_section.columnconfigure(0, weight=1)
    update_image_count()

    # ============================================================
    # SECTION 2: Size
    # ============================================================
    size_section = ttk.LabelFrame(
        main_frame, text="  2. Escolha o tamanho das fotos  ",
        style="Section.TLabelframe", padding=(15, 15),
    )
    size_section.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))

    preset_menu = tk.OptionMenu(
        size_section, preset_var, *[p[0] for p in SIZE_PRESETS],
    )
    preset_menu.configure(
        font=FONT_LARGE, width=30, bg=SECTION_BG, fg=TEXT_DARK,
        activebackground=ACCENT_BLUE, activeforeground="#FFFFFF",
        highlightthickness=1, highlightbackground=BORDER, relief="flat",
    )
    preset_menu["menu"].configure(
        font=FONT_MEDIUM, bg=SECTION_BG, fg=TEXT_DARK,
        activebackground=ACCENT_BLUE, activeforeground="#FFFFFF",
    )
    preset_menu.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 5))

    # Custom size fields (hidden by default)
    custom_frame = ttk.Frame(size_section)

    ttk.Label(custom_frame, text="Largura:", font=FONT_MEDIUM).grid(
        row=0, column=0, padx=(0, 5),
    )
    tk.Entry(
        custom_frame, textvariable=custom_width_var, font=FONT_LARGE,
        width=7, bg=SECTION_BG, fg=TEXT_DARK, relief="solid",
        highlightthickness=1, highlightcolor=ACCENT_BLUE,
    ).grid(row=0, column=1, padx=(0, 15))

    ttk.Label(custom_frame, text="Altura:", font=FONT_MEDIUM).grid(
        row=0, column=2, padx=(0, 5),
    )
    tk.Entry(
        custom_frame, textvariable=custom_height_var, font=FONT_LARGE,
        width=7, bg=SECTION_BG, fg=TEXT_DARK, relief="solid",
        highlightthickness=1, highlightcolor=ACCENT_BLUE,
    ).grid(row=0, column=3)

    def on_preset_change(*_args):
        selected = preset_var.get()
        if selected == "Personalizado...":
            custom_frame.grid(row=1, column=0, columnspan=4, sticky="w", pady=(10, 0))
        else:
            custom_frame.grid_forget()
            for label, w, h in SIZE_PRESETS:
                if label == selected:
                    custom_width_var.set(str(w))
                    custom_height_var.set(str(h))
                    break

    preset_var.trace_add("write", on_preset_change)

    # Backup checkbox
    ttk.Checkbutton(
        main_frame, text="Guardar fotos originais na subpasta 'originals'",
        variable=backup_var, style="Backup.TCheckbutton",
    ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 10))

    # ============================================================
    # SECTION 3: Action
    # ============================================================
    action_frame = ttk.Frame(main_frame)
    action_frame.grid(row=4, column=0, columnspan=2, pady=(5, 10))

    # Progress bar (canvas for custom look)
    progress_canvas = tk.Canvas(
        action_frame, width=500, height=26, bg=PROGRESS_BG,
        highlightthickness=0, relief="flat",
    )
    progress_canvas.grid(row=0, column=0, columnspan=2, pady=(0, 8))
    # Rounded rectangle effect
    progress_fill = progress_canvas.create_rectangle(
        0, 0, 0, 26, fill=PROGRESS_FILL, width=0,
    )

    status_var = tk.StringVar(value="Pronto - clique no botao abaixo para iniciar")
    ttk.Label(
        action_frame, textvariable=status_var, style="Status.TLabel",
    ).grid(row=1, column=0, columnspan=2, pady=(0, 12))

    def update_progress_bar(pct):
        fill_width = int(500 * pct / 100)
        progress_canvas.coords(progress_fill, 0, 0, fill_width, 26)

    def get_target_size():
        selected = preset_var.get()
        if selected != "Personalizado...":
            for label, w, h in SIZE_PRESETS:
                if label == selected:
                    return w, h

        try:
            w = int(custom_width_var.get())
            h = int(custom_height_var.get())
        except ValueError:
            messagebox.showerror(
                "Tamanho Invalido",
                "Por favor, insira numeros validos para largura e altura.",
            )
            return None

        if w < 1 or h < 1:
            messagebox.showerror(
                "Tamanho Invalido",
                "Largura e altura devem ser maiores que zero.",
            )
            return None
        return w, h

    def run_resize():
        if is_running["value"]:
            return

        folder = folder_var.get()
        if not Path(folder).is_dir():
            messagebox.showerror(
                "Pasta Nao Encontrada",
                f"Nao foi possivel encontrar a pasta:\n{folder}\n\n"
                "Por favor, escolha uma pasta valida.",
            )
            return

        size = get_target_size()
        if size is None:
            return

        target_width, target_height = size

        images = find_images(folder)
        if not images:
            messagebox.showinfo(
                "Nenhuma Foto Encontrada",
                "Nenhuma foto foi encontrada na pasta selecionada.\n\n"
                "As fotos devem ser arquivos .jpg, .jpeg, .png, .webp, .tiff ou .bmp.",
            )
            return

        try:
            quality = int(quality_var.get())
            quality = max(1, min(100, quality))
        except ValueError:
            quality = DEFAULT_QUALITY

        image_count = len(images)
        is_running["value"] = True
        resize_btn.configure(state="disabled")
        update_progress_bar(0)

        # Clear log
        log_text.configure(state="normal")
        log_text.delete("1.0", "end")
        log_text.configure(state="disabled")

        status_var.set(f"Redimensionando {image_count} foto(s)... aguarde")
        processed = {"count": 0}

        def on_progress(result):
            processed["count"] += 1
            pct = (processed["count"] / image_count) * 100

            if result["status"] == "resized":
                orig = result["original_size"]
                new = result["new_size"]
                msg = (f"Redimensionada: {result['name']}  "
                       f"({orig[0]}x{orig[1]} -> {new[0]}x{new[1]})")
            elif result["status"] == "skipped":
                msg = f"Ja esta pequena: {result['name']}"
            else:
                msg = f"Erro: {result['name']}"

            root.after(0, lambda m=msg, p=pct: _update_ui(m, p))

        def _update_ui(msg, pct):
            log_text.configure(state="normal")
            log_text.insert("end", msg + "\n")
            log_text.see("end")
            log_text.configure(state="disabled")
            update_progress_bar(pct)

        def _on_done(summary):
            root.after(0, lambda: _finish(summary))

        def _finish(summary):
            is_running["value"] = False
            resize_btn.configure(state="normal")
            update_progress_bar(100)

            done_msg = f"Concluido!  {summary['resized']} redimensionada(s)"
            if summary["skipped"] > 0:
                done_msg += f",  {summary['skipped']} ja pequena(s)"
            if summary["errors"] > 0:
                done_msg += f",  {summary['errors']} erro(s)"

            status_var.set(done_msg)
            update_image_count()

            finish_msg = (
                f"As fotos foram redimensionadas!\n\n"
                f"Redimensionadas: {summary['resized']}\n"
                f"Ja estavam pequenas: {summary['skipped']}\n"
                f"Erros: {summary['errors']}"
            )
            if backup_var.get():
                finish_msg += "\n\nAs fotos originais foram salvas na subpasta 'originals'."

            messagebox.showinfo("Concluido!", finish_msg)

        def _worker():
            try:
                summary = resize_all(
                    folder, target_width, target_height, quality,
                    no_backup=not backup_var.get(), on_progress=on_progress,
                )
                _on_done(summary)
            except Exception as e:
                root.after(0, lambda: _handle_error(str(e)))

        def _handle_error(err):
            is_running["value"] = False
            resize_btn.configure(state="normal")
            status_var.set("Algo deu errado")
            messagebox.showerror(
                "Erro",
                f"Algo deu errado ao redimensionar:\n\n{err}",
            )

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    resize_btn = ttk.Button(
        action_frame, text="   Redimensionar Fotos   ",
        style="Green.TButton", command=run_resize,
    )
    resize_btn.grid(row=2, column=0, pady=(0, 5))

    ttk.Button(
        action_frame, text="Fechar", style="Close.TButton",
        command=root.quit,
    ).grid(row=2, column=1, padx=(15, 0), pady=(0, 5))

    # ============================================================
    # Log (hidden by default)
    # ============================================================
    details_visible = {"value": False}

    def toggle_details():
        if details_visible["value"]:
            log_outer.grid_forget()
            toggle_btn.configure(text="Mostrar detalhes")
            details_visible["value"] = False
        else:
            log_outer.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(5, 0))
            toggle_btn.configure(text="Ocultar detalhes")
            details_visible["value"] = True

    toggle_btn = ttk.Button(
        main_frame, text="Mostrar detalhes", style="Link.TButton",
        command=toggle_details,
    )
    toggle_btn.grid(row=5, column=0, columnspan=2, sticky="w")

    log_outer = ttk.LabelFrame(
        main_frame, text="  Detalhes  ", style="Section.TLabelframe",
        padding=(10, 10),
    )

    log_text = tk.Text(
        log_outer, height=8, width=60, state="disabled",
        wrap="word", font=FONT_LOG, bg="#F8FAFC", fg=TEXT_DARK,
        relief="flat", highlightthickness=1, highlightbackground=BORDER,
    )
    log_scrollbar = ttk.Scrollbar(log_outer, orient="vertical", command=log_text.yview)
    log_text.configure(yscrollcommand=log_scrollbar.set)
    log_text.grid(row=0, column=0, sticky="nsew")
    log_scrollbar.grid(row=0, column=1, sticky="ns")
    log_outer.columnconfigure(0, weight=1)
    log_outer.rowconfigure(0, weight=1)

    # ============================================================
    # Update checker
    # ============================================================
    update_frame = ttk.Frame(main_frame)
    update_frame.grid(row=7, column=0, columnspan=2, sticky="sew", pady=(20, 0))

    update_status_var = tk.StringVar(value="")
    ttk.Label(
        update_frame, textvariable=update_status_var, font=("Helvetica", 9),
        foreground=TEXT_MID, background=BG,
    ).grid(row=1, column=0, columnspan=3, sticky="w")

    def do_check_update():
        update_btn.configure(state="disabled")
        update_status_var.set("Verificando...")

        def _worker():
            try:
                result = check_for_update()
                root.after(0, lambda: _on_check_result(result))
            except Exception as e:
                root.after(0, lambda: _on_check_error(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_check_result(result):
        update_btn.configure(state="normal")
        if result["available"]:
            update_status_var.set(f"Nova versao disponivel: {result['message']}")
            answer = messagebox.askyesno(
                "Atualizacao Disponivel",
                f"Uma nova versao foi encontrada!\n\n"
                f"{result['message']}\n\n"
                f"Deseja atualizar agora?",
            )
            if answer:
                do_apply_update(result["latest_sha"])
        else:
            update_status_var.set("Ja esta na versao mais recente!")

    def _on_check_error(err):
        update_btn.configure(state="normal")
        update_status_var.set("Erro ao verificar")
        messagebox.showerror(
            "Erro de Atualizacao",
            f"Nao foi possivel verificar atualizacoes:\n\n{err}\n\n"
            "Verifique sua conexao com a internet.",
        )

    def do_apply_update(sha):
        update_btn.configure(state="disabled")
        resize_btn.configure(state="disabled")
        update_status_var.set("Baixando atualizacao...")

        def on_progress(filename, index, total):
            if filename:
                root.after(0, lambda: update_status_var.set(
                    f"Baixando {filename}... ({index + 1}/{total})"
                ))

        def _worker():
            try:
                updated = apply_update(sha, on_progress=on_progress)
                root.after(0, lambda: _on_update_done(updated))
            except Exception as e:
                root.after(0, lambda: _on_update_error(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_update_done(updated):
        update_btn.configure(state="normal")
        resize_btn.configure(state="normal")
        update_status_var.set(f"Atualizado! ({len(updated)} arquivo(s))")
        messagebox.showinfo(
            "Atualizacao Concluida",
            f"Atualizacao instalada com sucesso!\n\n"
            f"Arquivos atualizados:\n"
            + "\n".join(f"  - {f}" for f in updated)
            + "\n\nPor favor, feche e abra o programa novamente.",
        )

    def _on_update_error(err):
        update_btn.configure(state="normal")
        resize_btn.configure(state="normal")
        update_status_var.set("Erro ao atualizar")
        messagebox.showerror(
            "Erro de Atualizacao",
            f"Nao foi possivel atualizar:\n\n{err}",
        )

    update_btn = ttk.Button(
        update_frame, text="Verificar Atualizacao",
        style="Update.TButton", command=do_check_update,
    )
    update_btn.grid(row=0, column=0, sticky="w")

    # Version label (bottom right, same row)
    ttk.Label(
        update_frame, text=f"v{__version__}", font=("Helvetica", 9),
        foreground=TEXT_LIGHT, background=BG,
    ).grid(row=0, column=2, sticky="e")

    update_frame.columnconfigure(1, weight=1)

    # Center window on screen
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"+{x}+{y}")

    return root


def main():
    root = create_app()
    root.mainloop()


if __name__ == "__main__":
    main()
