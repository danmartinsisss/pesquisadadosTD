from flask import Flask, render_template, request, jsonify, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = '$2b$12$ky.1Vk81lEgbrIVOTTvVm.7vJUUlSpiaxdZhCNBeqG2u2YhsV/zN6'


db_config = {
    "host": "#",
    "user": "#",
    "password": "#",
    "database": '#',
    "charset": "utf8",
    "port": #
}

def connect_to_database_login(db_config):
    try:
        connection = mysql.connector.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            charset=db_config["charset"],
            port=db_config["port"]
            
        )
        return connection

    except mysql.connector.Error as error:
        print(f"Erro ao conectar ao banco de dados: {error}")
        return None

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            charset=db_config["charset"],
            port=db_config["port"]
        )
        return connection

    except mysql.connector.Error as error:
        print(f"Erro ao conectar ao banco de dados: {error}")
        return None

def execute_query(query, params):
    connection = connect_to_database()

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            connection.close()
            return results

        except mysql.connector.Error as error:
            print(f"Erro ao executar a consulta: {error}")
            connection.close()
            return []

    else:
        return []

@app.route("/certidao_td")
def landing_page():
    return render_template("certidao_td.html", session=session)

@app.route("/")
def index():
    return render_template("certidao_td.html")

def execute_query_td(query, params):
    connection = connect_to_database()

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            connection.close()
            return results

        except mysql.connector.Error as error:
            print(f"Erro ao executar a consulta: {error}")
            connection.close()
            return []

    else:
        return []

def execute_query_orcamento(query, params):
    connection = connect_to_database()

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            connection.close()
            return results

        except mysql.connector.Error as error:
            print(f"Erro ao executar a consulta: {error}")
            connection.close()
            return []

    else:
        return []

@app.route("/consulta", methods=["GET", "POST"])
def consulta():
    if request.method == "POST":
        cpf_or_cnpj = request.json.get("cpf_or_cnpj")
        if len(cpf_or_cnpj) == 10:
            cpf_or_cnpj = "%" + cpf_or_cnpj

        elif len(cpf_or_cnpj) == 18:
            cpf_or_cnpj = cpf_or_cnpj + "%"
        else:
            cpf_or_cnpj = cpf_or_cnpj + "%"
        # Definir as datas fixas
        data_inicio = datetime(2000, 1, 1)
        data_final = datetime(2030, 12, 31)
        query = """
                SELECT
                   #
                """
        # Executar a consulta
        params = {'cpf_or_cnpj': cpf_or_cnpj + '%', 'data_inicio': data_inicio, 'data_final': data_final}
        results = execute_query(query, params)
        return jsonify(results)

    # Caso não seja um POST, renderizar a página de consulta
    return render_template("consulta.html")

@app.route("/certidao_td")
def certidao_td():
    return render_template("certidao_td.html")

@app.route("/buscas_td", methods=["GET", "POST"])
def buscas_td():
    if request.method == "POST":
        cpf_or_cnpj = request.json.get("cpf_or_cnpj")
        if len(cpf_or_cnpj) == 10:
            cpf_or_cnpj = "%" + cpf_or_cnpj

        elif len(cpf_or_cnpj) == 18:
            cpf_or_cnpj = cpf_or_cnpj + "%"
        else:
            cpf_or_cnpj = cpf_or_cnpj + "%"
        begin_date = request.json.get("begin_date")
        finish_date = request.json.get("finish_date")

        # No need to convert to datetime objects, use date strings directly
        data_inicio = begin_date
        data_final = finish_date

        query = """
                SELECT
                 #
          """
        params = (data_inicio, data_final, data_inicio, data_final, data_inicio, data_final, data_inicio, data_final, cpf_or_cnpj + '%')
        results = execute_query_orcamento(query, params)
        return jsonify(results)
    return render_template("buscas_td.html")

@app.route("/orcamento_td", methods=["GET", "POST"])
def orcamento_td():
    if request.method == "POST":
        cpf_or_cnpj = request.json.get("cpf_or_cnpj")
        if len(cpf_or_cnpj) == 10:
            cpf_or_cnpj = "%" + cpf_or_cnpj
        elif len(cpf_or_cnpj) == 18:
            cpf_or_cnpj = cpf_or_cnpj + "%"
        else:
            cpf_or_cnpj = cpf_or_cnpj + "%"
        begin_date = request.json.get("begin_date")
        finish_date = request.json.get("finish_date")

        data_inicio = begin_date
        data_final = finish_date

        query = """
                SELECT
                  #
          """
        params = (data_inicio, data_final, data_inicio, data_final,
                  data_inicio, data_final, data_inicio, data_final, cpf_or_cnpj + '%')
        results = execute_query_orcamento(query, params)

        registros_ativos = []
        registros_cancelados = []
        for registro in results:
            if registro['Situacao'] == 'Cancelado':
                registros_cancelados.append(registro)
            else:
                registros_ativos.append(registro)

        return jsonify({
            'ativos': registros_ativos,
            'cancelados': registros_cancelados
        })

    return render_template("orcamento_td.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port= 5500, debug=True)
