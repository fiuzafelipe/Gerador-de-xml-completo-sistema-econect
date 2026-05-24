import re

# Tudo o que for utilitário de xml

def montar_xml_processado(env, ret):

    if "<nfeProc" in env or "<procInut" in env:
        return env

    elif "<NFe" in env and "<infProt" in ret:

        m = re.search(
            r'(<protNFe.*?</protNFe>)',
            ret,
            re.DOTALL
        )

        p_xml = m.group(1) if m else ""

        n_corpo = env.replace(
            '<?xml version="1.0" encoding="UTF-8"?>',
            ''
        ).strip()

        return (
            f'<?xml version="1.0" encoding="UTF-8"?>'
            f'<nfeProc versao="4.00" '
            f'xmlns="http://www.portalfiscal.inf.br/nfe">'
            f'{n_corpo}{p_xml}</nfeProc>'
        )

    return ret if len(ret) > len(env) else env