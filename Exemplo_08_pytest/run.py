"""Ponto de entrada da aplicação Flask.

Para rodar em desenvolvimento:
    python run.py

Para rodar testes:
    pytest

A configuração de produção/desenvolvimento vem de variáveis de ambiente
(arquivo .env). Em ambiente de teste, o pytest sobrescreve via fixture.
"""

from microtask import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
