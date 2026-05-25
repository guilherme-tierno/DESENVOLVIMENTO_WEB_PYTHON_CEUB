import bcrypt

# Cadastro
# senha --> ortega
senha = input("Crie sua senha: ")
senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

print("Hash:", senha_hash)
print("Tamanho:", len(senha_hash))
print("\nAgora tente acessar...\n")

# Login
tentativa = input("Digite sua senha: ")
if bcrypt.checkpw(tentativa.encode('utf-8'), senha_hash):
    print("acesso liberado")
else:
    print("acesso negado")
