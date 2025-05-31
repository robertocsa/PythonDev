import mammoth
import pyperclip

# Lê e converte o arquivo .docx para HTML
with open("entrada.docx", "rb") as docx_file:
    result = mammoth.convert_to_html(docx_file)
    html = result.value

# Insere uma quebra de linha após cada parágrafo
html_com_quebras = html.replace("</p>", "</p>\n")

# Exibe no terminal
print(html_com_quebras)

# Salva em um arquivo
with open("saida.txt", "w", encoding="utf-8") as f:
    f.write(html_com_quebras)

# Copia para a área de transferência
pyperclip.copy(html_com_quebras)
print("\nHTML copiado para a área de transferência e salvo em 'saida.txt'.")
