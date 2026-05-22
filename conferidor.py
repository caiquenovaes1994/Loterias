import os
import requests
import json

DE_PARA_LOTERIAS = {
    # Mega-Sena
    "mega-sena": "megasena",
    "mega sena": "megasena",
    "megasena": "megasena",
    "mega-senha": "megasena",
    "mega-sena da virada": "megasena",
    "mega da virada": "megasena",
    "megadavirada": "megasena",
    
    # Lotofácil
    "lotofácil": "lotofacil",
    "lotofacil": "lotofacil",
    "loto fácil": "lotofacil",
    "loto facil": "lotofacil",
    
    # Quina
    "quina": "quina",
    
    # Lotomania
    "lotomania": "lotomania",
    "loto mania": "lotomania",
    
    # Timemania
    "timemania": "timemania",
    "time mania": "timemania",
    
    # Dupla Sena
    "dupla sena": "duplasena",
    "dupla-sena": "duplasena",
    "duplasena": "duplasena",
    
    # Federal
    "federal": "federal",
    "loteria federal": "federal",
    
    # Dia de Sorte
    "dia de sorte": "diadesorte",
    "diadesorte": "diadesorte",
    
    # Super Sete
    "super sete": "supersete",
    "supersete": "supersete",
    
    # +Milionária
    "mais milionária": "maismilionaria",
    "mais milionaria": "maismilionaria",
    "maismilionaria": "maismilionaria",
    "+milionaria": "maismilionaria",
    "+milionária": "maismilionaria"
}

def normalizar_nome_loteria(nome_usuario):
    """Normaliza o nome da loteria para o padrão esperado pela API."""
    nome_limpo = nome_usuario.lower().strip()
    return DE_PARA_LOTERIAS.get(nome_limpo, nome_limpo)

