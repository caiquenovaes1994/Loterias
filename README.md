# 🎰 Loterias Automáticas: Conferidor Consolidado Financeiro

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![JSON](https://img.shields.io/badge/json-5E5E5E?style=for-the-badge&logo=json&logoColor=white)

Uma solução automatizada e robusta para conferência de jogos das Loterias Caixa, integrando automação via GitHub Actions, relatórios visuais e análise financeira detalhada de prêmios.

---

## 🌟 Diferenciais do Projeto

- **Automação Inteligente:** Execução programada (Cron) sincronizada com os horários oficiais de sorteio da Caixa.
- **Cálculo Financeiro Real:** Integração com a `listaRateioPremio` da API oficial, exibindo o valor real do prêmio pago pela Caixa para cada faixa de acerto.
- **Gestão de Bolões:** Divisão automática de prêmios entre participantes, calculando o valor exato por cota.
- **Normalização Dinâmica:** Tratamento de nomes de loterias (ex: "Mega-Sena", "Mega da Virada", "+Milionária") garantindo que o usuário não precise se preocupar com a sintaxe exata da API.
- **Suporte Total a Modalidades Especiais:**
  - **+Milionária:** Conferência de dezenas + trevos com faixas de premiação específicas.
  - **Timemania:** Validação automática do "Time do Coração".
- **Relatórios Visuais:** Saída formatada em Markdown no `GITHUB_STEP_SUMMARY`, com destaque para premiações e valores monetários.

## 📊 Estrutura do Repositório

O projeto é modular e organizado para facilitar a manutenção e a privacidade das suas apostas:

- **`conferidor.py`**: O núcleo lógico do sistema, responsável pelo consumo da API, processamento dos resultados e cálculos financeiros.
- **`jogos_pessoais.json`**: Armazena suas apostas individuais.
- **`jogos_bolao.json`**: Armazena as apostas em grupo, incluindo metadados de participantes e valores de cota.
- **`.github/workflows/`**: Configuração da pipeline de automação.
- **`REGRAS_LOTERIAS.md`**: Guia de referência rápida sobre as modalidades e dias de sorteio.

## ⚙️ Funcionamento

O sistema consome os dados da API pública de Loterias da Caixa Econômica Federal. A cada execução, ele cruza as dezenas sorteadas com as apostas cadastradas, aplica as regras de premiação, busca o valor de rateio oficial e gera um relatório financeiro completo formatado em BRL.

---

_Desenvolvido para automatizar a sorte e organizar a fé._ 🍀

## 👤 Autor

### Caique Novaes

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/caiquenovaes1994)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:caiquenovaes1994@gmail.com)
