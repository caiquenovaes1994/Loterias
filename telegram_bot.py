"""
Bot do Telegram - Avisos em Tempo Real de Loterias
===================================================
Monitora as datas dos concursos definidas em jogos_pessoais.json e
envia notificações automáticas ao usuário antes dos sorteios.

Modos de operação:
  --ci       Modo GitHub Actions: execução única, sem loop de espera.
             Envia alertas e resultado para concursos com sorteio hoje/amanhã.
  (padrão)   Modo daemon local: loop contínuo com agendamento por threads.

Notificações enviadas:
  - 24h antes do sorteio
  -  1h antes do sorteio
  - No momento do sorteio (dispara conferência automática via API Caixa)
  - Resultado final com conferência dos jogos

Uso:
    python telegram_bot.py          # modo daemon (local)
    python telegram_bot.py --ci     # modo CI (GitHub Actions)

Variáveis de ambiente (opcionais, sobrepõem as constantes):
    TELEGRAM_TOKEN   Token do bot
    TELEGRAM_CHAT_ID ID do chat de destino
"""

import os
import sys
import json
import time
import logging
import threading
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# ─────────────────────────────────────────────
# Configurações
# ─────────────────────────────────────────────
# As credenciais NUNCA devem ser commitadas no repositório.
# Em produção (GitHub Actions): configure como Repository Secrets.
# Localmente: exporte as variáveis antes de rodar o script:
#   $env:TELEGRAM_TOKEN   = "<seu_token>"
#   $env:TELEGRAM_CHAT_ID = "<seu_chat_id>"
_token   = os.environ.get("TELEGRAM_TOKEN", "")
_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

if not _token or not _chat_id:
    print(
        "[ERRO] Variáveis de ambiente obrigatórias não definidas.\n"
        "  TELEGRAM_TOKEN   — token do bot (@BotFather)\n"
        "  TELEGRAM_CHAT_ID — ID do seu chat (@userinfobot)\n"
        "\nNo PowerShell:\n"
        "  $env:TELEGRAM_TOKEN   = 'SEU_TOKEN'\n"
        "  $env:TELEGRAM_CHAT_ID = 'SEU_CHAT_ID'",
        file=sys.stderr
    )
    sys.exit(1)

BOT_TOKEN = _token
CHAT_ID   = _chat_id
FUSO      = ZoneInfo("America/Sao_Paulo")
JSON_FILE = os.path.join(os.path.dirname(__file__), "jogos_pessoais.json")
API_BASE  = "https://servicebus2.caixa.gov.br/portaldeloterias/api"
TG_API    = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

# Controla quais alertas já foram enviados em modo daemon (evita duplicatas)
alertas_enviados: set[str] = set()


# ─────────────────────────────────────────────
# Telegram helpers
# ─────────────────────────────────────────────
def enviar_mensagem(texto: str, parse_mode: str = "HTML") -> bool:
    """Envia mensagem via Telegram Bot API."""
    try:
        resp = requests.post(
            f"{TG_API}/sendMessage",
            json={"chat_id": CHAT_ID, "text": texto, "parse_mode": parse_mode},
            timeout=10
        )
        data = resp.json()
        if data.get("ok"):
            log.info("✅ Mensagem enviada ao Telegram.")
            return True
        else:
            log.error("❌ Telegram API error: %s", data)
            return False
    except Exception as e:
        log.error("❌ Falha ao enviar mensagem: %s", e)
        return False


# ─────────────────────────────────────────────
# Mapeamentos de loterias
# ─────────────────────────────────────────────
DE_PARA = {
    "mega-sena": "megasena", "megasena": "megasena",
    "lotofacil": "lotofacil", "lotofácil": "lotofacil",
    "quina": "quina",
    "timemania": "timemania",
    "maismilionaria": "maismilionaria",
    "lotomania": "lotomania",
    "duplasena": "duplasena",
    "diadesorte": "diadesorte",
    "supersete": "supersete",
}

