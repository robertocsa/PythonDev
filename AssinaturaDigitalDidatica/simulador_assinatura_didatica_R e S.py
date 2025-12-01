# simulador_assinatura_didatica.py

import tkinter as tk
from tkinter import scrolledtext, messagebox
import hashlib
import math
import random

def eh_primo(n: int) -> bool:
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def inverso_modular(a, m):
    try:
        return pow(a, -1, m)
    except ValueError:
        return None

def gerar_k_valido(P):
    """Gera um k aleatório válido que seja coprimo com P-1."""
    m = P - 1
    while True:
        k = random.randint(2, m - 1)
        if math.gcd(k, m) == 1:
            return k

def hash_reduzido(data: bytes) -> int:
    """Calcula o hash SHA-256 e retorna o valor decimal dos últimos 5 chars hex."""
    full_hash_hex = hashlib.sha256(data).hexdigest()
    reduced_hash_hex = full_hash_hex[-5:]
    return int(reduced_hash_hex, 16)

# ==================== JANELA ====================
root = tk.Tk()
root.title("Assinatura Digital – Simulador Didático")
root.geometry("1480x900")
root.configure(bg="#f5f7fa")

# ==================== VARIÁVEIS ====================
P_var = tk.IntVar(value=2147483647)
G_var = tk.IntVar(value=5)
privada_var = tk.IntVar(value=13)
k_var = tk.IntVar(value=gerar_k_valido(2147483647))
assinatura_gerada = {"r": None, "s": None}

# ==================== VALIDAÇÃO ====================
def validar_P():
    try:
        n = int(entry_P.get())
        if n > 17 and eh_primo(n):
            P_var.set(n)
            validar_k()
            recalcular_tudo()
        else:
            messagebox.showwarning("Erro", "P deve ser primo > 17")
            entry_P.delete(0, tk.END)
            entry_P.insert(0, str(P_var.get()))
    except ValueError:
        pass

def validar_G():
    try:
        n = int(entry_G.get())
        if 1 < n < P_var.get():
            G_var.set(n)
            recalcular_tudo()
        else:
            messagebox.showwarning("Erro", "G deve ser < P")
            entry_G.delete(0, tk.END)
            entry_G.insert(0, str(G_var.get()))
    except ValueError:
        pass

def validar_privada():
    try:
        n = int(entry_privada.get())
        if 1 < n < P_var.get():
            privada_var.set(n)
            recalcular_tudo()
        else:
            messagebox.showwarning("Erro", "Chave privada deve estar entre 2 e P-1")
            entry_privada.delete(0, tk.END)
            entry_privada.insert(0, str(privada_var.get()))
    except ValueError:
        pass

def validar_k(*args):
    try:
        n = int(entry_k.get())
        P = P_var.get()
        if not (1 < n < P and math.gcd(n, P - 1) == 1):
            novo_k = gerar_k_valido(P)
            k_var.set(novo_k)
            entry_k.delete(0, tk.END)
            entry_k.insert(0, str(novo_k))
            messagebox.showinfo("Correção Automática", f"k inválido. Novo k gerado automaticamente: {novo_k}")
        
        recalcular_tudo()
    except ValueError:
        pass

# ==================== CÁLCULOS ====================
def recalcular_tudo(*args):
    atualizar_chave_publica()
    gerar_assinatura()

def atualizar_chave_publica():
    try:
        P = P_var.get()
        G = G_var.get()
        priv = privada_var.get()
        if P <= 17 or G >= P or priv >= P or priv < 2:
            pub_label.config(text="Valores inválidos", fg="red")
            return
        chave_publica = pow(G, priv, P)
        pub_label.config(text=f"Chave pública Y = {G}^{priv} mod {P} = {chave_publica}", fg="black")
    except Exception as e:
        pub_label.config(text=f"Erro no cálculo: {e}", fg="red")

