# Dia 2 – Login que resiste a ataques

## Relatório de correção das falhas de autenticação

### 1. Objetivo

Corrigir as falhas de autenticação identificadas no Dia 1 na API do Banco Pop: senhas guardadas em texto puro, token de sessão que qualquer pessoa consegue fabricar e login sem limite de tentativas.

### 2. Metodologia

As correções foram feitas em três arquivos: `app/security.py`, `app/config.py` e `app/routes/auth.py`. Foram adicionadas duas bibliotecas ao `requirements.txt`, com as versões fixadas:

- `pwdlib[argon2]==0.3.1`, para o hash das senhas;
- `PyJWT==2.15.1`, para gerar e conferir o token assinado.

O segredo de assinatura do token saiu do código e passou a ser lido do arquivo `.env`, que está no `.gitignore` e não vai para o repositório.

Depois de cada correção, o banco foi recriado com `python seed.py` e o mesmo ataque foi repetido, para confirmar que ele deixou de funcionar.

### 3. Falhas corrigidas

#### 3.1. Senha guardada em texto puro

- **Arquivo:** `app/security.py`
- **Antes:** `guardar_senha` devolvia a senha como ela foi digitada, e `conferir_senha` comparava os dois textos diretamente.
- **Correção:** as senhas passam a ser guardadas como hash Argon2, com um salt diferente para cada senha.

```python
hasher = PasswordHash.recommended()

def guardar_senha(senha: str) -> str:
    return hasher.hash(senha)

def conferir_senha(senha_enviada: str, senha_guardada: str) -> bool:
    return hasher.verify(senha_enviada, senha_guardada)
```

- **Verificação:** com o usuário bruno autenticado, `GET /usuarios/1` devolveu a senha da ana como `$argon2id$v=19$m=65536,t=3,p=4$...`, e não mais `ana123`.
- **Classificação OWASP:** API2 – Broken Authentication.

**Análise:** Se o banco de dados vazar, o que sai agora é o hash, que não pode ser revertido para a senha original. O salt faz duas senhas iguais gerarem hashes diferentes.

#### 3.2. Token de sessão sem assinatura e sem validade

- **Arquivos:** `app/security.py` e `app/config.py`
- **Antes:** o token era só um JSON em base64 (`{"sub": 1, "nome": ..., "papel": ...}`). Qualquer pessoa conseguia montar um token com o `sub` de outro usuário e entrar na conta dele sem senha. O segredo estava escrito no código (`SEGREDO = "banco-pop-123"`).
- **Correção:** o token passa a ser um JWT assinado com HS256, com validade de 30 minutos. O segredo é lido do `.env`.

```python
def criar_token(usuario: Usuario) -> str:
    conteudo = {
        "sub": str(usuario.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_DO_TOKEN),
    }
    return jwt.encode(conteudo, SEGREDO, algorithm="HS256")
```

O `ler_token` usa `jwt.decode`, que confere a assinatura e a validade, e devolve `None` em caso de `jwt.InvalidTokenError`. O `usuario_logado` busca o usuário com `int(conteudo["sub"])`.

- **Verificação:** o token forjado do Dia 1 (`eyJzdWIiOiAxfQ==`, que é `{"sub": 1}` em base64) foi enviado para `GET /usuarios/eu` e recebeu `401 Unauthorized` com `{"detail":"token inválido"}`.
- **Classificação OWASP:** API2 – Broken Authentication; API8 – Security Misconfiguration (segredo no código).

**Análise:** Sem o segredo, não é possível gerar uma assinatura válida, então alterar o conteúdo do token o invalida. O `sub` foi gravado como texto porque as versões recentes do PyJWT recusam `sub` numérico. O token também deixou de carregar `nome` e `papel`, porque o conteúdo de um JWT pode ser lido por qualquer pessoa que tenha o token.

#### 3.3. Login sem limite de tentativas

- **Arquivo:** `app/routes/auth.py`
- **Antes:** o login respondia a todas as tentativas, sem limite, o que permitia testar senhas em massa (força bruta).
- **Correção:** a API guarda, para cada nome de usuário, os horários das tentativas erradas. Com 5 erros nos últimos 5 minutos, ela responde `429 Too Many Requests` antes mesmo de conferir a senha. Um login certo zera a contagem.

```python
MAX_ERROS = 5
SEGUNDOS_DE_ESPERA = 300
erros_de_login: dict[str, list[float]] = {}
```

- **Verificação:** `python ataques/tentativas_de_login.py` mostrou cinco respostas `401` para as senhas erradas e `429` na sexta tentativa, mesmo com a senha certa (`ana123`).
- **Classificação OWASP:** API2 – Broken Authentication.

**Análise:** O bloqueio é por nome de usuário e acontece antes da conferência da senha, então quem está bloqueado não consegue nem testar se acertou. Os outros usuários continuam entrando normalmente.

### 4. Resumo dos resultados

| Falha | Arquivo | Ataque repetido | Antes | Depois | Risco OWASP |
|:---|:---|:---|:---|:---|:---|
| Senha em texto puro | `app/security.py` | `GET /usuarios/1` como bruno | `ana123` | `$argon2id$...` | **API2** |
| Token sem assinatura | `app/security.py` | Token forjado `{"sub": 1}` | Acesso à conta da ana | `401 token inválido` | **API2** |
| Segredo no código | `app/config.py` | Leitura do código-fonte | Segredo visível | Lido do `.env` | **API8** |
| Login sem limite | `app/routes/auth.py` | `tentativas_de_login.py` | `401` sem limite | 5× `401`, depois `429` | **API2** |

### 5. Pontos que continuam em aberto

- `GET /usuarios/1` ainda devolve o campo `senha` (agora como hash) e o Bruno ainda consegue consultar dados da Ana. Essas falhas de autorização e exposição de dados são corrigidas nos Dias 3 e 4.
- A contagem de tentativas fica na memória da API: ela é zerada quando a API reinicia e não é compartilhada entre várias instâncias. Para uma API em produção, essa contagem iria para um armazenamento compartilhado.

### 6. Conclusão

As três falhas de autenticação identificadas no Dia 1 foram corrigidas e verificadas repetindo o ataque original. A API passou a guardar só o hash das senhas, a emitir tokens assinados com prazo de validade e a bloquear tentativas de login em massa. O segredo de assinatura saiu do código.

A API agora sabe com segurança **quem** está fazendo cada requisição. O próximo passo é conferir **o que** cada pessoa pode acessar, que é o tema do Dia 3.
