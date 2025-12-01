import tkinter as tk
from tkinter import scrolledtext, messagebox
import hashlib

# ===========================================================
# PRIMALIDADE – rápido o suficiente para < 10¹²
# ===========================================================
def eh_primo(n: int) -> bool:
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True


# ===========================================================
# INVERSO MODULAR – Euclides Estendido (instantâneo)
# ===========================================================
def inverso(a, m):
    if m == 1:
        return 0

    m0 = m
    x0, x1 = 0, 1

    if m == 0:
        return None

    while a > 1:
        q = a // m
        a, m = m, a % m
        x0, x1 = x1 - q * x0, x0

    if a != 1:
        return None

    return x1 % m0


# ===========================================================
# GUI
# ===========================================================
root = tk.Tk()
root.title("Assinatura Digital – Simulador Didático (Valor Único)")
root.geometry("1480x950")
root.configure(bg="#f5f7fa")

# -------------------------
# VARS
# -------------------------
#P_var = tk.IntVar(value=101)
P_var = tk.IntVar(value=1000000007)
G_var = tk.IntVar(value=113)
privada_var = tk.IntVar(value=17)  # d

# -------------------------
# Validação
# -------------------------
def validar_primo(entry, var):
    try:
        n = int(entry.get())
        if eh_primo(n) and n > 2:
            var.set(n)
            recalcular_tudo()
        else:
            messagebox.showwarning("Erro", "Valor deve ser primo > 2")
            entry.delete(0, tk.END)
            entry.insert(0, str(var.get()))
    except:
        pass


def validar_P(): validar_primo(entry_P, P_var)
def validar_G(): validar_primo(entry_G, G_var)


# =======================================================
# OBTÉM CHAVES
# =======================================================
def obter_chaves():
    P = P_var.get()
    G = G_var.get()
    d = privada_var.get()

    n = P * G
    phi = (P - 1) * (G - 1)

    e = inverso(d, phi)
    if e is None:
        return None, None, None, None

    return n, phi, d, e


# =======================================================
# ATUALIZAÇÃO GERAL
# =======================================================
def recalcular_tudo(*args):
    atualizar_chaves()
    gerar_assinatura()
    verificar_assinatura()


# =======================================================
# ATUALIZAÇÃO DO TOPO
# =======================================================
def atualizar_chaves():
    try:
        n, phi, d, e = obter_chaves()

        if n is None:
            pub_label.config(text="Chave pública inválida (d não possui inverso mod φ(n))", fg="red")
            return

        pub_label.config(
            text=f"chave pública (e)={e}",
            fg="#000000",
            font=("Courier", 13, "bold")
        )

        texto_chaves = (
            f"n = P × G = {P_var.get()} × {G_var.get()} = {n}\n"
            f"φ(n) = (P−1)(G−1) = ({P_var.get()}−1)({G_var.get()}−1) = {phi}\n\n"
            f"Cálculo da chave pública e:\n"
            f"• Fórmula algébrica:   e · d ≡ 1  (mod φ(n))\n"
            f"• Aplicação numérica:   e · {d} ≡ 1  (mod {phi})\n"
            f"• Resultado: e = {e}\n\n"
            "Observações importantes:\n"
            "• n é usado como módulo nas operações de assinar e verificar.\n"
            "• φ(n) é usado SOMENTE para calcular e (o inverso modular de d)."
        )

        chaves_esq_label.config(text=texto_chaves)

    except Exception as ex:
        pub_label.config(text=f"Erro ao gerar chaves: {ex}", fg="red")


# =======================================================
# ASSINATURA
# =======================================================
assinatura_global = None
hash_bruto_global = None
hash_reduzido_global = None


