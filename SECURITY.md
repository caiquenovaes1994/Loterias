# 🔒 Política de Segurança

## Versões Suportadas

| Versão | Suporte          |
| ------ | ---------------- |
| main   | ✅ Suportada     |

## Reportando uma Vulnerabilidade

Se você descobrir uma vulnerabilidade de segurança neste projeto, **não abra uma Issue pública**. Em vez disso, reporte de forma responsável através de um dos canais abaixo:

📧 **E-mail:** [caiquenovaes1994@gmail.com](mailto:caiquenovaes1994@gmail.com)

### O que incluir no seu reporte

- Descrição clara da vulnerabilidade
- Passos para reprodução (se aplicável)
- Impacto potencial
- Sugestão de correção (se possível)

### O que esperar

- **Confirmação de recebimento:** em até 48 horas
- **Avaliação inicial:** em até 7 dias úteis
- **Resolução:** depende da severidade, mas você será mantido(a) informado(a) sobre o progresso

## Boas Práticas de Segurança

Este projeto adota as seguintes práticas para proteger dados sensíveis:

### 🔐 Secrets e Credenciais

- Tokens de API (Telegram, WhatsApp) **nunca são commitados** no repositório
- Credenciais são gerenciadas exclusivamente via [GitHub Secrets](https://docs.github.com/pt/actions/security-guides/encrypted-secrets)
- O `.gitignore` inclui proteção contra arquivos `.env`, `secrets.json` e `*.token`

### ⚙️ GitHub Actions

- O workflow opera com permissão mínima (`contents: read`)
- Nenhum dado sensível é exposto nos logs do workflow
- O bot executa em modo CI com `timeout-minutes: 10` para evitar execuções descontroladas

### 🌐 Comunicação Externa

- As chamadas à API da Caixa utilizam HTTPS
- As chamadas à API do Telegram utilizam HTTPS
- Nenhum dado pessoal é armazenado em bancos de dados externos

## Escopo

Esta política cobre exclusivamente o código e a infraestrutura deste repositório. Vulnerabilidades em serviços de terceiros (API Caixa, Telegram Bot API, CallMeBot) devem ser reportadas aos respectivos mantenedores.
