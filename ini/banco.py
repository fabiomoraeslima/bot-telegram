ubuntu@ip-10-155-14-172:/src/packaging/enel/ini$ cat banco.py
import time
import psycopg2
import requests
import telebot

def connection():
    connection = psycopg2.connect(user='fabio.monitoramento',
                                    password='M0nitF4b10',
                                    host='10.155.11.238',
                                    port='55432',
                                    database='producao_utilities_v2')
    return connection

def bot_conection():

    chat_id = "-1001867822012"
    chave_api = '5867712391:AAEtcqXK4Cqu0JXI2Uz37DzZHYGfqxPBhBk'

    return chat_id, chave_api
