# 🎰 Loterias Automáticas: Conferidor Consolidado Financeiro

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-v4%20%2F%20v5-2671E5?style=flat&logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat&logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![WhatsApp Bot](https://img.shields.io/badge/WhatsApp-Bot-25D366?style=flat&logo=whatsapp&logoColor=white)](https://www.callmebot.com/blog/free-api-whatsapp-messages/)
[![JSON](https://img.shields.io/badge/JSON-5E5E5E?style=flat&logo=json&logoColor=white)](https://www.json.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

Uma solução automatizada e robusta para conferência de jogos das Loterias Caixa, com **avisos em tempo real via Bot do Telegram e WhatsApp**, automação via GitHub Actions, relatórios visuais e análise financeira detalhada de prêmios.

---

## 🌟 Diferenciais do Projeto

- **🤖 Bots em Tempo Real:** Receba notificações automáticas no **Telegram** e **WhatsApp** (exclusivo para grupos de bolão) 7 dias, 3 dias, 24h e 1h antes do sorteio. Os bots conferem seus jogos automaticamente assim que o resultado é publicado.
- **Automação Inteligente:** Execução programada (Cron) com 5 horários diários sincronizados aos sorteios oficiais da Caixa.
- **Cálculo Financeiro Real:** Integração com a `listaRateioPremio` da API oficial, exibindo o valor real do prêmio pago pela Caixa para cada faixa de acerto.
- **Gestão de Bolões:** Divisão automática de prêmios entre participantes, calculando o valor exato por cota.
- **Normalização Dinâmica:** Tratamento de nomes de loterias (ex: "Mega-Sena", "Mega da Virada", "+Milionária") garantindo que o usuário não precise se preocupar com a sintaxe exata da API.
- **Suporte Total a Modalidades Especiais:**
  - **+Milionária:** Conferência de dezenas + trevos com faixas de premiação específicas.
  - **Timemania:** Validação automática do "Time do Coração".
- **Digest Inteligente:** Em dias sem sorteio, o bot silencia alertas isolados e envia **apenas uma única mensagem diária** com o resumo dos próximos jogos (até 7 dias). Se não houver nenhum jogo no período, ele permanece em silêncio.

---

## 📊 Estrutura do Repositório

```text
Loterias/
├── conferidor.py          # Núcleo lógico: consome API, processa e calcula prêmios
├── telegram_bot.py        # Bot Telegram: alertas em tempo real + conferência automática
├── jogos_pessoais.json    # Suas apostas individuais (com datas dos concursos)
├── jogos_bolao.json       # Apostas em grupo com metadados financeiros
├── requirements.txt       # Dependências Python
├── pyrightconfig.json     # Configuração Pyright (suprime erros de ambiente virtual)
├── REGRAS_LOTERIAS.md     # Referência rápida das modalidades e dias de sorteio
├── LICENSE                # Licença MIT
├── CODE_OF_CONDUCT.md     # Código de conduta do projeto
└── .github/workflows/     # Pipeline de automação GitHub Actions
```

---

## 🤖 Bots de Notificação (Telegram e WhatsApp)

### Janelas de notificação

O bot monitora as datas definidas em `jogos_pessoais.json` e adapta o envio de mensagens:

**Nos dias em que há sorteios (ou resultados pendentes):**
O bot dispara os alertas programados em seus horários específicos:

| ⏱️ Quando | 📬 Mensagem |
| --- | --- |
| 7 dias antes | "Faltam 7 dias!" — anote na agenda |
| 3 dias antes | "Faltam 3 dias!" — prepare-se |
| 1 dia antes | "Sorteio Amanhã!" — lembrete com data e hora |
| ≤ 2h antes | "Falta X minuto(s)!" — aviso final |
| Pós-sorteio | Conferência completa com resultado e prêmios (disparado uma única vez) |

> ℹ️ **Sobre o envio de Resultados (Pós-sorteio):** Para evitar mensagens repetitivas em dias subsequentes, a busca e envio do resultado do sorteio ocorre apenas na primeira janela do cron configurado (**até 3 horas** após o horário oficial do sorteio). Sorteios cujas datas já passaram dessa janela não causam disparos repetitivos e são ignorados até que você atualize os concursos para o futuro.

**Nos dias sem sorteios (ou sem pendências):**

- O bot não emite os alertas isolados para evitar repetições desnecessárias. Em vez disso, envia **apenas 1 mensagem no dia (às 15h BRT)**, contendo um resumo (Digest) de todos os próximos sorteios mapeados em até 7 dias.
- Caso não haja nenhum sorteio programado para os próximos 7 dias, o bot fica silencioso e não envia nenhuma notificação.

### 🟢 Integração com WhatsApp (CallMeBot)

O sistema suporta envios simultâneos para o Telegram e WhatsApp. Caso as variáveis de ambiente do WhatsApp sejam configuradas, o bot enviará a conferência do sorteio para o seu número privado no WhatsApp **exclusivamente com os resultados dos Jogos de Bolão** (`jogos_bolao.json`).

> **💡 Dica para Grupos:** Como o WhatsApp possui limitações rígidas para bots automáticos em grupos, a solução ideal é você receber essa mensagem com o resultado do bolão no seu privado e apenas **encaminhá-la com 1 toque** para o seu grupo de apostas!

### Configuração do `jogos_pessoais.json` e `jogos_bolao.json`

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

> Loterias sem `data_sorteio` (ou com `null`) são ignoradas pelo bot de alertas.

### Executar o bot localmente

```bash
pip install -r requirements.txt

# Modo daemon (contínuo, com agendamento por threads)
python telegram_bot.py

# Modo CI (execução única — igual ao GitHub Actions)
python telegram_bot.py --ci
```

O bot em modo daemon fica rodando em background e agenda os alertas automaticamente. Alertas já enviados não são duplicados, mesmo com reinicializações do loop de verificação a cada 10 minutos.

---

## ⚙️ GitHub Actions — Automação via Workflow

O workflow principal (`telegram_bot.yml`) executa `telegram_bot.py --ci` em **5 horários diários**, cobrindo sorteios noturnos (≈20h BRT) e diurnos (≈11h BRT).

### 🕐 Agenda de Disparos

| Horário (BRT) | Horário (UTC) | Finalidade |
| --- | --- | --- |
| 09h00 | 12:00 | Aviso "falta 1h" para sorteios das 11h |
| 12h30 | 15:30 | Busca resultado de sorteios das 11h |
| 15h00 | 18:00 | Alertas 7d / 3d / amanhã + digest semanal |
| 18h00 | 21:00 | Aviso "falta 1h" para sorteios das 20h |
| 21h30 | 00:30 (d+1) | Busca resultado de sorteios das 20h |

> Todos os disparos rodam diariamente (`* * *`). O bot detecta automaticamente se o sorteio é hoje, amanhã ou nos próximos dias e age de acordo.

### 🔐 Configurar Secrets no GitHub

Antes do workflow funcionar, cadastre as credenciais do Telegram em:
**Repositório → Settings → Secrets and variables → Actions → New repository secret**

| Nome do Secret | Valor |
| --- | --- |
| `TELEGRAM_TOKEN` | Token do bot (obtido no [@BotFather](https://t.me/BotFather)) |
| `TELEGRAM_CHAT_ID` | ID do seu chat (use [@userinfobot](https://t.me/userinfobot)) |
| `WHATSAPP_PHONE` | (Opcional) Seu telefone com DDI para envio de Bolão |
| `WHATSAPP_API_KEY` | (Opcional) Chave API do [CallMeBot](https://www.callmebot.com/) |

> ⚠️ **Nunca** comite o token diretamente no código. Sempre use Secrets.

### ▶️ Disparo Manual

Acesse **Actions → 🎰 Bot de Loterias — Telegram → Run workflow** para disparar sob demanda a qualquer momento, com campo opcional para informar o motivo.

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
