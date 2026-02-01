#download_ans.py

import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"


def listar_links(url: str):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    return [a.get("href") for a in soup.find_all("a") if a.get("href")]


def listar_anos():
    hrefs = listar_links(BASE_URL)
    anos = []
    for h in hrefs:
        m = re.match(r"(\d{4})/?$", h)
        if m:
            anos.append(int(m.group(1)))
    anos.sort()
    return anos


def extrair_ano_tri_do_zip(nome_zip: str):
    """
    Cobre o padrão real do diretório da ANS:
    - 1T2025.zip, 2T2025.zip, 4T2024.zip, etc.
    """
    # padrão direto: 1T2025.zip
    m = re.search(r"([1-4])T(20\d{2})", nome_zip, re.IGNORECASE)
    if m:
        tri = int(m.group(1))
        ano = int(m.group(2))
        return ano, tri

    # fallback: pega ano e tenta achar trimestre em outras posições
    m_ano = re.search(r"(20\d{2})", nome_zip)
    ano = int(m_ano.group(1)) if m_ano else None

    tri = None
    m_tri = re.search(r"([1-4])T|T([1-4])", nome_zip, re.IGNORECASE)
    if m_tri:
        tri = int(m_tri.group(1) or m_tri.group(2))

    return ano, tri


def obter_ultimos_tres_trimestres():
    anos = listar_anos()
    print(f"Anos disponiveis: {anos[-5:]}")

    encontrados = {}  # (ano,tri) -> url_zip

    # vai do ano mais recente pro mais antigo até juntar >= 3 trimestres
    for ano in reversed(anos):
        url_ano = f"{BASE_URL}{ano}/"
        print(f"\nProcurando em {ano}/...")

        hrefs = listar_links(url_ano)
        zips_hrefs = [h for h in hrefs if h.lower().endswith(".zip")]
        print(f"  Total ZIPs em {ano}: {len(zips_hrefs)}")

        for zip_href in zips_hrefs:
            ano_zip, tri_zip = extrair_ano_tri_do_zip(zip_href)
            if ano_zip and tri_zip:
                url_zip = url_ano.rstrip("/") + "/" + zip_href
                encontrados[(ano_zip, tri_zip)] = url_zip
                print(f"    OK {zip_href} -> {ano_zip} T{tri_zip}")

        if len(encontrados) >= 3:
            break

    # ordena por mais recente e pega 3
    todos = [(a, t, url) for (a, t), url in encontrados.items()]
    todos.sort(key=lambda x: (-x[0], -x[1]))
    ultimos3 = todos[:3]

    print(f"\nTotal trimestres identificados: {len(todos)}")
    return ultimos3


def baixar_arquivo(url: str, destino: Path):
    destino.parent.mkdir(parents=True, exist_ok=True)
    print(f"  -> {url.split('/')[-1]}  para  {destino.name}")

    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()

    with open(destino, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

    print(f"  OK Baixado: {destino.name}")
    return destino


def baixar_zips_ultimos_tres_trimestres(raw_dir="data/raw"):
    raw_path = Path(raw_dir)
    raw_path.mkdir(parents=True, exist_ok=True)

    trimestres = obter_ultimos_tres_trimestres()

    print("\n" + "=" * 50)
    print("BAIXANDO OS 3 TRIMESTRES MAIS RECENTES")
    print("=" * 50)

    arquivos_baixados = []
    for ano, tri, zip_url in trimestres:
        nome = Path(zip_url).name
        destino = raw_path / f"{ano}_T{tri}_{nome}"
        baixar_arquivo(zip_url, destino)
        arquivos_baixados.append(destino)

    print("\nOK DOWNLOAD CONCLUIDO!")
    return arquivos_baixados


if __name__ == "__main__":
    baixar_zips_ultimos_tres_trimestres()
