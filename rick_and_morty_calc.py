#!/usr/bin/env python3
"""
Rick & Morty Themed Calculator (tkinter)
Salve como: rick_and_morty_calc.py
Execute: python rick_and_morty_calc.py
"""

import tkinter as tk
from tkinter import font, messagebox
import ast
import operator
import random
import os

# ---------- Configurações de tema -----------
BG = "#0f1720"           # fundo escuro
PANEL = "#071017"        # painel dos botões
NEON_GREEN = "#7CFC00"   # verde neon
NEON_CYAN = "#00FFFF"    # ciano neon
ACCENT = "#9B59B6"       # roxo suave
TEXT = "#E6F9F2"         # texto claro

# Frases aleatórias estilo Rick
RICK_QUOTES = [
    "Wubba Lubba Dub Dub!",
    "Get Schwifty!",
    "I'm Mr. Meeseeks, look at me!",
    "Sometimes science is more art than science.",
    "Existence is pain to a Meeseeks.",
    "Nobody exists on purpose, nobody belongs anywhere."
]

# ---------- Avaliador seguro de expressões ----------
# Permitimos apenas operações aritméticas básicas (no eval direto)
ALLOWED_BINOP = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

ALLOWED_UNARYOP = {
    ast.UAdd: lambda x: x,
    ast.USub: operator.neg,
}

def safe_eval(expr: str):
    """
    Avalia expressões numéricas de forma segura usando ast.
    Permite números, + - * / ** % e parênteses.
    """
    expr = expr.strip()
    if not expr:
        raise ValueError("Expressão vazia")

    node = ast.parse(expr, mode='eval')

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type in ALLOWED_BINOP:
                return ALLOWED_BINOP[op_type](left, right)
            raise ValueError(f"Operador não permitido: {op_type}")
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op_type = type(node.op)
            if op_type in ALLOWED_UNARYOP:
                return ALLOWED_UNARYOP[op_type](operand)
            raise ValueError(f"Unary op não permitido: {op_type}")
        if isinstance(node, ast.Num):  # para Python < 3.8
            return node.n
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Constante não-numérica")
        if isinstance(node, ast.Call):
            raise ValueError("Chamadas de função não são permitidas")
        raise ValueError(f"Node não permitido: {type(node)}")

    return _eval(node)

# ---------- GUI ----------
class RickCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rick & Morty Calculator")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.geometry("360x520")
        # ícone opcional - se houver icon.ico na pasta
        try:
            if os.path.exists("icon.ico"):
                self.iconbitmap("icon.ico")
        except Exception:
            pass

        # Fonts
        self.big_font = font.Font(family="Helvetica", size=28, weight="bold")
        self.display_font = font.Font(family="Consolas", size=20)
        self.small_font = font.Font(family="Helvetica", size=10, weight="bold")

        # Top frame (imagem opcional + frase)
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=(12, 6))

        # Tenta carregar imagem rick.png (opcional)
        self.image_label = tk.Label(top, bg=BG)
        self.image_label.pack()
        if os.path.exists("rick.png"):
            try:
                img = tk.PhotoImage(file="rick.png")
                # reduzir se for grande
                img = img.subsample(max(1, img.width()//200), max(1, img.height()//120))
                self.image_label.configure(image=img)
                self.image_label.image = img
            except Exception:
                self.image_label.configure(text="(Imagem rick.png inválida)", fg=NEON_CYAN, bg=BG)

        # Frase do Rick
        self.quote_var = tk.StringVar(value=random.choice(RICK_QUOTES))
        quote_label = tk.Label(top, textvariable=self.quote_var, bg=BG, fg=NEON_CYAN, font=self.small_font)
        quote_label.pack(pady=(6,0))

        # Display
        self.display_var = tk.StringVar()
        display_frame = tk.Frame(self, bg=PANEL, padx=10, pady=10)
        display_frame.pack(fill="x", padx=12, pady=(8, 12))

        self.display = tk.Entry(display_frame, textvariable=self.display_var,
                                font=self.big_font, justify="right", bd=0, bg=PANEL, fg=TEXT,
                                insertbackground=TEXT)
        self.display.pack(fill="x")
        self.display_var.set("0")

        # Buttons
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(padx=12, pady=(0,12))

        buttons = [
            ['C', '⌫', '%', '/'],
            ['7','8','9','*'],
            ['4','5','6','-'],
            ['1','2','3','+'],
            ['+/-','0','.','=']
        ]

        for r, row in enumerate(buttons):
            row_frame = tk.Frame(btn_frame, bg=BG)
            row_frame.pack(fill="x", pady=6)
            for c, char in enumerate(row):
                btn = tk.Button(row_frame, text=char, command=lambda ch=char: self.on_button(ch),
                                font=self.display_font, bd=0, relief="raised",
                                padx=10, pady=10, width=6)
                # Estilo por tipo
                if char in "0123456789.":
                    btn.configure(bg="#071e12", fg=NEON_GREEN, activebackground="#0b341f")
                elif char in "+-*/%":
                    btn.configure(bg="#08202a", fg=NEON_CYAN, activebackground="#08333b")
                elif char in ['=', 'C', '⌫', '+/-']:
                    btn.configure(bg=ACCENT, fg=TEXT, activebackground="#6f3f9a")
                btn.pack(side="left", padx=6)

        # Bottom small text
        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=12, pady=(0,12))
        hint = tk.Label(bottom, text="Pressione Enter para =   •   Tema: Rick & Morty", bg=BG, fg="#9aa7a3", font=self.small_font)
        hint.pack(side="left")

        # Bind keys
        self.bind("<Return>", lambda e: self.on_button("="))
        self.bind("<BackSpace>", lambda e: self.on_button("⌫"))
        self.bind("<Escape>", lambda e: self.on_button("C"))
        for k in "0123456789.+-*/%":
            self.bind(k, lambda e, ch=k: self.on_button(ch))
        self.bind("<Key>", self.on_keypress)

    def on_keypress(self, event):
        # atualizar frase ocasionalmente
        if random.random() < 0.02:
            self.quote_var.set(random.choice(RICK_QUOTES))

    def on_button(self, ch):
        cur = self.display_var.get()
        if cur == "0" and ch not in ("C", "⌫", "=", "+/-"):
            cur = ""

        if ch == "C":
            self.display_var.set("0")
            return
        if ch == "⌫":
            # backspace
            new = cur[:-1]
            self.display_var.set(new if new else "0")
            return
        if ch == "=":
            try:
                expr = self.display_var.get()
                result = safe_eval(expr)
                # formatar resultado para remover .0 quando inteiro
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                self.display_var.set(str(result))
                # frase de vitória do Rick
                self.quote_var.set(random.choice(["Morty, olha isso!", "Science, bitch!", random.choice(RICK_QUOTES)]))
            except Exception as e:
                self.display_var.set("Erro")
                messagebox.showerror("Erro", f"Expressão inválida:\n{e}")
            return
        if ch == "+/-":
            try:
                val = self.display_var.get()
                if val.startswith("-"):
                    self.display_var.set(val[1:])
                else:
                    if val != "0":
                        self.display_var.set("-" + val)
            except Exception:
                pass
            return

        # para todos os outros (números e operadores)
        new = cur + ch
        # evitar sequências inválidas tipo "++" (deixar o usuário digitar, mas opcionalmente prevenir)
        self.display_var.set(new)

# ---------- Executa ----------
if __name__ == "__main__":
    app = RickCalculator()
    app.mainloop()
