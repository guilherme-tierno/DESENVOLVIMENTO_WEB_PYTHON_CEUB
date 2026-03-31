import pymysql

try:
    conexao = pymysql.connect(
        host="localhost",
        user="salvador",
        password="salvador",
        database="helpdesk_lite_db",
        port=3306
    )

    print("Conexão com o MySQL realizada com sucesso!")

    conexao.close()

except Exception as erro:
    print("Erro ao conectar no banco:")
    print(erro)