def gerar_assinatura(*args):
    global assinatura_gerada
    try:
        P = P_var.get()
        G = G_var.get()
        priv = privada_var.get()
        k = k_var.get()

        texto = texto_original.get("1.0", tk.END).strip()
        if not texto:
            hash_full_label.config(text="Hash SHA256:", fg="black")
            hash_reduced_label.config(text="Hash Reduzido:", fg="black")
            r_label.config(text="R:", fg="black")
            s_label.config(text="S:", fg="black")
            assinatura_label.config(text="Assinatura:", fg="black")
            texto_assinado.delete("1.0", tk.END)
            assinatura_recebida.delete("1.0", tk.END)
            verificar_assinatura()
            return
        
        texto_bytes = texto.encode()
        full_hash_hex = hashlib.sha256(texto_bytes).hexdigest()
        h = hash_reduzido(texto_bytes)

        hash_full_label.config(text=f"Hash SHA256: {full_hash_hex}", fg="black")
        hash_reduced_label.config(text=f"Hash Reduzido (h): {h}", fg="black")

        # 2. Gerar R
        r = pow(G, k, P)
        r_label.config(text=f"R = {G}^{k} mod {P} = {r}", fg="black")

        # 3. Gerar S
        inverso_k = inverso_modular(k, P - 1)
        if inverso_k is None:
            raise ValueError("k não é coprimo com P-1")
        s = (inverso_k * (h - priv * r)) % (P - 1)
        s_label.config(text=f"S = {inverso_k} * ({h} - {priv} * {r}) mod {P-1} = {s}", fg="black")
        
        assinatura_gerada = {"r": r, "s": s}
        assinatura_label.config(text=f"Assinatura=(R={r}, S={s})", fg="black")

        # Copia para o lado de verificação e dispara a verificação
        texto_assinado.delete("1.0", tk.END)
        texto_assinado.insert("1.0", texto)
        assinatura_recebida.delete("1.0", tk.END)
        assinatura_recebida.insert("1.0", f"R={r}, S={s}")
        
        verificar_assinatura()

    except Exception as e:
        assinatura_label.config(text=f"Erro na assinatura: {e}", fg="red")

def verificar_assinatura(*args):
    try:
        P = P_var.get()
        G = G_var.get()
        
        texto_verificar = texto_assinado.get("1.0", tk.END).strip()
        assinatura_str = assinatura_recebida.get("1.0", tk.END).strip()

        if not texto_verificar or not assinatura_str:
            v1_formula_label.config(text="V1 (Fórmula):", fg="black")
            v1_label.config(text="V1 (Valor):", fg="black")
            v2_formula_label.config(text="V2 (Fórmula):", fg="black")
            v2_label.config(text="V2 (Valor):", fg="black")
            hash_full_verif_label.config(text="Hash SHA256:", fg="black")
            hash_reduced_verif_label.config(text="Hash Reduzido:", fg="black")
            resultado_verificacao.config(text="Aguardando dados...", fg="blue")
            return

        try:
            # Extração mais robusta de R e S
            r_val = int(assinatura_str.split('R=')[-1].split(',')[0].strip())
            s_val = int(assinatura_str.split('S=')[-1].strip())
        except (IndexError, ValueError):
            resultado_verificacao.config(text="Erro: Assinatura inválida", fg="red")
            return
        
        texto_bytes = texto_verificar.encode()
        full_hash_hex = hashlib.sha256(texto_bytes).hexdigest()
        h_verif = hash_reduzido(texto_bytes)

        hash_full_verif_label.config(text=f"Hash SHA256: {full_hash_hex}", fg="black")
        hash_reduced_verif_label.config(text=f"Hash Reduzido (h): {h_verif}", fg="black")

        # 2. Calcular a chave pública y
        priv = privada_var.get()
        chave_publica = pow(G, priv, P)
        
        # 3. Calcular V1 (Fórmula e Valor)
        v1_formula_label.config(text=f"V1 (Fórmula): {G}^h mod {P}", fg="black")
        v1 = pow(G, h_verif, P)
        v1_label.config(text=f"V1 (Valor): {v1}", fg="black")

        # 4. Calcular V2 (Fórmula e Valor)
        v2_formula_label.config(text=f"V2 (Fórmula): (Y^R * R^S) mod {P}", fg="black")
        v2 = (pow(chave_publica, r_val, P) * pow(r_val, s_val, P)) % P
        v2_label.config(text=f"V2 (Valor): {v2}", fg="black")

        # 5. Comparar V1 e V2
        if v1 == v2:
            resultado_verificacao.config(text="Verificação: Assinatura VÁLIDA! (V1 == V2)", fg="green")
        else:
            resultado_verificacao.config(text="Verificação: Assinatura INVÁLIDA! (V1 != V2)", fg="red")
            
    except Exception as e:
        resultado_verificacao.config(text=f"Erro na verificação: {e}", fg="red")

