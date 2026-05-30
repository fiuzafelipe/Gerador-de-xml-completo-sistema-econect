import os
import logging

# Responsável pelos relatórios.

def salvar_relatorio_numeracao(destino, num_loj, relatorio_final):
    try:
        ext = f".{int(num_loj):03d}"
        caminho_relatorio = os.path.join(
            destino,
            f"Numeracao_Faltante{ext}"
        )

        with open(caminho_relatorio, "w", encoding="utf-8") as f:
            f.write(
                "\n".join(str(x) for x in relatorio_final or [])
            )

        return caminho_relatorio

    except Exception as e:
        # Agora sim, o logging captura o erro real de escrita em disco!
        logging.exception("Erro ao salvar relatório")
        raise e