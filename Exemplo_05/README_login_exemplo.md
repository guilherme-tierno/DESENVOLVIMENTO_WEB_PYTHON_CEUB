# HelpDesk Lite com Login

## O que foi alterado
- inclusão de `password_hash` na tabela `users`
- página de login em `/auth/login`
- uso de `generate_password_hash()` e `check_password_hash()`
- sessão com `session["user_id"]`
- proteção de rotas com `login_required`
- correção do formulário de usuário (`customer` e `agent`)

## Como executar
1. Crie o banco com o script `HelpDeskLiteDB_login.sql`.
2. Ajuste o `.env` com sua `DATABASE_URL`.
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Rode a aplicação:
   ```bash
   python run.py
   ```

## Usuário de teste
- E-mail: `marina.alves@campus.edu.br`
- Senha: `123456`
