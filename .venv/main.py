import pandas as pd
import paramiko
import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
import time

load_dotenv()  # Carrega as variáveis do .env

# >>> CONFIGURAÇÕES <<<
SFTP_HOST = os.getenv('SFTP_HOST')
SFTP_PORT = int(os.getenv('SFTP_PORT', 22))
SFTP_USER = os.getenv('SFTP_USER')
SFTP_PASSWORD = os.getenv('SFTP_PASSWORD')
REMOTE_BASE_PATH = 'source'
LOCAL_SAVE_PATH = 'sink'

st.title("DATA CHECKER")  # Interface title

# Barra de carregamento
progress_bar = st.progress(0)

# >>> SOLICITA DATA DO USUÁRIO <<<
data_usuario = st.text_input("Informe a data no formato YYYYMMDD:")
if st.button('Run Data Check') and data_usuario:
    REMOTE_PATH = f"{REMOTE_BASE_PATH}{data_usuario}/"
    nomes_arquivos = [
        f'account_u_{data_usuario}.zip',
        f'account_i_{data_usuario}.zip',
        f'contact_u_{data_usuario}.zip',
        f'contact_i_{data_usuario}.zip',
        f'consent_u_{data_usuario}.zip',
        f'consent_i_{data_usuario}.zip',
        f'result_success_{data_usuario}_1200.csv',
        f'result_error_{data_usuario}_1200.csv',
    ]

    os.makedirs(LOCAL_SAVE_PATH, exist_ok=True)

    progress_step = 100 / len(nomes_arquivos)
    current_progress = 0

    try:
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)
# regras de analise dos docs
        def analisar_csv(df):
            total = len(df)
            erros = 0
            detalhe_erros = []

            for index, row in df.iterrows():
                if pd.isnull(row).any():
                    erros += 1
                    detalhe_erros.append(f"Erro na linha {index}")

            return total, erros, (erros / total) * 100, detalhe_erros

        relatorio_geral = []

        for arquivo in nomes_arquivos:
            try:
                remote_file = REMOTE_PATH + arquivo
                local_file = os.path.join(LOCAL_SAVE_PATH, arquivo)

                inicio = time.time()
                sftp.get(remote_file, local_file)
                st.text(f"🆗 Arquivo baixado: {arquivo}")

                df = pd.read_csv(local_file)
                total, total_erros, pct_erros, detalhes = analisar_csv(df)
                fim = time.time()
                duracao = time.strftime("%M:%S", time.gmtime(fim - inicio))

                relatorio_geral.append({
                    "arquivo": arquivo,
                    "total": total,
                    "erros": total_erros,
                    "pct_erros": pct_erros,
                    "detalhes": detalhes
                })

                current_progress += progress_step
                progress_bar.progress(int(current_progress))

            except FileNotFoundError:
                st.error(f"⚠️ Arquivo não encontrado no servidor: {arquivo}")
            except Exception as e:
                st.error(f"💀 Erro ao processar {arquivo}: {e}")

        if relatorio_geral:
            df_geral = pd.DataFrame(relatorio_geral)
            caminho_geral = os.path.join(LOCAL_SAVE_PATH, f'relatorio_geral_{data_usuario}.csv')
            df_geral.to_csv(caminho_geral, index=False, encoding='utf-8')
            st.success(f"📋 Relatório consolidado salvo em: {caminho_geral}")

    finally:
        sftp.close()
        transport.close()