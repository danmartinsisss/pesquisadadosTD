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
                    titulo.protocolo AS Protocolo,
                    titulo.pdata AS Data_Protocolo,
                    IF(titulo.registro <> '', titulo.registro, titulo.registropri) AS 'Registro/Averbacao',
                    IF(titulo.registro <> '', titulo.rdata, titulo.dataaverb) AS Data,
                    titulo.nomenat AS Natureza,
                    CONCAT(pessoa.Nome, ' CPF/CNPJ: ', pessoa.CpfCgc) AS Nome,
                    denominacaocontratante.den_descricao AS Qualificacao
                FROM
                    document.titulo
                    INNER JOIN document.contratante ON contratante.sequencia = titulo.sequencia
                    INNER JOIN document.pessoa ON pessoa.CodPes = contratante.CodPes
                    LEFT JOIN document.denominacaocontratante ON denominacaocontratante.den_id = contratante.Denominacao
                WHERE
                    denominacaocontratante.den_descricao NOT LIKE '%Procurador%' 
                    AND denominacaocontratante.den_descricao NOT LIKE '%Representante%' 
                    AND (
                        (titulo.rdata BETWEEN %(data_inicio)s AND %(data_final)s)
                        OR (
                            titulo.DataAverb BETWEEN %(data_inicio)s AND %(data_final)s
                            AND IF(titulo.dataaverb IS NOT NULL AND titulo.registropri <> '00000000', 1, 0) = 1
                        )
                    )
                    AND (pessoa.CpfCgc LIKE %(cpf_or_cnpj)s || '%%')
                GROUP BY 
                    titulo.sequencia
                ORDER BY 
                    IF(titulo.registro <> '', titulo.registro, titulo.registropri)
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
                    pessoa.Nome AS Nome,
                pessoa.CpfCgc AS CpfCnpj,
                    IF(titulo.registro <>'', titulo.registro, titulo.registropri) 'Registro/Averbacao',
                    titulo.nomenat Natureza,
                    CONCAT(
                        'PROTOCOLO: ', titulo.protocolo, ' em ', DATE_FORMAT(titulo.pdata, '%d/%m/%Y'), ' ',
                        IF(titulo.dataaverb IS NOT NULL,
                            CONCAT('- Averbação Av-', titulo.numaverb, '/', titulo.registropri, ' de ', DATE_FORMAT(titulo.dataaverb, '%d/%m/%Y'), '\nNATUREZA: ', titulo.Nomenat, '\nCONTRATANTE: '),
                            CONCAT('- Registro: ', titulo.registro, ' de ', DATE_FORMAT(titulo.rdata, '%d/%m/%Y'), '\nNATUREZA: ', titulo.NomeNat, ' ')),
                        GROUP_CONCAT(DISTINCT'\n',denominacaocontratante.den_descricao, ' CONTRATANTE: ', pessoa.Nome, ' CPF/CNPJ: ', pessoa.CpfCgc),
                        IF(bemtd.sequencia IS NULL, '\nBENS ALIENADOS: Não há', GROUP_CONCAT(DISTINCT '\nBENS ALIENADOS: ', bemmovel.bem_descricao, '\nDESCRIÇÃO: ', bemtd.observacao))
                    ) Texto
                FROM
                    document.titulo
                    INNER JOIN document.contratante ON contratante.sequencia = titulo.sequencia
                    INNER JOIN document.pessoa ON pessoa.CodPes = contratante.CodPes
                    INNER JOIN document.denominacaocontratante ON denominacaocontratante.den_id = contratante.Denominacao
                    LEFT JOIN document.bemtd ON bemtd.sequencia = titulo.Sequencia
                    LEFT JOIN document.bemmovel ON bemmovel.bem_id = bemtd.bem_movel
                WHERE
                    denominacaocontratante.den_descricao NOT LIKE '%Procurador%' 
                    AND denominacaocontratante.den_descricao NOT LIKE '%Representante%'
                    AND ((titulo.rdata BETWEEN %s AND %s) OR (titulo.DataAverb BETWEEN %s AND %s AND (IF(titulo.dataaverb IS NOT NULL AND titulo.registropri <> '00000000', 1, 0)) = 1))
                    AND titulo.sequencia IN (
                        SELECT
                            GROUP_CONCAT(titulo.sequencia)
                        FROM
                            document.titulo
                            INNER JOIN document.contratante ON contratante.sequencia = titulo.sequencia
                            INNER JOIN document.pessoa ON pessoa.CodPes = contratante.CodPes
                            INNER JOIN document.denominacaocontratante ON denominacaocontratante.den_id = contratante.Denominacao
                        WHERE
                            ((titulo.rdata BETWEEN %s AND %s) OR (titulo.DataAverb BETWEEN %s AND %s AND (IF(titulo.dataaverb IS NOT NULL AND titulo.registropri <> '00000000', 1, 0)) = 1))
                            AND pessoa.CpfCgc LIKE %s || '%%'
                        GROUP BY 
                            titulo.sequencia
                    )
                GROUP BY 
                   titulo.sequencia
                ORDER BY 
                    IF(titulo.registro <>'', titulo.registro, titulo.registropri)
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
                    pessoa.Nome AS Nome,
                    pessoa.CpfCgc AS CpfCnpj,
                    IF(titulo.registro <>'', titulo.registro, titulo.registropri) 'Registro/Averbacao',
                    titulo.nomenat Natureza,
                    CONCAT(
                        'PROTOCOLO: ', titulo.protocolo, ' em ', DATE_FORMAT(titulo.pdata, '%d/%m/%Y'), ' ',
                        IF(titulo.dataaverb IS NOT NULL,
                            CONCAT('- Averbação Av-', titulo.numaverb, '/', titulo.registropri, ' de ', DATE_FORMAT(titulo.dataaverb, '%d/%m/%Y'), '\nNATUREZA: ', titulo.Nomenat, '\nCONTRATANTE: '),
                            CONCAT('- Registro: ', titulo.registro, ' de ', DATE_FORMAT(titulo.rdata, '%d/%m/%Y'), '\nNATUREZA: ', titulo.NomeNat, ' - ')),
                        GROUP_CONCAT(denominacaocontratante.den_descricao, ' CONTRATANTE: ', pessoa.Nome, ' CPF/CNPJ: ', pessoa.CpfCgc),
                        IF(bemtd.sequencia IS NULL, '\nBENS ALIENADOS: Não há', GROUP_CONCAT(DISTINCT '\nBENS ALIENADOS: ', bemmovel.bem_descricao, '\nDESCRIÇÃO: ', bemtd.observacao))
                    ) Texto,
                    if(titulo.registro <>'' and exists(select a.sequencia from document.titulo a where a.sequenciapri = titulo.sequencia and a.nomenat like '%CANC%' and titulo.dataaverb is not null and titulo.numaverb>0 group by a.sequencia)<>'','Cancelado', if(titulo.dataaverb is not null and titulo.numaverb>0 and titulo.nomenat like '%CANC%','Cancelado','Ativo')) Situacao
                FROM
                    document.titulo
                    INNER JOIN document.contratante ON contratante.sequencia = titulo.sequencia
                    INNER JOIN document.pessoa ON pessoa.CodPes = contratante.CodPes
                    INNER JOIN document.denominacaocontratante ON denominacaocontratante.den_id = contratante.Denominacao
                    LEFT JOIN document.bemtd ON bemtd.sequencia = titulo.Sequencia
                    LEFT JOIN document.bemmovel ON bemmovel.bem_id = bemtd.bem_movel
                WHERE
                    denominacaocontratante.den_descricao NOT LIKE '%Procurador%' 
                    AND denominacaocontratante.den_descricao NOT LIKE '%Representante%'
                    AND ((titulo.rdata BETWEEN %s AND %s) OR (titulo.DataAverb BETWEEN %s AND %s AND (IF(titulo.dataaverb IS NOT NULL AND titulo.registropri <> '00000000', 1, 0)) = 1))
                    AND titulo.sequencia IN (
                        SELECT
                            GROUP_CONCAT(titulo.sequencia)
                        FROM
                            document.titulo
                            INNER JOIN document.contratante ON contratante.sequencia = titulo.sequencia
                            INNER JOIN document.pessoa ON pessoa.CodPes = contratante.CodPes
                            INNER JOIN document.denominacaocontratante ON denominacaocontratante.den_id = contratante.Denominacao
                        WHERE
                            ((titulo.rdata BETWEEN %s AND %s) OR (titulo.DataAverb BETWEEN %s AND %s AND (IF(titulo.dataaverb IS NOT NULL AND titulo.registropri <> '00000000', 1, 0)) = 1))
                            AND pessoa.CpfCgc LIKE %s || '%%'
                        GROUP BY 
                            titulo.sequencia
                    )
                GROUP BY 
                   titulo.sequencia
                ORDER BY 
                    IF(titulo.registro <>'', titulo.registro, titulo.registropri)
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
