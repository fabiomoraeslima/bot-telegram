import time
import psycopg2
import openpyxl
import pandas as pd
import os
import warnings
from tqdm import tqdm
from ini import banco
from datetime import datetime
from psycopg2 import Error


### Local variables
sql_exec = 'hist_'
pathsql = 'sql/'
pathname = 'result/'
filename = pathname + 'hist_transactions.xlsx'

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

#Main Inicio do programa
if __name__ == '__main__':

    print('starting process')
    r = files_path(pathsql)

    df_final = pd.DataFrame(columns = ['purchase_channel', 'name', 'date', 'hora', 'turno', 'gap_time', 'gap_time_decimal'])

    for files in r:

        '''filtra os arquivos que serão executados '''
        if (files.find(sql_exec)) > -1:

            print('executing query ',files)

            ''' Executa Funcao principal e gera aquivo xlsx '''
            result = execution(pathsql+files)
            df = pd.DataFrame(result)
            df_final = df_final.append(df)

    #df_result = pd.DataFrame(append_data)
    wb = openpyxl.Workbook()
    df_final.to_excel(filename, index=False)


    print('finished process')
    