FAIXAS_MEGASENA  = {6: 1, 5: 2, 4: 3}
FAIXAS_LOTOFACIL = {15: 1, 14: 2, 13: 3, 12: 4, 11: 5}
FAIXAS_QUINA     = {5: 1, 4: 2, 3: 3, 2: 4}

EMOJIS = {
    "megasena": "🟢",
    "lotofacil": "🔵",
    "quina": "🟣",
    "timemania": "🟡",
    "maismilionaria": "🔴",
}


# ─────────────────────────────────────────────
# Helpers financeiros e de conferência
# ─────────────────────────────────────────────
def formatar_real(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def buscar_resultado(loteria: str, concurso: int) -> dict | None:
    endpoint = f"{loteria}/{concurso}" if concurso else loteria
    url = f"{API_BASE}/{endpoint}"
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        log.error("Erro ao buscar resultado de %s: %s", loteria, e)
    return None


def conferir_jogo(loteria: str, jogo_info, dez_sort: list, tre_sort: list,
                  time_sort: str, lista_rateio: list) -> str:
    if isinstance(jogo_info, dict):
        dezenas_user = [int(x) for x in jogo_info.get("dezenas", "").replace("-", " ").split()]
        trevos_user  = [int(x) for x in jogo_info.get("trevos", "").replace("-", " ").split()] if "trevos" in jogo_info else []
        time_user    = jogo_info.get("time", "").strip()
    else:
        dezenas_user = [int(x) for x in str(jogo_info).replace("-", " ").split()]
        trevos_user, time_user = [], ""

    acertos_dez  = len(set(dezenas_user) & set(dez_sort))
    acertos_tre  = len(set(trevos_user) & set(tre_sort))
    acertou_time = time_user.lower() == time_sort.lower() if time_user and time_sort else False

    faixa = None
    if loteria == "megasena":
        faixa = FAIXAS_MEGASENA.get(acertos_dez)
    elif loteria == "lotofacil":
        faixa = FAIXAS_LOTOFACIL.get(acertos_dez)
    elif loteria == "quina":
        faixa = FAIXAS_QUINA.get(acertos_dez)
    elif loteria == "timemania":
        faixa = {7: 1, 6: 2, 5: 3, 4: 4, 3: 5}.get(acertos_dez) if acertos_dez >= 3 else None
    elif loteria == "maismilionaria":
        faixas_mm = {
            (6, 2): 1, (6, 1): 2, (5, 2): 3, (5, 1): 4,
            (4, 2): 5, (4, 1): 6, (3, 2): 7, (3, 1): 8,
            (2, 2): 9, (2, 1): 10,
        }
        faixa = faixas_mm.get((acertos_dez, acertos_tre))

    premio = 0.0
    if faixa and lista_rateio:
        for item in lista_rateio:
            if item.get("faixa") == faixa:
                premio += float(item.get("valorPremio", 0))

    dez_fmt = sorted(dezenas_user)
    if loteria == "maismilionaria":
        linha = f"  <code>{dez_fmt}</code> + T:<code>{sorted(trevos_user)}</code> | ✔️ {acertos_dez}D+{acertos_tre}T"
    elif loteria == "timemania":
        t_ico = "✅" if acertou_time else "❌"
        linha = f"  <code>{dez_fmt}</code> | ✔️ {acertos_dez} | Time {time_user}: {t_ico}"
    else:
        linha = f"  <code>{dez_fmt}</code> | ✔️ {acertos_dez}"

    if premio > 0:
        linha += f"\n  💰 <b>PREMIADO!</b> {formatar_real(premio)}"

    return linha


def montar_mensagem_resultado(loteria: str, dados: dict, jogos: list) -> str:
    emoji    = EMOJIS.get(loteria, "🎰")
    num      = dados.get("numero", "?")
    data     = dados.get("dataApuracao", "?")
    dez_sort = [int(n) for n in dados.get("listaDezenas", [])]
    tre_sort = [int(n) for n in dados.get("listaTrevoSorteado", [])]
    time_sort = dados.get("nomeTimeCoracaoSorteado", "").strip()
    rateio   = dados.get("listaRateioPremio", [])

    if loteria == "maismilionaria":
        resultado = f"🔢 Resultado: <code>{sorted(dez_sort)}</code> | Trevos: <code>{sorted(tre_sort)}</code>\n"
    elif loteria == "timemania":
        resultado = f"🔢 Resultado: <code>{sorted(dez_sort)}</code> | Time: <b>{time_sort}</b>\n"
    else:
        resultado = f"🔢 Resultado: <code>{sorted(dez_sort)}</code>\n"

    linhas_jogos = []
    for i, jogo in enumerate(jogos, 1):
        linha = conferir_jogo(loteria, jogo, dez_sort, tre_sort, time_sort, rateio)
        linhas_jogos.append(f"<b>Jogo {i}:</b>\n{linha}")

    corpo  = "\n".join(linhas_jogos)
    titulo = f"{emoji} <b>{loteria.upper()}</b> — Concurso {num} ({data})\n"
    return f"{titulo}{resultado}\n👤 <b>Seus Jogos:</b>\n{corpo}"


# ─────────────────────────────────────────────
# Parsing de JSON e datas
# ─────────────────────────────────────────────
def carregar_jogos() -> dict:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_data_sorteio(iso_str: str | None) -> datetime | None:
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=FUSO)
        return dt
    except ValueError:
        return None


