# pyDash - Implementação do Algoritmo ABR: Probe and Adapt

Este repositório contém a implementação do algoritmo **Probe and Adapt** como parte do projeto do **Grupo 15** da disciplina **Redes de Computadores** da **Universidade de Brasília (UnB)**, no semestre **2024.1**. O objetivo principal deste projeto é desenvolver e avaliar um algoritmo de adaptação de taxa de bits (ABR) para streaming de vídeo no padrão MPEG-DASH.

## Descrição do Projeto

### Sobre o Algoritmo Probe and Adapt
O algoritmo **Probe and Adapt** é uma técnica avançada de adaptação de taxa para streaming de vídeo sobre HTTP. Ele funciona sondando periodicamente a largura de banda disponível e ajustando dinamicamente a qualidade do vídeo com base nos resultados obtidos, a fim de maximizar a qualidade de reprodução sem causar interrupções (re-buffering).

### Plataforma pyDash
O projeto é desenvolvido sobre a plataforma **pyDash**, uma ferramenta que simula um ambiente de cliente MPEG-DASH, permitindo a implementação e avaliação de diferentes algoritmos ABR. A estrutura da plataforma pyDash é modular, composta principalmente pelos componentes `Player`, `IR2A`, e `ConnectionHandler`, que gerenciam o fluxo de dados e a adaptação da qualidade do vídeo.

## Estrutura do Projeto

- **r2a/probe_and_adapt.py**: Implementação do algoritmo ABR `Probe and Adapt`.
- **dash_client.json**: Arquivo de configuração que define os parâmetros do ambiente de execução e o algoritmo ABR a ser utilizado.
- **results/**: Diretório onde os resultados das execuções (estatísticas e gráficos) são armazenados.
- **docs/**: Documentação adicional do projeto, incluindo relatórios técnicos e apresentações.

## Configuração e Execução

### Requisitos
- Python 3.x
- Bibliotecas Python: `requests`, `numpy`, `matplotlib`, `lxml`

### Resultados
Os resultados das execuções, incluindo gráficos de desempenho e logs, serão salvos na pasta `results/`. Estes podem ser usados para analisar o comportamento do algoritmo sob diferentes condições de rede.

## Avaliação

O algoritmo **Probe and Adapt** será avaliado com base em diferentes cenários de teste que simulam condições de rede variadas. As principais métricas de desempenho incluem:
- Qualidade média dos segmentos de vídeo baixados.
- Número de interrupções na reprodução (re-buffering).
- Eficiência na adaptação à largura de banda disponível.

## Referências

- [MPEG-DASH Overview](https://en.wikipedia.org/wiki/Dynamic_Adaptive_Streaming_over_HTTP)
- [Probe and Adapt: Rate Adaptation for HTTP Video Streaming At Scale](https://arxiv.org/pdf/1305.0510)

