# Exemplo 08 — Testing com pytest

Projeto-exemplo da **Aula 08 — Testing que previne incidentes** do curso de
Desenvolvimento Backend. Inclui a aplicação MicroTask/Helpdesk completa e uma
suíte de testes pronta para rodar.

## Estrutura

```
Exemplo_08_pytest/
├── run.py                  Ponto de entrada (dev server)
├── pytest.ini              Configuração do pytest
├── pyproject.toml          Configuração de coverage (fail_under=80)
├── requirements.txt
├── .env.example            Template de variáveis (copiar para .env)
├── src/
│   └── microtask/
│       ├── __init__.py     create_app(test_config=None)
│       ├── config.py
│       ├── extensions.py   db, migrate
│       ├── models.py       User, Ticket, TicketUpdate (com @validates)
│       ├── auth_jwt.py     gerar_token, token_required, role_required
│       ├── blueprints/
│       │   ├── pages/      / e /sobre
│       │   ├── auth/       /auth/login (form e JSON), /auth/logout
│       │   ├── users/      CRUD + /users/registrar (anti mass assignment)
│       │   ├── tickets/    CRUD + /close + /reopen
│       │   └── api/        /api/tickets, /api/users, /api/me (JWT)
│       └── templates/
└── tests/
    ├── conftest.py         Fixtures: app, client, usuário, token_de, ...
    ├── test_smoke.py       4 testes
    ├── test_users.py       CRUD + parametrize (~17 testes)
    ├── test_tickets.py     CRUD + relações + parametrize (~14 testes)
    └── test_auth.py        Login, JWT, mass assignment, autorização (~17 testes)
```

## Como rodar

### 1) Preparar o ambiente

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 2) Configurar variáveis (opcional para testes)

```bash
cp .env.example .env
# Edite DATABASE_URL se for rodar o app contra MySQL real
```

> Para **rodar os testes**, NÃO é necessário ter MySQL local. A suíte usa
> SQLite em memória configurado pela fixture `app` em `tests/conftest.py`.

### 3) Rodar os testes

```bash
pytest                       # roda tudo
pytest -v                    # verboso
pytest -m auth               # só testes marcados com @pytest.mark.auth
pytest -m "crud and not slow"
pytest tests/test_auth.py    # só um arquivo
pytest -k "mass_assignment"  # só testes cujo nome contém o termo
```

### 4) Cobertura

```bash
# Relatório no terminal com linhas faltantes
pytest --cov=src/microtask --cov-report=term-missing --cov-branch

# Relatório HTML navegável (gera ./htmlcov/index.html)
pytest --cov=src/microtask --cov-report=html --cov-branch
```

A configuração de cobertura (`pyproject.toml`) está com `fail_under = 80`.
Se a cobertura cair abaixo disso, o `pytest` retorna exit code != 0 — útil
em pipelines de CI.

### 5) Rodar o app de verdade

```bash
# precisa de DATABASE_URL no .env apontando para um banco real
python run.py
# acesse http://127.0.0.1:5000
```

## Markers disponíveis

| Marker     | Para que serve                          |
|------------|-----------------------------------------|
| `auth`     | Testes de autenticação e autorização    |
| `crud`     | Operações CRUD                          |
| `security` | Mass assignment, autorização, hash      |
| `slow`     | Testes lentos (não usados ainda)        |

## Pontos didáticos cobertos

- **AAA pattern** em todo teste.
- **Fixtures** em `conftest.py` com escopo de função (banco recriado a cada teste).
- **Parametrize** para validação de input (e-mails inválidos, prioridades inválidas).
- **SQLite em memória** para isolamento e velocidade.
- **JWT** com expiração validada e forjada manualmente em teste.
- **Mass assignment**: payload com `role=admin` é ignorado pelo registro público.
- **Broken access control**: customer não fecha ticket de outro customer.
- **Cobertura de branch** habilitada via `pyproject.toml`.

## Saída esperada de `pytest`

```
============================ test session starts =============================
collected 52 items

tests/test_auth.py::test_senha_nao_eh_armazenada_em_texto_puro PASSED
tests/test_auth.py::test_login_com_credenciais_corretas_retorna_token PASSED
tests/test_auth.py::test_login_com_senha_errada_retorna_401 PASSED
tests/test_auth.py::test_usuario_nao_consegue_se_autopromover_a_admin PASSED
... (e por aí vai)

============================= 52 passed in X.XXs =============================
```