# ─────────────────────────────────────────────
# MODO CI — execução única para GitHub Actions
# ─────────────────────────────────────────────
def executar_modo_ci():
    """
    Execução única: sem loop, sem threads de espera.
    Lógica baseada em quando o workflow é disparado:
      - Se o sorteio é HOJE (pós-hora): busca resultado e confere jogos.
      - Se o sorteio é HOJE (pré-hora): aviso com contagem regressiva.
      - Se o sorteio é AMANHÃ: lembrete de 24h.
      - Se não há nada hoje/amanhã: envia digest dos próximos 7 dias.
    """
    log.info("🤖 Modo CI ativado.")
    jogos_data = carregar_jogos()
    agora      = datetime.now(tz=FUSO)
    hoje       = agora.date()
    amanha     = (agora + timedelta(days=1)).date()
    limite_7d  = hoje + timedelta(days=7)
    mensagens_enviadas = 0
    proximos: list[tuple] = []  # (dt_sorteio, loteria, concurso, emoji)

    for nome_bruto, config in jogos_data.items():
        loteria  = DE_PARA.get(nome_bruto, nome_bruto)
        concurso = config.get("concurso")
        jogos    = config.get("jogos", [])
        dt_str   = config.get("data_sorteio")

        if not concurso or not jogos:
            log.info("Sem jogos registrados para %s — pulando.", loteria)
            continue

        if not dt_str:
            log.info("Sem data de sorteio para %s — pulando.", loteria)
            continue

        dt_sorteio = parse_data_sorteio(dt_str)
        if not dt_sorteio:
            continue

        data_sorteio = dt_sorteio.date()
        hora_fmt     = dt_sorteio.strftime("%H:%M")
        emoji        = EMOJIS.get(loteria, "🎰")

        # Coleta para o digest semanal (inclui hoje e amanhã também)
        if hoje <= data_sorteio <= limite_7d:
            proximos.append((dt_sorteio, loteria, concurso, emoji))

        # ── Sorteio AMANHÃ: envia lembrete de 24h ──
        if data_sorteio == amanha:
            msg = (
                f"{emoji} <b>Lembrete — Sorteio Amanhã!</b>\n\n"
                f"<b>{loteria.upper()}</b> — Concurso <b>{concurso}</b>\n"
                f"📅 {dt_sorteio.strftime('%d/%m/%Y')} às <b>{hora_fmt}</b>\n\n"
                f"Seus jogos já estão registrados. Boa sorte! 🍀"
            )
            if enviar_mensagem(msg):
                mensagens_enviadas += 1

        # ── Sorteio HOJE: busca resultado ou avisa ──
        elif data_sorteio == hoje:
            if agora >= dt_sorteio:
                log.info("Buscando resultado de %s/%d...", loteria, concurso)
                dados = None
                for tentativa in range(1, 4):
                    dados = buscar_resultado(loteria, concurso)
                    if dados and dados.get("listaDezenas"):
                        break
                    log.warning("Tentativa %d falhou. Aguardando 60s...", tentativa)
                    time.sleep(60)

                if dados and dados.get("listaDezenas"):
                    msg = montar_mensagem_resultado(loteria, dados, jogos)
                    if enviar_mensagem(msg):
                        mensagens_enviadas += 1
                else:
                    enviar_mensagem(
                        f"⚠️ Não consegui buscar o resultado do <b>{loteria.upper()}</b> "
                        f"concurso <b>{concurso}</b>.\n"
                        f"Verifique em loterias.caixa.gov.br"
                    )
                    mensagens_enviadas += 1
            else:
                delta_min = int((dt_sorteio - agora).total_seconds() / 60)
                msg = (
                    f"{emoji} <b>Sorteio Hoje!</b>\n\n"
                    f"<b>{loteria.upper()}</b> — Concurso <b>{concurso}</b>\n"
                    f"🕐 Começa às <b>{hora_fmt}</b> "
                    f"(em aproximadamente {delta_min} min)\n\n"
                    f"Boa sorte! 🎯"
                )
                if enviar_mensagem(msg):
                    mensagens_enviadas += 1
        else:
            log.info("Sorteio de %s em %s — fora da janela imediata.", loteria, data_sorteio)

    # ── Digest semanal: dispara quando nada foi enviado hoje/amanhã ──
    if mensagens_enviadas == 0:
        if proximos:
            proximos.sort(key=lambda t: t[0])
            data_exec = agora.strftime("%d/%m/%Y %H:%M")
            linhas = []
            for dt, lot, conc, em in proximos:
                dias = (dt.date() - hoje).days
                if dias == 0:
                    quando = "<b>HOJE</b>"
                elif dias == 1:
                    quando = "<b>Amanhã</b>"
                else:
                    quando = f"<b>{dt.strftime('%d/%m')} ({dias} dias)</b>"
                linhas.append(
                    f"{em} <b>{lot.upper()}</b> #{conc}\n"
                    f"   📅 {quando} às {dt.strftime('%H:%M')}"
                )
            corpo = "\n\n".join(linhas)
            msg = (
                f"📆 <b>Próximos Sorteios — {data_exec}</b>\n\n"
                f"{corpo}\n\n"
                f"<i>Nenhum alerta imediato nesta execução. "
                f"O bot rodará novamente nos horários programados.</i> 🤖"
            )
            if enviar_mensagem(msg):
                mensagens_enviadas += 1
                log.info("📆 Digest semanal enviado (%d sorteios listados).", len(proximos))
        else:
            log.info("Nenhum sorteio configurado nos próximos 7 dias. Nada enviado.")
    else:
        log.info("✅ %d mensagem(ns) enviada(s) com sucesso.", mensagens_enviadas)