# ==================== CONTEÚDO DA INTERFACE ====================
frame_assinatura = tk.Frame(root, bg="#e3e6e8", padx=10, pady=10)
frame_assinatura.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

frame_verificacao = tk.Frame(root, bg="#e3e6e8", padx=10, pady=10)
frame_verificacao.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

FONT_CALC = ("Helvetica", 12)
FONT_BOLD = ("Helvetica", 12, "bold")
FONT_SMALLER = ("Courier", 10)

# Frame de Assinatura
tk.Label(frame_assinatura, text="Gerar Assinatura Digital", font=("Helvetica", 16, "bold"), bg="#e3e6e8").pack(pady=5)

# Parâmetros
frame_parametros = tk.LabelFrame(frame_assinatura, text="Parâmetros (ElGamal)", bg="#f5f7fa", padx=10, pady=5, font=FONT_BOLD)
frame_parametros.pack(fill=tk.X, pady=5)

tk.Label(frame_parametros, text="P (Primo grande > 17):", bg="#f5f7fa").pack(side=tk.LEFT, padx=5)
entry_P = tk.Entry(frame_parametros, textvariable=P_var, width=15)
entry_P.pack(side=tk.LEFT, padx=5)
entry_P.bind("<Return>", lambda e: validar_P())

tk.Label(frame_parametros, text="G (Gerador < P):", bg="#f5f7fa").pack(side=tk.LEFT, padx=5)
entry_G = tk.Entry(frame_parametros, textvariable=G_var, width=5)
entry_G.pack(side=tk.LEFT, padx=5)
entry_G.bind("<Return>", lambda e: validar_G())

tk.Label(frame_parametros, text="Chave Privada (x):", bg="#f5f7fa").pack(side=tk.LEFT, padx=5)
entry_privada = tk.Entry(frame_parametros, textvariable=privada_var, width=5)
entry_privada.pack(side=tk.LEFT, padx=5)
entry_privada.bind("<Return>", lambda e: validar_privada())

tk.Label(frame_parametros, text="k (Secreto, Coprimo com P-1):", bg="#f5f7fa").pack(side=tk.LEFT, padx=5)
entry_k = tk.Entry(frame_parametros, textvariable=k_var, width=5)
entry_k.pack(side=tk.LEFT, padx=5)
entry_k.bind("<Return>", lambda e: validar_k())
entry_k.bind("<KeyRelease>", validar_k)

# Chave pública
pub_label = tk.Label(frame_assinatura, text="Chave pública:", justify=tk.LEFT, anchor="w", bg="#e3e6e8", font=FONT_CALC)
pub_label.pack(fill=tk.X, pady=5)

# Explicação de R, S, K
tk.Label(frame_assinatura, text="Nota: k é um valor aleatório secreto usado apenas uma vez.", font=FONT_SMALLER, bg="#e3e6e8", anchor="w").pack(fill=tk.X)
tk.Label(frame_assinatura, text="R e S são as duas partes que compõem a assinatura digital.", font=FONT_SMALLER, bg="#e3e6e8", anchor="w").pack(fill=tk.X)


# Texto original
tk.Label(frame_assinatura, text="Texto a ser Assinado:", bg="#e3e6e8", font=FONT_BOLD).pack(pady=5)
texto_original = scrolledtext.ScrolledText(frame_assinatura, width=70, height=10, wrap=tk.WORD)
texto_original.pack(pady=5)
texto_original.insert("1.0", "RCSantos Scripts")
texto_original.bind("<KeyRelease>", gerar_assinatura)

# Geração da assinatura
tk.Label(frame_assinatura, text="--- Processo de Assinatura ---", font=("Helvetica", 14, "italic"), bg="#e3e6e8").pack(pady=10)

hash_full_label = tk.Label(frame_assinatura, text="Hash SHA256:", justify=tk.LEFT, anchor="w", bg="#e3e6e8", font=FONT_SMALLER)
hash_full_label.pack(fill=tk.X, pady=2)
hash_reduced_label = tk.Label(frame_assinatura, text="Hash Reduzido (h):", justify=tk.LEFT, anchor="w", bg="#e3e6e8", font=FONT_CALC)
hash_reduced_label.pack(fill=tk.X, pady=2)

