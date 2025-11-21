# manim -pqh -r 1080,1086 TrianguloDePascal_3b1b.py TrianguloDePascal
# https://docs.manim.community/en/stable/tutorials/quickstart.html

from manim import *
import numpy as np
import math

def combinacao(n, k):
    return math.comb(n, k)

def expand_binomio_latex(n):
    termos = []
    for k in range(n + 1):
        c = math.comb(n, k)
        if k == 0:
            termos.append(f"a^{n}")
        elif k == n:
            termos.append(f"b^{n}")
        else:
            termos.append(f"{c} a^{n-k} b^{k}")
    return " + ".join(termos)

class TrianguloPascal(Scene):
    def construct(self):
        ciano = "#8af8ff"
        deep_blue = "#040f2f"
        neon = "#00f5ff"
        azul_escuro = "#030630"
        laranja="#ffd82f"
        corForeground = "#f0f0e1"

        self.camera.background_color = azul_escuro
        self.camera.frame_width = 14
        self.camera.frame_height = 14
        self.camera.aspect_ratio = 1.0
     
        titulo = Title("Triângulo de Pascal", color=laranja)
        titulo = titulo.to_edge(UP, buff=-2.4)
        self.play(Write(titulo), run_time=0.3)

        info_nk = MathTex("", color=WHITE).scale(0.65)
        info_comb = MathTex("", color=WHITE).scale(0.65)
        self.add(info_nk, info_comb)

        max_linhas = 9
        raio = 0.32
        dx = 0.78
        dy = 0.69
        triangulo = []

        def seta(origem, destino, lado="esq"):
            start = origem.get_edge_center(DOWN)
            if lado == "esq":
                end = destino.get_edge_center(LEFT)
                sentido = 1
            else:
                end = destino.get_edge_center(RIGHT)
                sentido = -1
            return CurvedArrow(
                start, end,
                angle=0.7 * sentido,
                color=neon,
                stroke_width=5,
                tip_length=0.18
            )

        for n in range(max_linhas + 1):
            linha_figuras = []
            triangulo.append(linha_figuras)
           
            info_bottom = MathTex("", color=WHITE).scale(0.75)
            #info_bottom.to_edge(DOWN, buff=0.25)
            self.add(info_bottom)
           
            painel = VGroup(
                MathTex(
                    rf"\sum_{{k=0}}^{{{n}}}\binom{{{n}}}{{k}} = 2^{{{n}}} = {2**n}",
                    color=WHITE,
                    font_size=36
                ),
                MathTex(
                    rf"(a+b)^{{{n}}} = " + expand_binomio_latex(n),
                    color=WHITE,
                    font_size=34
                )
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(titulo, DOWN, aligned_edge=LEFT, buff=0.15)
            
            self.play(FadeIn(painel), run_time=0.2)

            for k in range(n + 1):
                offset_y = 3.5
                pos = np.array([dx * (k - n / 2), -dy * n + offset_y, 0])

                if k == 0 or k == n:
                    val = 1
                    texto_info = fr"n={n},\ k={k},\ C(n,k)=C({n},{k})={val}"
                    soma_text = ""
                else:
                    left = triangulo[n-1][k-1].val
                    right = triangulo[n-1][k].val
                    val = left + right
                    texto_info = fr"n={n},\ k={k},\ C(n,k)=C({n},{k})={val}\ \text{{ ou }}\ {left}+{right}={val}"
                    soma_text = f"{left} + {right} = {val}"

                # Texto da soma temporário (aparece só quando não é 1)
                soma_circulo = MathTex(soma_text, color=laranja, font_size=36)
                soma_circulo.next_to(pos, DOWN, buff=0.75)

                # Atualiza rodapé               
                info_bottom = MathTex(texto_info, color=WHITE).scale(0.75)
                info_bottom.next_to(pos, DOWN, buff=1.6)
                info_bottom.set_x(0)   # <─ essa linha garante o centralizado horizontal perfeito

                # === ANIMAÇÕES SINCRONIZADAS ===
                circ = Circle(radius=raio, color=WHITE).move_to(pos)
                txt = Text(str(val), color=WHITE, font_size=22).move_to(pos)
                circ.val = val
                circ.txt = txt
                linha_figuras.append(circ)

                arrows = VGroup()

                if n > 0 and 0 < k < n:
                    cima_esq = triangulo[n-1][k-1]
                    cima_dir = triangulo[n-1][k]
                    s1 = seta(cima_esq, circ, lado="esq")
                    s2 = seta(cima_dir, circ, lado="dir")
                    arrows.add(s1, s2)

                    # Mostra a soma temporária e o texto do rodapé
                    self.play(
                        FadeIn(soma_circulo, shift=DOWN*0.3),
                        FadeIn(info_bottom),
                        run_time=1.8
                    )

                    # Cria setas 
                    self.play(Create(arrows, run_time=0.8))
                    
                    # Cria o circulo e o numero
                    self.play(FadeIn(circ, run_time=0.8))
                    self.play(FadeIn(txt, run_time=1.2))
                    
                    # Remove setas e soma temporária
                    self.play(
                        FadeOut(arrows, run_time=1.0),
                        FadeOut(soma_circulo, run_time=1.0)
                    )
                else:
                    # Casos das extremidades (só 1)
                    self.play(
                        FadeIn(info_bottom),
                        FadeIn(circ),
                        FadeIn(txt),
                        run_time=1.2
                    )
                
                self.play(FadeOut(info_bottom, run_time=1.2))

                # Pequeno tempo de leitura entre um círculo e outro
                self.wait(1.8)

            # Limpa painel
            self.play(FadeOut(painel, run_time=1.0))
                        
            