# ─────────────────────────────────────────────
# MODO DAEMON — execução local contínua
# ─────────────────────────────────────────────
def chave_alerta(loteria: str, concurso: int, tipo: str) -> str:
    return f"{loteria}:{concurso}:{tipo}"


def agendar_alerta(loteria: str, concurso: int, dt_sorteio: datetime,
                   delta: timedelta, tipo: str, mensagem_fn):
    agora  = datetime.now(tz=FUSO)
    disparo = dt_sorteio - delta
    espera  = (disparo - agora).total_seconds()
    chave   = chave_alerta(loteria, concurso, tipo)

    if chave in alertas_enviados:
        return
    if espera <= 0:
        log.info("Horário de alerta [%s] já passou para %s. Pulando.", tipo, loteria)
        return

    log.info("⏳ Agendando alerta [%s] para %s em %.0f segundos.", tipo, loteria, espera)

    def disparar():
        time.sleep(espera)
        alertas_enviados.add(chave)
        enviar_mensagem(mensagem_fn())
        log.info("🔔 Alerta [%s] disparado para %s.", tipo, loteria)

    threading.Thread(target=disparar, daemon=True).start()


def agendar_conferencia_daemon(loteria: str, concurso: int, jogos: list, dt_sorteio: datetime):
    chave = chave_alerta(loteria, concurso, "resultado")
    if chave in alertas_enviados:
        return

    agora   = datetime.now(tz=FUSO)
    disparo = dt_sorteio + timedelta(minutes=30)
    espera  = max((disparo - agora).total_seconds(), 0)

    def conferir():
        time.sleep(espera)
        for tentativa in range(1, 6):
            log.info("🔍 Tentativa %d — resultado %s/%d", tentativa, loteria, concurso)
            dados = buscar_resultado(loteria, concurso)
            if dados and dados.get("listaDezenas"):
                alertas_enviados.add(chave)
                enviar_mensagem(montar_mensagem_resultado(loteria, dados, jogos))
                return
            time.sleep(300)
        enviar_mensagem(
            f"⚠️ Não consegui buscar o resultado do <b>{loteria.upper()}</b> "
            f"concurso <b>{concurso}</b>.\nVerifique em loterias.caixa.gov.br"
        )

    threading.Thread(target=conferir, daemon=True).start()


