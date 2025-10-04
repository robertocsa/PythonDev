Projeto para apresentação de dados estatísticos, de fontes como IBGE, Atlas. 
Permite observação de valores estatísticos como IDH, PIB, Qtde escolas e outros.
Para rodar o código, é preciso baixar os "shapes" (malhas vetoriais) disponibilizados pelo IBGE em https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html
O programa escrito em Python mescla os dados da malha, seus geometry valores (vetores) e os que compilei em uma planilha Excel denominada DadosMunicipios.xlsx

Baixe o arquivo BR_Municipios_2024.zip, descompacte-o em uma subpasta (da pasta onde salvará o aplicativo) denominada MalhasTerritoriais
Mantenha o arquivo DadosMunicipios.xlsx na mesma pasta do aplicativo (MapaCoropleticoTerritorialBrasil.py). Baixe as bibliotecas necessárias (pip instal <nome da biblioteca>). E rode. Criado e experimentado na versão Python 3.12.
Elaborado com auxílio do Grok e ChatGPT (IAs).

Observação importante: embora se tenham tomado os devidos cuidados para uma boa compilação, este estudo não tem pretensões além de servir como material didático. Some-se a isso a dificuldade imensa de se obter dados de fontes confiáveis, além da dinâmica de criação de novas cidades ao longo dos anos base da pesquisa (variando de 2010 a 2025), e da mudança de critérios para a divisão territorial (mudança de mesorregiões e microrregiões para regiões imediatas (RGI) e regiões intermediárias (RGINT)). 

Alguns dados faltantes, por exemplo os do município de Boa Esperança do Norte (MT), criado em 2025, foram preenchidos pela média dos valores dos municípios da mesma região imediata.
De modo similar, os valores das regiões (Mesorregião, Microrregião, RGINT e RGI) foram agrupados pelas respectivas médias (dos valores por município) quando envolvendo índices ou médias (variáveis intensivas); e agrupados pela soma (dos valores por município), quando envolvendo valores de totalização (variáveis extensivas). Ou seja, se uma hipotética região imediata é formada por 3 municípios, o PIB (por exemplo) é formado pela soma dos respectivos PIBs e o IDH, pelas respectivas médias entre eles.
