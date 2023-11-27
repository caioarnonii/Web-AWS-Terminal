import subprocess
import time
import signal
import mysql.connector
import pyodbc

connection = mysql.connector.connect(
        host='localhost',
        database='streamoon',
        user='StreamoonUser',
        password='Moon2023'
    )

connectionSQLServer = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=127.0.0.1;'
            'DATABASE=streamoon;'
            'UID=StreamoonUser;'
            'PWD=Moon2023;'
            'TrustServerCertificate=yes;'
        )

idServidor = 2222

def execute_command(command: str):
    entrada_comando = command.split(' ')

    # Inicia o processo
    try:
        p = subprocess.Popen(entrada_comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except Exception as e:
        return str(e)

    try:
        # Aguarda por algum tempo (3 segundos neste exemplo)
        time.sleep(0.3)

    finally:
        # Envie um sinal SIGINT para tentar encerrar o processo
        try:
            p.send_signal(signal.SIGINT)
        except Exception as e:
            print(f"Erro ao enviar sinal SIGINT: {e}")

        # Aguarde um pouco mais para dar tempo ao processo para terminar
        time.sleep(2)

        # Se o processo ainda estiver ativo, tente encerrá-lo forçadamente com SIGTERM
        try:
            p.send_signal(signal.SIGTERM)
        except Exception as e:
            print(f"Erro ao enviar sinal SIGTERM: {e}")

        # Aguarde até que o processo termine
        p.wait()

    # Obtém a saída do comando
    saida_comando, erro_comando = p.communicate()

    saida_comando = saida_comando.encode('UTF-8')
    return saida_comando


# Conexão com o banco 

def selectDB():
    mySql_select = f"SELECT * FROM terminal WHERE fkServidor = {idServidor} AND retorno IS NULL ORDER BY idTerminal DESC LIMIT 1;"

    cursor = connection.cursor()

    cursor.execute(mySql_select)

    resultado = cursor.fetchone()
    print(resultado)

    if resultado != None and len(resultado) > 0:
        lastID = resultado[0]
        comando = resultado[1]

        saida_comando = execute_command(comando)

        updateDB(saida_comando, lastID)
        updateDBSQLServer(saida_comando, lastID)
    connection.commit()
    cursor.close()
    


def updateDB(saida_comando, lastId):
    saida_comando = saida_comando.decode('utf-8').replace('\"', "\'")
    mySql_update = f"UPDATE terminal set retorno = \"{saida_comando}\" WHERE idTerminal = {lastId}"

    cursor = connection.cursor()
    cursor.execute(mySql_update)

    connection.commit()
    cursor.close()


def updateDBSQLServer(saida_comando, lastId):
    saida_comando = saida_comando.decode('utf-8').replace('\"', "\'")
    mySql_update = f"UPDATE terminal set retorno = \"{saida_comando}\" WHERE idTerminal = {lastId}"

    cursor = connectionSQLServer.cursor()
    cursor.execute(mySql_update)

    connectionSQLServer.commit()
    cursor.close()



while True:
    selectDB()
    time.sleep(1)