def executar_modo_daemon():
    log.info("🚀 Bot de Loterias iniciado (modo daemon).")
    enviar_mensagem(
        "🤖 <b>Bot de Loterias iniciado!</b>\n\n"
        "Vou te avisar antes dos sorteios e enviar a conferência automática. ✅"
    )

    while True:
        jogos_data = carregar_jogos()
        agora = datetime.now(tz=FUSO)

        for nome_bruto, config in jogos_data.items():
            loteria  = DE_PARA.get(nome_bruto, nome_bruto)
            concurso = config.get("concurso")
            jogos    = config.get("jogos", [])
            dt_str   = config.get("data_sorteio")

            if not concurso or not jogos:
                continue

            dt_sorteio = parse_data_sorteio(dt_str)
            if not dt_sorteio or dt_sorteio < agora - timedelta(hours=2):
                continue

            emoji = EMOJIS.get(loteria, "🎰")

            agendar_alerta(
                loteria, concurso, dt_sorteio,
                delta=timedelta(hours=24), tipo="24h",
                mensagem_fn=lambda l=loteria, c=concurso, d=dt_sorteio, e=emoji: (
                    f"{e} <b>Lembrete 24h!</b>\n\nAmanhã tem <b>{l.upper()}</b>!\n"
                    f"📅 Concurso <b>{c}</b>\n🕐 Sorteio às <b>{d.strftime('%H:%M')}</b> "
                    f"de {d.strftime('%d/%m/%Y')}\n\nBoa sorte! 🍀"
                )
            )
            agendar_alerta(
                loteria, concurso, dt_sorteio,
                delta=timedelta(hours=1), tipo="1h",
                mensagem_fn=lambda l=loteria, c=concurso, d=dt_sorteio, e=emoji: (
                    f"{e} <b>Falta 1 hora!</b>\n\nO sorteio da <b>{l.upper()}</b> "
                    f"começa às <b>{d.strftime('%H:%M')}</b>!\n"
                    f"📋 Concurso <b>{c}</b>\n\nSeus jogos já estão confirmados? 🎯"
                )
            )
            agendar_alerta(
                loteria, concurso, dt_sorteio,
                delta=timedelta(seconds=0), tipo="inicio",
                mensagem_fn=lambda l=loteria, c=concurso, e=emoji: (
                    f"{e} <b>O sorteio começou!</b>\n\n<b>{l.upper()}</b> — "
                    f"Concurso <b>{c}</b>\nAguardando resultado... 🥁\n\n"
                    f"Em instantes envio a conferência dos seus jogos!"
                )
            )
            agendar_conferencia_daemon(loteria, concurso, jogos, dt_sorteio)

        time.sleep(600)


# ─────────────────────────────────────────────
# Entrada
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if "--ci" in sys.argv:
        executar_modo_ci()
    else:
        executar_modo_daemon()