def gerar_assinatura(*args):
    global assinatura_global, hash_bruto_global, hash_reduzido_global

    texto = entrada_msg.get("1.0", "end").strip()
    if not texto:
        label_sha_esq.config(text="")
        label_red_esq.config(text="")
        label_conta_esq.config(text="")
        label_sig_correta.config(text="")
        entry_sig.delete(0, tk.END)
        return

    # HASH
    sha256_hex = hashlib.sha256(texto.encode()).hexdigest()
    ult5 = sha256_hex[-5:].upper()
    h_bruto = int(ult5, 16)

    n, phi, d, e = obter_chaves()
    if n is None:
        label_sig_correta.config(text="Não é possível gerar assinatura", fg="red")
        return

    h_mod = h_bruto % n

    assinatura = pow(h_mod, d, n)
    assinatura_global = assinatura

    entry_sig.delete(0, tk.END)
    entry_sig.insert(0, str(assinatura))

    label_sha_esq.config(text=f"SHA-256:\n{sha256_hex}", font=("Helvetica", 12, "bold"))
    label_red_esq.config(
        text=f"Últimos 5 chars → {ult5} = {h_bruto}\nh reduzido mod n = {h_mod}",
        fg="#7d3c98", font=("Helvetica", 12, "bold")
    )
    label_conta_esq.config(
        text=f"Assinatura = (h mod n)^d mod n\n{h_mod}^{d} mod {n} = {assinatura}",
        font=("Courier", 12)
    )
    label_sig_correta.config(
        text=f"Assinatura gerada: {assinatura}",
        fg="#2980b9", font=("Courier", 20, "bold")
    )


# =======================================================
# VERIFICAÇÃO
# =======================================================
def verificar_assinatura(*args):
    texto = entrada_ver.get("1.0", "end").strip()
    if not texto:
        label_sha_dir.config(text="")
        label_red_dir.config(text="")
        label_calc_dir.config(text="")
        label_result.config(text="Aguardando...", fg="gray")
        return

    sha256_hex = hashlib.sha256(texto.encode()).hexdigest()
    ult5 = sha256_hex[-5:].upper()
    h_bruto_ver = int(ult5, 16)

    n, phi, d, e = obter_chaves()
    if n is None:
        label_result.config(text="Chave inválida", fg="red")
        return

    h_mod_ver = h_bruto_ver % n

    label_sha_dir.config(text=f"SHA-256:\n{sha256_hex}", font=("Helvetica", 12, "bold"))
    label_red_dir.config(
        text=f"Últimos 5 chars → {ult5} = {h_bruto_ver}\nh reduzido mod n = {h_mod_ver}",
        fg="#7d3c98", 
        font=("Helvetica", 12, "bold")
    )

    try:
        sig = int(entry_sig.get())
    except:
        label_result.config(text="Assinatura não numérica", fg="red")
        return

    h_rec = pow(sig, e, n)

    label_calc_dir.config(
        text=f"Verificação:\n"
             f"sig^e mod n = {sig}^{e} mod {n} = {h_rec}\n"
             f"h mod n     = {h_mod_ver}",
        font=("Helvetica", 12)
    )

    if h_rec == h_mod_ver:
        label_result.config(text="VALIDA – mensagem autêntica!", fg="#27ae60", font=("Courier", 20, "bold"))
    else:
        label_result.config(text="INVÁLIDA – assinatura incorreta!", fg="red", font=("Courier", 20, "bold"))


# =======================================================
# INTERFACE
# =======================================================
tk.Label(root,
         text="Simulador Didático de Assinatura Digital – Valor Único",
         font=("Helvetica", 22, "bold"), bg="#2c3e50", fg="white", pady=16).pack(fill="x")

cfg = tk.LabelFrame(root, text="Configurações", font=("Helvetica", 12, "bold"), bg="#ecf0f1")
cfg.pack(pady=10, padx=20, fill="x")

# Linha superior
tk.Label(cfg, text="Primo P:", bg="#ecf0f1").grid(row=0, column=0, padx=20, pady=8)
entry_P = tk.Entry(cfg, textvariable=P_var, width=12, font=("Courier",14), justify="center")
entry_P.grid(row=0, column=1, padx=10)
entry_P.bind("<FocusOut>", lambda e: validar_P())

tk.Label(cfg, text="Primo G:", bg="#ecf0f1").grid(row=0, column=2, padx=20)
entry_G = tk.Entry(cfg, textvariable=G_var, width=12, font=("Courier",14), justify="center")
entry_G.grid(row=0, column=3, padx=10)
entry_G.bind("<FocusOut>", lambda e: validar_G())

tk.Label(cfg, text="Chave privada (d):", bg="#ecf0f1").grid(row=0, column=4, padx=20)
tk.Entry(cfg, textvariable=privada_var, width=10, font=("Courier",14), justify="center", fg="red").grid(row=0, column=5, padx=10)

