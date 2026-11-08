import tkinter as tk
from tkinter import ttk

import customtkinter as ctk


BG = "#F3F6FA"
PRIMARY = "#2457A7"
TEXT = "#1F2937"
MUTED = "#64748B"


def configure_treeview(parent: tk.Misc, columns: tuple[str, ...], headings: tuple[str, ...]):
    style = ttk.Style(parent)
    style.configure(
        "DonQuelo.Treeview", rowheight=30, font=("Segoe UI", 10),
        background="#FFFFFF", fieldbackground="#FFFFFF", foreground=TEXT,
    )
    style.configure(
        "DonQuelo.Treeview.Heading", font=("Segoe UI", 10, "bold"),
        background="#E9EFF7", foreground=TEXT,
    )
    style.map("DonQuelo.Treeview", background=[("selected", "#D5E6FF")])
    tree = ttk.Treeview(parent, columns=columns, show="headings", style="DonQuelo.Treeview")
    for column, heading in zip(columns, headings):
        tree.heading(column, text=heading)
        tree.column(column, width=110, minwidth=75, anchor="center")
    return tree


def section_title(parent, text: str):
    return ctk.CTkLabel(
        parent, text=text, font=ctk.CTkFont(size=22, weight="bold"),
        text_color=TEXT, anchor="w",
    )