def carregar_json(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def enviar_para_resumo(texto):
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(texto + "\n")
    else:
        print(texto)

def formatar_real(valor):
    """Formata valor numérico para o padrão monetário brasileiro."""
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def calcular_premio_caixa(loteria, qtd_dez, qtd_tre, acertou_time, lista_rateio):
    """Mapeia o resultado do usuário com a faixa de premiação da API e retorna o valor."""
    if not lista_rateio:
        return 0.0
    
    faixas_ganhas = []
    if loteria == "megasena":
        faixa = {6: 1, 5: 2, 4: 3}.get(qtd_dez)
        if faixa: faixas_ganhas.append(faixa)
    elif loteria == "lotofacil":
        faixa = {15: 1, 14: 2, 13: 3, 12: 4, 11: 5}.get(qtd_dez)
        if faixa: faixas_ganhas.append(faixa)
    elif loteria == "timemania":
        if qtd_dez >= 3:
            faixa_dez = {7: 1, 6: 2, 5: 3, 4: 4, 3: 5}.get(qtd_dez)
            if faixa_dez: faixas_ganhas.append(faixa_dez)
        if acertou_time:
            faixas_ganhas.append(6) # Faixa 6 é o Time do Coração
    elif loteria == "maismilionaria":
        faixa = None
        if qtd_dez == 6 and qtd_tre == 2: faixa = 1
        elif qtd_dez == 6 and qtd_tre == 1: faixa = 2
        elif qtd_dez == 5 and qtd_tre == 2: faixa = 3
        elif qtd_dez == 5 and qtd_tre == 1: faixa = 4
        elif qtd_dez == 4 and qtd_tre == 2: faixa = 5
        elif qtd_dez == 4 and qtd_tre == 1: faixa = 6
        elif qtd_dez == 3 and qtd_tre == 2: faixa = 7
        elif qtd_dez == 3 and qtd_tre == 1: faixa = 8
        elif qtd_dez == 2 and qtd_tre == 2: faixa = 9
        elif qtd_dez == 2 and qtd_tre == 1: faixa = 10
        if faixa: faixas_ganhas.append(faixa)
        
    valor_total = 0.0
    for f in faixas_ganhas:
        for item in lista_rateio:
            if item.get("faixa") == f:
                valor_total += float(item.get("valorPremio", 0))
    return valor_total

def processar_lista_jogos(jogos, loteria, dezenas_sort, trevos_sort, time_sort, lista_rateio, label, meta_bolao=None):
    if not jogos:
        return
    
    enviar_para_resumo(f"#### {label}")
    if meta_bolao:
        part = meta_bolao.get("quantidade_cotas", meta_bolao.get("total_participantes", 1))
        cota = meta_bolao.get("valor_cota", meta_bolao.get("valor_cota_paga", 0.0))
        enviar_para_resumo(f"ℹ️ *Configuração do Bolão: {part} cotas | Valor da cota: {formatar_real(cota)}*")

    for i, jogo_info in enumerate(jogos, 1):
        dezenas_user, trevos_user, time_user = [], [], ""
        
        if isinstance(jogo_info, dict):
            dezenas_user = [int(x.strip()) for x in jogo_info.get("dezenas", "").replace('-', ' ').split()]
            trevos_user = [int(x.strip()) for x in jogo_info.get("trevos", "").replace('-', ' ').split()] if "trevos" in jogo_info else []
            time_user = jogo_info.get("time", "").strip()
        else:
            dezenas_user = [int(x.strip()) for x in jogo_info.replace('-', ' ').split()]
        
        acertos_dez = set(dezenas_user).intersection(set(dezenas_sort))
        qtd_dez = len(acertos_dez)
        acertos_tre = set(trevos_user).intersection(set(trevos_sort))
        qtd_tre = len(acertos_tre)
        acertou_time = time_user.lower() == time_sort.lower() if time_user and time_sort else False
        
        # Calcula prêmio oficial
        valor_premio = calcular_premio_caixa(loteria, qtd_dez, qtd_tre, acertou_time, lista_rateio)
        
        premio_tag = ""
        financeiro_str = ""
        if valor_premio > 0:
            premio_tag = "💰 **PREMIAÇÃO!**"
            if meta_bolao:
                part = meta_bolao.get("quantidade_cotas", meta_bolao.get("total_participantes", 1))
                valor_por_cota = valor_premio / part
                financeiro_str = f"\n  * 💵 **Prêmio Total:** {formatar_real(valor_premio)} | 💸 **Cada Cota Recebe:** {formatar_real(valor_por_cota)}"
            else:
                financeiro_str = f"\n  * 💵 **Prêmio Total:** {formatar_real(valor_premio)} (100% Seu)"

        # Formatação de saída Markdown
        if loteria == "maismilionaria":
            enviar_para_resumo(f"* **Jogo {i}:** `{sorted(dezenas_user)}` + T:`{sorted(trevos_user)}` | Acertos: `{qtd_dez}D+{qtd_tre}T` {premio_tag}{financeiro_str}")
        elif loteria == "timemania":
            t_status = "✅" if acertou_time else "❌"
            enviar_para_resumo(f"* **Jogo {i}:** `{sorted(dezenas_user)}` | Acertos: `{qtd_dez}` | Time {time_user}: {t_status} {premio_tag}{financeiro_str}")
        else:
            enviar_para_resumo(f"* **Jogo {i}:** `{sorted(dezenas_user)}` | Acertos: `{qtd_dez}` {premio_tag}{financeiro_str}")

def conferir_loterias():
    pessoais = carregar_json('jogos_pessoais.json')
    bolao = carregar_json('jogos_bolao.json')
    
    todas_loterias_brutas = set(list(pessoais.keys()) + list(bolao.keys()))
    
    headers = {"User-Agent": "Mozilla/5.0"}
    enviar_para_resumo("## 🎰 Conferência Consolidada Financeira\n")

    loterias_processadas = set()

    for nome_bruto in todas_loterias_brutas:
        loteria = normalizar_nome_loteria(nome_bruto)
        
        if loteria in loterias_processadas:
            continue
        loterias_processadas.add(loteria)

        conc_p = pessoais.get(nome_bruto, {}).get("concurso")
        conc_b = bolao.get(nome_bruto, {}).get("concurso")
        concurso = conc_p or conc_b
        
        endpoint = f"{loteria}/{concurso}" if concurso else loteria
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/{endpoint}"
        
        try:
            res = requests.get(url, headers=headers, timeout=15).json()
            num = res.get("numero")
            data = res.get("dataApuracao")
            dez_sort = [int(n) for n in res.get("listaDezenas", [])]
            tre_sort = [int(n) for n in res.get("listaTrevoSorteado", [])]
            time_sort = res.get("nomeTimeCoracaoSorteado", "").strip()
            lista_rateio = res.get("listaRateioPremio", [])
            
            enviar_para_resumo(f"### 📊 {loteria.upper()} - Concurso {num} ({data})")
            
            if loteria == "maismilionaria":
                enviar_para_resumo(f"**Resultado Oficial:** Dezenas `{sorted(dez_sort)}` | Trevos `{sorted(tre_sort)}` \n")
            elif loteria == "timemania":
                enviar_para_resumo(f"**Resultado Oficial:** Dezenas `{sorted(dez_sort)}` | Time: **{time_sort}** \n")
            else:
                enviar_para_resumo(f"**Resultado Oficial:** `{sorted(dez_sort)}` \n")
            
            # Jogos Pessoais
            processar_lista_jogos(pessoais.get(nome_bruto, {}).get("jogos"), loteria, dez_sort, tre_sort, time_sort, lista_rateio, "👤 Jogos Pessoais")
            
            # Jogos de Bolão com Metadados Financeiros
            meta_b = {
                "quantidade_cotas": bolao.get(nome_bruto, {}).get("quantidade_cotas", bolao.get(nome_bruto, {}).get("total_participantes", 1)),
                "valor_cota": bolao.get(nome_bruto, {}).get("valor_cota", bolao.get(nome_bruto, {}).get("valor_cota_paga", 0.0))
            } if bolao.get(nome_bruto, {}).get("jogos") else None
            
            processar_lista_jogos(bolao.get(nome_bruto, {}).get("jogos"), loteria, dez_sort, tre_sort, time_sort, lista_rateio, "👥 Jogos de Bolão", meta_b)
            
            enviar_para_resumo("\n---")
        except Exception as e:
            enviar_para_resumo(f"💥 Erro em {nome_bruto}: {e}")

if __name__ == '__main__':
    conferir_loterias()