# -> e volta para o topo JUNTO com P, G e d
pub_label = tk.Label(cfg, text="", bg="#ecf0f1", font=("Courier", 14, "bold"))
pub_label.grid(row=0, column=6, columnspan=4, padx=30)

# Painéis
main = tk.Frame(root, bg="#f5f7fa")
main.pack(pady=15, padx=20, fill="both", expand=True)

# ----------------- ESQUERDA -----------------
esq = tk.LabelFrame(main, text="1 → Mensagem original", font=("Helvetica", 13, "bold"))
esq.pack(side="left", fill="both", expand=True, padx=(0,12))

entrada_msg = scrolledtext.ScrolledText(esq, height=5, font=("Arial", 11))
entrada_msg.pack(pady=10, padx=15, fill="both", expand=True)
entrada_msg.insert("1.0", "RCSantos Scripts")

# BLOCO DAS CHAVES (n, phi, fórmula do e)
chaves_esq_label = tk.Label(esq, text="", font=("Courier", 12), justify="left", bg="#eef3ff")
chaves_esq_label.pack(pady=10, padx=15, fill="x")

label_sha_esq = tk.Label(esq, text="", bg="white", relief="sunken", height=3, anchor="w")
label_sha_esq.pack(pady=8, padx=15, fill="x")

label_aviso = tk.Label(esq,
    text="Usamos apenas os últimos 5 caracteres do hash (20 bits) para simplificação didática",
    bg="#fffacd", fg="#030303", font=("Helvetica", 12, "bold"), pady=10    
)
label_aviso.pack(fill="x", padx=20, pady=8)

label_red_esq = tk.Label(esq, text="", justify="left", bg="#f8f9fa")
label_red_esq.pack(pady=8, anchor="w", padx=20)

label_conta_esq = tk.Label(esq, text="", font=("Courier", 13))
label_conta_esq.pack(pady=5)

label_sig_correta = tk.Label(esq, text="", font=("Courier", 20, "bold"), fg="#2980b9")
label_sig_correta.pack(pady=15)

tk.Button(esq, text="ATUALIZAR", font=("Helvetica", 13, "bold"), bg="#3498db", fg="white",
          command=recalcular_tudo).pack(pady=10)

# ----------------- DIREITA -----------------
dir = tk.LabelFrame(main, text="2 → Mensagem a verificar", font=("Helvetica", 13, "bold"))
dir.pack(side="right", fill="both", expand=True, padx=(12,0))

entrada_ver = scrolledtext.ScrolledText(dir, height=5, font=("Arial", 11))
entrada_ver.pack(pady=10, padx=15, fill="both", expand=True)
entrada_ver.insert("1.0", "RCSantos Scripts")

label_sha_dir = tk.Label(dir, text="", bg="white", relief="sunken", height=3, anchor="w")
label_sha_dir.pack(pady=8, padx=15, fill="x")

label_red_dir = tk.Label(dir, text="", justify="left", bg="#f8f9fa", font=("Helvetica", 12, "bold"), pady=10)
label_red_dir.pack(pady=8, anchor="w", padx=20)

tk.Label(dir, text="Assinatura recebida:", font=14).pack(pady=(15,5))
entry_sig = tk.Entry(dir, font=("Courier", 20), width=28, justify="center")
entry_sig.pack(pady=8)

label_calc_dir = tk.Label(dir, text="", font=("Courier", 13), bg="#f8f9fa", justify="left", anchor="w")
label_calc_dir.pack(pady=10, padx=20, fill="x")

label_result = tk.Label(dir, text="Aguardando...", font=("Helvetica", 20, "bold"))
label_result.pack(pady=30)

tk.Button(dir, text="VERIFICAR", font=("Helvetica", 13, "bold"), bg="#e74c00", fg="white",
          command=verificar_assinatura).pack(pady=10)

# Triggers
entrada_msg.bind("<KeyRelease>", gerar_assinatura)
entrada_ver.bind("<KeyRelease>", verificar_assinatura)
entry_sig.bind("<KeyRelease>", verificar_assinatura)
P_var.trace("w", lambda *_: recalcular_tudo())
G_var.trace("w", lambda *_: recalcular_tudo())
privada_var.trace("w", lambda *_: recalcular_tudo())

recalcular_tudo()
root.mainloop()
