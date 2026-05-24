import os

# Responsável pelos relatórios.

def salvar_relatorio_numeração(
    destino,
    num_loj,
    relatorio_final
):

    ext = f".{int(num_loj):03d}"

    caminho_relatorio = os.path.join(
        destino,
        f"Numeracao_Faltante{ext}"
    )

    with open(
        caminho_relatorio,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(relatorio_final)
        )

    return caminho_relatorio