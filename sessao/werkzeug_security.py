from werkzeug.security import generate_password_hash, check_password_hash

# Cadastro
# senha --> ortega
senha = input("Crie sua senha: ")
senha_hash = generate_password_hash(senha)

print("Hash:", senha_hash)
print("Tamanho:", len(senha_hash))
print("\nAgora tente acessar...\n")

# Login
tentativa = input("Digite sua senha: ")
if check_password_hash(senha_hash, tentativa):
    print("acesso liberado")
else:
    print("acesso negado")
