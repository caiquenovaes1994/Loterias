# 🎰 Loterias Automáticas: Conferidor Consolidado

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![JSON](https://img.shields.io/badge/json-5E5E5E?style=for-the-badge&logo=json&logoColor=white)

Uma solução automatizada e robusta para conferência de jogos das Loterias Caixa, integrando automação via GitHub Actions e relatórios visuais diretamente no seu repositório.

---

## 🌟 Diferenciais do Projeto

- **Automação Inteligente:** Execução programada (Cron) sincronizada com os horários oficiais de sorteio da Caixa.
- **Conferência Consolidada:** Suporte a múltiplas categorias de jogos (Pessoais e Bolões) em arquivos independentes.
- **Normalização Dinâmica:** Tratamento de nomes de loterias (ex: "Mega-Sena", "Mega da Virada", "+Milionária") garantindo que o usuário não precise se preocupar com a sintaxe exata da API.
- **Suporte Total a Modalidades Especiais:**
  - **+Milionária:** Conferência de dezenas + trevos com faixas de premiação específicas.
  - **Timemania:** Validação automática do "Time do Coração".
- **Relatórios Visuais:** Saída formatada em Markdown no `GITHUB_STEP_SUMMARY`, com destaque visual para potenciais premiações (💰).

## 📊 Estrutura do Repositório

O projeto é modular e organizado para facilitar a manutenção e a privacidade das suas apostas:

- **`conferidor.py`**: O núcleo lógico do sistema, responsável pelo consumo da API e processamento dos resultados.
- **`jogos_pessoais.json`**: Armazena suas apostas individuais.
- **`jogos_bolao.json`**: Armazena as apostas em grupo (bolões).
- **`.github/workflows/`**: Configuração da pipeline de automação.
- **`REGRAS_LOTERIAS.md`**: Guia de referência rápida sobre as modalidades e dias de sorteio.

## ⚙️ Funcionamento

O sistema consome os dados da API pública de Loterias da Caixa Econômica Federal. A cada execução, ele cruza as dezenas sorteadas com as apostas cadastradas nos arquivos JSON, aplicando as regras de premiação de cada modalidade e gerando um log detalhado de acertos.

---

_Desenvolvido para automatizar a sorte e organizar a fé._ 🍀

## 👤 Autor

### Caique Novaes

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/caiquenovaes1994)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:caiquenovaes1994@gmail.com)
