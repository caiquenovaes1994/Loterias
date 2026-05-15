import os
import requests

# 🎯 Configure aqui os seus jogos fixos
MEUS_JOGOS = {
    "megasena": [
        [4, 8, 15, 16, 23, 42],
        [10, 20, 30, 40, 50, 60]
    ],
    "lotofacil": [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    ]
}

def enviar_para_resumo(texto):
    """Escreve o resultado no dashboard do GitHub Actions ou no console local."""
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(texto + "\n")
    else:
        print(texto)

def conferir_loterias():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    enviar_para_resumo("## 🎰 Resultado da Conferência Automática\n")

    for loteria, jogos in MEUS_JOGOS.items():
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/{loteria}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                enviar_para_resumo(f"❌ Erro ao acessar API da {loteria.upper()} (Status: {response.status_code})")
                continue
                
            dados = response.json()
            concurso = dados.get("numero")
            data_sorteio = dados.get("dataApuracao")
            
            # Garante os números sorteados formatados como inteiros
            dezenas_sorteadas = [int(n) for n in dados.get("listaDezenas", [])]
            
            if not dezenas_sorteadas:
                enviar_para_resumo(f"⚠️ Não foi possível ler as dezenas do concurso {concurso} da {loteria.upper()}.")
                continue

            enviar_para_resumo(f"### 📊 {loteria.upper()} - Concurso {concurso} ({data_sorteio})")
            enviar_para_resumo(f"**Números Sorteados:** `{sorted(dezenas_sorteadas)}` \n")
            
            for i, jogo in enumerate(jogos, 1):
                # Identifica a interseção dos números
                acertos = set(jogo).intersection(set(dezenas_sorteadas))
                qtd_acertos = len(acertos)
                
                # Formatação visual do resultado
                status = "🟢 GANHOU ALGO?!" if qtd_acertos >= 4 else "⚪ Não foi dessa vez"
                enviar_para_resumo(
                    f"* **Jogo {i}:** `{sorted(jogo)}` | **Acertos:** `{qtd_acertos}` {status}\n"
                    f"  * *Números acertados:* {sorted(list(acertos)) if acertos else 'Nenhum'}"
                )
            enviar_para_resumo("\n---")
            
        except Exception as e:
            enviar_para_resumo(f"💥 Erro crítico ao processar {loteria.upper()}: {str(e)}")

if __name__ == "__main__":
    conferir_loterias()