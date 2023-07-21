import time
import psycopg2
import openpyxl
import pandas as pd
import os
import warnings
import telebot
import requests
from tqdm import tqdm
from ini import banco
from datetime import datetime
from psycopg2 import Error

### Local variables
sql_exec = 'online'
pathsql = 'sql/'
pathname = 'result/'
filename = pathname + 'monitor.xlsx'

#ignora warning
warnings.filterwarnings("ignore")

#funcao carrega arquivos
def files_path(path):
    '''usando a função walk pra retornar path e filename (path, file)'''
    return [(file) for p, _, files in os.walk(os.path.abspath(path)) for file in files]

#Funcao para validar o resultado
def execution(pathsql):

    try:
        conecta = banco.connection()
    except SystemExit:
        print (Error.pgerror)

    ''' le o arquivo .sql e executa '''

    try:
        file = open(pathsql)
        sql = file.read()
        file.close()

        sql_query = pd.read_sql_query (sql, conecta)

    except SystemExit:
        print (Error.pgerror)

    return (sql_query)

#funcao envia mensagen telegram
def bot_send_msg(df):

    chat_id, chave_api = banco.bot_conection()

    #Create the message
    body ='🚨  Atenção aos Alertas 🚨 '
    if df.empty == False:
        for i in range(len(df)):
            body=body + '\n \n Empresa: ' + str((df['name'].iloc[i])) \
                                +'\n Tempo Inatividade: ' + str((df['gap_time'].iloc[i]))  \
                                +'\n Data: ' + str((df['date_time'].iloc[i]))

 #bot.send_message(-1001867822012, body)
    url = f"https://api.telegram.org/bot{chave_api}/sendMessage?chat_id={chat_id}&text={body}"
    print(requests.get(url).json()) # this sends the message
   # print(body)

#funcao envia mensagen Normalizacao telegram
def bot_send_msg_norm(df):

    chat_id, chave_api = banco.bot_conection()

    #Create the message
    body ='✅  Alerta Normalizado ✅ '
    for i in range(len(df)):
        body=body + '\n \n Empresa: ' + str((df['name'].iloc[i])) \
                            +'\n Tempo Inatividade: ' + str((df['gap_time'].iloc[i]))  \
                            +'\n Data: ' + str((df['date_time'].iloc[i]))

 #bot.send_message(-1001867822012, body)
    url = f"https://api.telegram.org/bot{chave_api}/sendMessage?chat_id={chat_id}&text={body}"
    print(requests.get(url).json()) # this sends the message
    #    print(body)

#Main Inicio do programa
if __name__ == '__main__':

    print('starting process')

    r = files_path(pathsql)

    df_final = pd.DataFrame(columns = ['name','valida_gap_time','turno','created_at','gap_time','date_time'])

    for files in r:

        '''filtra os arquivos que serão executados '''
        if (files.find(sql_exec)) > -1:
            print('executing query ',files)

            ''' Executa Funcao principal e gera aquivo xlsx '''
            ret = execution(pathsql+files)
            df_result = pd.DataFrame(ret)
            df_final = df_final.append(df_result)

            ''' Coleta Nome da Empresa para criar arquivo de parametro'''
            empresa = (str((df_result['name'].iloc[0]))) + '.txt'
            valida = files_path(pathname)

            ''' Valida Resultado para enviar msg Telegram '''
            df_bot = df_result[df_result["valida_gap_time"].isin([0])]

            if df_bot.empty == False:
                bot_send_msg(df_bot)
                f = open(pathname + empresa,"w+")
                f.close()
                print('send message')

            if df_bot.empty == True and empresa in valida :
                bot_send_msg_norm(df_result)
                os.remove(pathname + empresa)

    wb = openpyxl.Workbook()
    Sheet_name = wb.sheetnames
    df_final.to_excel(filename, index=False)

print('finished process')
