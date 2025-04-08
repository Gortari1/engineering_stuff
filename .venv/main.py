import pandas as pd
import paramiko
import os
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega as variáveis do .env

# === CONFIGURAÇÕES ===
SFTP_HOST = os.getenv('SFTP_HOST')
SFTP_PORT = int(os.getenv('SFTP_PORT', 22))
SFTP_USER = os.getenv('SFTP_USER')
SFTP_PASSWORD = os.getenv('SFTP_PASSWORD')
REMOTE_PATH = '/import/ImportacaoDadosSFMC/'
LOCAL_SAVE_PATH = './arquivos_analisados/'

# === GERA A DATA DE HOJE ===
data_hoje = datetime.today().strftime('%Y%m%d')
nomes_arquivos = [
    f'account_u_{data_hoje}.csv',
    f'account_i_{data_hoje}.csv',
    f'contact_u_{data_hoje}.csv',
    f'contact_i_{data_hoje}.csv'
]

# === GARANTIR PASTA LOCAL ===
os.makedirs(LOCAL_SAVE_PATH, exist_ok=True)

# === CONEXÃO COM SFTP ===
transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
transport.connect(username=SFTP_USER, password=SFTP_PASSWORD)
sftp = paramiko.SFTPClient.from_transport(transport)

# === FUNÇÃO DE ANÁLISE ===
def analisar_csv(df):
    total = len(df)
    faltantes = df.isnull().sum()
    porcentagem = (faltantes / total * 100).round(2)
    relatorio = pd.DataFrame({'Valores Faltantes': faltantes, '% Faltantes': porcentagem})

    # Compor nome completo
    df['FullName'] = (df.get('FirstName', '') + ' ' + df.get('LastName', '')).fillna('').str.strip()
    nomes_invalidos = df['FullName'].str.upper().isin([
        'NOME NÂO DISPONÍVEL', 'NOMENÃODISPONÍVEL', 'NOMENÃODISPONIVEL', 'NOMENÃODISPONÍVEL'
    ]).sum()

    birth_ausentes = df['Birthdate'].isnull().sum() if 'Birthdate' in df.columns else 0
    return relatorio, total, nomes_invalidos, birth_ausentes

# === PROCESSAR CADA ARQUIVO ESPERADO ===
for arquivo in nomes_arquivos:
    try:
        remote_file = REMOTE_PATH + arquivo
        local_file = os.path.join(LOCAL_SAVE_PATH, arquivo)

        # Baixar do servidor
        sftp.get(remote_file, local_file)
        print(f"✅ Arquivo baixado: {arquivo}")

        # Analisar
        df = pd.read_csv(local_file)
        relatorio, total, nomes_inv, birth_missing = analisar_csv(df)

        print(f"📊 Análise de {arquivo}")
        print(f" - Total de registros: {total}")
        print(f" - Nomes inválidos: {nomes_inv}")
        print(f" - Datas de nascimento ausentes: {birth_missing}")

        # Salvar relatório
        nome_saida = arquivo.replace('.csv', '_analisado.csv')
        caminho_saida = os.path.join(LOCAL_SAVE_PATH, nome_saida)
        relatorio.to_csv(caminho_saida, encoding='utf-8')
        print(f"📝 Relatório salvo em: {caminho_saida}\n")

    except FileNotFoundError:
        print(f"⚠️ Arquivo não encontrado no servidor: {arquivo}")
    except Exception as e:
        print(f"❌ Erro ao processar {arquivo}: {e}")

# === FECHAR CONEXÃO ===
sftp.close()
transport.close()
