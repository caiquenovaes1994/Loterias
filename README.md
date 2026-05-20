# 🎰 Loterias Automáticas: Conferidor Consolidado Financeiro

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-v4%20%2F%20v5-2671E5?style=flat&logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat&logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![JSON](https://img.shields.io/badge/JSON-5E5E5E?style=flat&logo=json&logoColor=white)](https://www.json.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

Uma solução automatizada e robusta para conferência de jogos das Loterias Caixa, com **avisos em tempo real via Bot do Telegram**, automação via GitHub Actions, relatórios visuais e análise financeira detalhada de prêmios.

---

## 🌟 Diferenciais do Projeto

- **🤖 Bot do Telegram em Tempo Real:** Receba notificações automáticas 24h antes, 1h antes e no momento do sorteio. O bot confere seus jogos automaticamente assim que o resultado é publicado.
- **Automação Inteligente:** Execução programada (Cron) sincronizada com os horários oficiais de sorteio da Caixa.
- **Cálculo Financeiro Real:** Integração com a `listaRateioPremio` da API oficial, exibindo o valor real do prêmio pago pela Caixa para cada faixa de acerto.
- **Gestão de Bolões:** Divisão automática de prêmios entre participantes, calculando o valor exato por cota.
- **Normalização Dinâmica:** Tratamento de nomes de loterias (ex: "Mega-Sena", "Mega da Virada", "+Milionária") garantindo que o usuário não precise se preocupar com a sintaxe exata da API.
- **Suporte Total a Modalidades Especiais:**
  - **+Milionária:** Conferência de dezenas + trevos com faixas de premiação específicas.
  - **Timemania:** Validação automática do "Time do Coração".
- **Relatórios Visuais:** Saída formatada em Markdown no `GITHUB_STEP_SUMMARY`, com destaque para premiações e valores monetários.

---

## 📊 Estrutura do Repositório

```text
Loterias/
├── conferidor.py          # Núcleo lógico: consome API, processa e calcula prêmios
├── telegram_bot.py        # Bot Telegram: alertas em tempo real + conferência automática
├── jogos_pessoais.json    # Suas apostas individuais (com datas dos concursos)
├── jogos_bolao.json       # Apostas em grupo com metadados financeiros
├── requirements.txt       # Dependências Python
├── REGRAS_LOTERIAS.md     # Referência rápida das modalidades e dias de sorteio
├── LICENSE                # Licença MIT
├── CODE_OF_CONDUCT.md     # Código de conduta do projeto
└── .github/workflows/     # Pipeline de automação GitHub Actions
```

---

## 🤖 Bot do Telegram

### Notificações automáticas

O bot monitora as datas definidas em `jogos_pessoais.json` e envia:

| ⏱️ Momento | 📬 Mensagem |
| --- | --- |
| 24h antes | Lembrete do sorteio com data e hora |
| 1h antes | Aviso de que o sorteio está próximo |
| Na hora | Confirmação de início do sorteio |
| +30 min | Conferência completa dos seus jogos com prêmios |

### Configuração do `jogos_pessoais.json`

Adicione o campo `"data_sorteio"` em ISO 8601 (fuso de Brasília) para cada concurso:

```json
{
  "megasena": {
    "concurso": 3010,
    "data_sorteio": "2026-05-24T11:00:00",
    "jogos": ["09-23-42-45-46-48", "..."]
  }
}
```

> Loterias sem `data_sorteio` (ou com `null`) são conferidas apenas pelo GitHub Actions, sem alertas do bot.

### Executar o bot localmente

```bash
pip install -r requirements.txt
python telegram_bot.py
```

O bot fica rodando em background e agenda os alertas automaticamente. Alertas já enviados não são duplicados, mesmo com reinicializações do loop de verificação a cada 10 minutos.

---

## ⚙️ GitHub Actions — Automação via Workflow

O workflow principal (`telegram_bot.yml`) executa `telegram_bot.py --ci` em três horários diários, cobrindo lembretes e conferências de resultado.

### 🕐 Agenda de Disparos

| Horário (BRT) | Horário (UTC) | Ação |
|---|---|---|
| 15h00 | 18:00 | Lembrete "sorteio amanhã" / aviso "sorteio hoje" |
| 18h00 | 21:00 | Aviso "falta 1 hora" para sorteios das 20h |
| 21h30 | 00:30 (d+1) | Busca resultado e confere seus jogos |

> Todos os três horários rodam diariamente (`* * *`). O bot detecta automaticamente se o sorteio é hoje ou amanhã e age de acordo.

### 🔐 Configurar Secrets no GitHub

Antes do workflow funcionar, cadastre as credenciais do Telegram em:
**Repositório → Settings → Secrets and variables → Actions → New repository secret**

| Nome do Secret | Valor |
|---|---|
| `TELEGRAM_TOKEN` | Token do bot (obtido no [@BotFather](https://t.me/BotFather)) |
| `TELEGRAM_CHAT_ID` | ID do seu chat (use [@userinfobot](https://t.me/userinfobot)) |

> ⚠️ **Nunca** comite o token diretamente no código. Sempre use Secrets.

### ▶️ Disparo Manual

Acesse **Actions → 🎰 Bot de Loterias — Telegram → Run workflow** para disparar sob demanda a qualquer momento.

---

_Desenvolvido para automatizar a sorte e organizar a fé._ 🍀

---

## 👤 Autor

### Caique Novaes

[![GitHub](https://img.shields.io/badge/GitHub-caiquenovaes1994-181717?style=flat&logo=github&logoColor=white)](https://github.com/caiquenovaes1994)
&nbsp;
[![Gmail](https://img.shields.io/badge/Gmail-caiquenovaes1994@gmail.com-EA4335?style=flat&logo=gmail&logoColor=white)](mailto:caiquenovaes1994@gmail.com)
&nbsp;
[![Telegram](https://img.shields.io/badge/Telegram-@caiquenovaes94-26A5E4?style=flat&logo=telegram&logoColor=white)](https://t.me/caiquenovaes94)
