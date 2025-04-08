# 📊 Analisador de Qualidade de Dados via SFTP

Este projeto é um script Python que se conecta a um servidor SFTP, baixa arquivos `.csv` do dia atual e realiza uma análise automatizada de qualidade dos dados, gerando relatórios salvos localmente em formato `.csv` com codificação UTF-8.

---

## 🚀 Funcionalidades

- Conexão segura via SFTP
- Busca automática de arquivos com base na data do dia (formato `YYYYMMDD`)
- Download dos arquivos:
  - `account_u_YYYYMMDD.csv`
  - `account_i_YYYYMMDD.csv`
  - `contact_u_YYYYMMDD.csv`
  - `contact_i_YYYYMMDD.csv`
- Análise de:
  - Total de registros
  - Dados ausentes por coluna
  - Detecção de nomes inválidos (como “NomeNãoDisponível”)
  - Datas de nascimento ausentes
- Geração de relatório por arquivo com sufixo `_analisado.csv`

---
## 🧰 Requisitos

Python 3.7+
Bibliotecas:

pip install pandas paramiko python-dotenv

---

## 🧠 Como usar

Clone o repositório:
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
Crie e configure o .env
Execute o script:
python analisador.py
Os arquivos analisados estarão na pasta arquivos_analisados/

---

## 📌 Observações

Os arquivos buscados devem estar no diretório remoto /import/ImportacaoDadosSFMC
O script utiliza a data do sistema para compor os nomes dos arquivos a serem buscados
Se um dos arquivos não for encontrado, o script continuará com os demais

---

##🛡️ Segurança

Este projeto utiliza variáveis de ambiente para proteger credenciais de acesso ao servidor. Nunca compartilhe ou suba seu .env ao GitHub.