r_label = tk.Label(frame_assinatura, text="R (parte 1 da assinatura):", justify=tk.LEFT, anchor="w", bg="#e3e6e8", font=FONT_CALC)
r_label.pack(fill=tk.X, pady=2)
s_label = tk.Label(frame_assinatura, text="S (parte 2 da assinatura):", justify=tk.LEFT, anchor="w", bg="#e3e6e8", font=FONT_CALC)
s_label.pack(fill=tk.X, pady=2)
assinatura_label = tk.Label(frame_assinatura, text="Assinatura:", justify=tk.LEFT, anchor="w", bg="#e3e6e8", font=FONT_BOLD)
assinatura_label.pack(fill=tk.X, pady=10)

# Frame de Verificação
frame_verificacao_inner = tk.Frame(frame_verificacao, bg="#e3e6e8")
frame_verificacao_inner.pack(fill=tk.BOTH, expand=True)

tk.Label(frame_verificacao_inner, text="Verificar Assinatura Digital", font=("Helvetica", 16, "bold"), bg="#e3e6e8").pack(pady=5)

tk.Label(frame_verificacao_inner, text="Texto Recebido:", bg="#e3e6e8", font=FONT_BOLD).pack(pady=5)
texto_assinado = scrolledtext.ScrolledText(frame_verificacao_inner, width=70, height=10, wrap=tk.WORD)
texto_assinado.pack(pady=5)
texto_assinado.insert("1.0", "RCSantos Scripts")
texto_assinado.bind("<KeyRelease>", verificar_assinatura)

tk.Label(frame_verificacao_inner, text="Assinatura Recebida (R, S):", bg="#e3e6e8", font=FONT_BOLD).pack(pady=5)
assinatura_recebida = scrolledtext.ScrolledText(frame_verificacao_inner, width=70, height=5, wrap=tk.WORD)
assinatura_recebida.pack(pady=5)
assinatura_recebida.bind("<KeyRelease>", verificar_assinatura)

# Botão de verificação manual (mantido, mas os eventos automáticos já funcionam)
btn_verificar = tk.Button(frame_verificacao_inner, text="Verificar Assinatura", command=verificar_assinatura)
btn_verificar.pack(pady=10)

# Verificação
tk.Label(frame_verificacao_inner, text="--- Processo de Verificação ---", font=("Helvetica", 14, "italic"), bg="#e3e6e8").pack(pady=10)

hash_full_verif_label = tk.Label(frame_verificacao_inner, text="Hash SHA256:", justify=tk.LEFT, anchor="w", bg="#e3e6e8", font=FONT_SMALLER)
hash_full_verif_label.pack(fill=tk.X, pady=2)
hash_reduced_verif_label = tk.Label(frame_verificacao_inner, text="Hash Reduzido (h):", justify=tk.LEFT, anchor="w", bg="#e3e6e8", font=FONT_CALC)
hash_reduced_verif_label.pack(fill=tk.X, pady=2)

# V1 e V2 com fórmulas e valores
v1_formula_label = tk.Label(frame_verificacao_inner, text="V1 (Fórmula):", justify=tk.LEFT, anchor="w", bg="#e3e6e8", font=FONT_CALC, relief=tk.GROOVE)
v1_formula_label.pack(fill=tk.X, pady=2)
v1_label = tk.Label(frame_verificacao_inner, text="V1 (Valor):", justify=tk.LEFT, anchor="w", bg="#e3e6e8", font=FONT_CALC)
v1_label.pack(fill=tk.X, pady=2)

v2_formula_label = tk.Label(frame_verificacao_inner, text="V2 (Fórmula):", justify=tk.LEFT, anchor="w", bg="#e3e6e8", font=FONT_CALC, relief=tk.GROOVE)
v2_formula_label.pack(fill=tk.X, pady=2)
v2_label = tk.Label(frame_verificacao_inner, text="V2 (Valor):", justify=tk.LEFT, anchor="w", bg="#e3e6e8", font=FONT_CALC)
v2_label.pack(fill=tk.X, pady=2)

resultado_verificacao = tk.Label(frame_verificacao_inner, text="Resultado da Verificação:", justify=tk.LEFT, anchor="w", bg="#e3e6e8", font=FONT_BOLD)
resultado_verificacao.pack(fill=tk.X, pady=10)

# Callbacks iniciais
recalcular_tudo()

root.mainloop()
