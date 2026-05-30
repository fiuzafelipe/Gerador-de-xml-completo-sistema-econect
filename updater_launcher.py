import requests

from updater import baixar_atualizacao
from updater import URL_VERSION


response = requests.get(
    URL_VERSION,
    timeout=10
)

dados = response.json()

download_url = dados.get(
    "download_url"
)

baixar_atualizacao(
    download_url
)