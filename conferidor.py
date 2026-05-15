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

def processar_lista_jogos(jogos, loteria, dezenas_sort, trevos_sort, time_sort, label):
    if not jogos:
        return
    
    enviar_para_resumo(f"#### {label}")
    for i, jogo_info in enumerate(jogos, 1):
        dezenas_user = []
        trevos_user = []
        time_user = ""
        
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
        
        # Lógica de prêmios (usando nome normalizado da loteria)
        premio = ""
        if (loteria == "megasena" and qtd_dez >= 4) or (loteria == "lotofacil" and qtd_dez >= 11):
            premio = "💰 **PREMIAÇÃO!**"
        elif loteria == "maismilionaria" and ((qtd_dez >= 2 and qtd_tre >= 1) or (qtd_tre == 2) or (qtd_dez >= 3)):
            premio = "💰 **PREMIAÇÃO!**"
        elif loteria == "timemania" and (qtd_dez >= 3 or acertou_time):
            premio = "💰 **PREMIAÇÃO!**"
            
        # Formatação de saída
        if loteria == "maismilionaria":
            enviar_para_resumo(f"* **Jogo {i}:** `{sorted(dezenas_user)}` + T:`{sorted(trevos_user)}` | Acertos: `{qtd_dez}D+{qtd_tre}T` {premio}")
        elif loteria == "timemania":
            t_status = "✅" if acertou_time else "❌"
            enviar_para_resumo(f"* **Jogo {i}:** `{sorted(dezenas_user)}` | Acertos: `{qtd_dez}` | Time {time_user}: {t_status} {premio}")
        else:
            enviar_para_resumo(f"* **Jogo {i}:** `{sorted(dezenas_user)}` | Acertos: `{qtd_dez}` {premio}")

def conferir_loterias():
    pessoais = carregar_json('jogos_pessoais.json')
    bolao = carregar_json('jogos_bolao.json')
    
    # Lista todas as loterias citadas em ambos os arquivos
    todas_loterias_brutas = set(list(pessoais.keys()) + list(bolao.keys()))
    
    headers = {"User-Agent": "Mozilla/5.0"}
    enviar_para_resumo("## 🎰 Conferência Consolidada\n")

    # Dicionário para evitar processar a mesma loteria normalizada duas vezes
    # (caso o usuário use "MegaSena" em um arquivo e "mega-sena" no outro)
    loterias_processadas = set()

    for nome_bruto in todas_loterias_brutas:
        loteria = normalizar_nome_loteria(nome_bruto)
        
        if loteria in loterias_processadas:
            continue
        loterias_processadas.add(loteria)

        # Busca concurso em ambos os arquivos (usando a chave original ou normalizada)
        # Para ser robusto, verificamos tanto a chave bruta quanto as outras possíveis
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
            
            enviar_para_resumo(f"### 📊 {loteria.upper()} - Concurso {num} ({data})")
            
            # Processa cada categoria (buscando pelo nome bruto original)
            processar_lista_jogos(pessoais.get(nome_bruto, {}).get("jogos"), loteria, dez_sort, tre_sort, time_sort, "👤 Jogos Pessoais")
            processar_lista_jogos(bolao.get(nome_bruto, {}).get("jogos"), loteria, dez_sort, tre_sort, time_sort, "👥 Jogos de Bolão")
            
            enviar_para_resumo("\n---")
        except Exception as e:
            # Mostra o nome original no erro para facilitar identificação
            enviar_para_resumo(f"💥 Erro em {nome_bruto}: {e}")

if __name__ == '__main__':
    conferir_loterias()
