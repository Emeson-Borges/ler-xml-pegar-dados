import os
import xml.etree.ElementTree as ET

# Caminho para a pasta contendo os XMLs
pasta_xmls = 'C:/Users/itarg/Desktop/2200'  # Substitua pelo caminho da sua pasta

# Diretório para salvar o arquivo de saída único
diretorio_saida = 'D:/ProjetosPycharme/Script-pega-dados-id,recibo,protocolo,matricula/dados.sql'  # Substitua pelo caminho desejado

# Função para extrair dados específicos de um arquivo XML
def extrair_dados_arquivo_xml(xml_file):
    try:
        # Parse o XML
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Define os namespaces
        namespaces = {
            'eSocial': 'http://www.esocial.gov.br/schema/download/retornoProcessamento/v1_0_0',
            'evt': 'http://www.esocial.gov.br/schema/evt/evtAdmissao/v_S_01_00_00',
            'ret': 'http://www.esocial.gov.br/schema/evt/retornoEvento/v1_2_1'
        }

        # Encontre os elementos desejados usando expressões de caminho com namespaces
        ide_evento = root.find('.//evt:evtAdmissao/evt:ideEvento', namespaces).attrib.get('Id', 'N/A')
        matricula = root.find('.//evt:evtAdmissao/evt:vinculo/evt:matricula', namespaces).text

        # Tente obter o valor do Id do elemento <retornoEvento>
        retorno_evento_id = root.find('.//ret:retornoEvento', namespaces).attrib.get('Id', 'N/A')

        protocolo_envio_lote = root.find('.//ret:protocoloEnvioLote', namespaces).text
        nr_recibo = root.find('.//ret:nrRecibo', namespaces).text

        return ide_evento, matricula, retorno_evento_id, protocolo_envio_lote, nr_recibo
    except Exception as e:
        print(f"Erro ao analisar o arquivo {xml_file}: {str(e)}")
        return None, None, None, None, None

# Dicionário para armazenar os dados correspondentes
mapeamento_dados = {}

# Abre o arquivo de saída fora do loop
with open(diretorio_saida, 'w') as arquivo_saida:
    # Loop através de todos os arquivos XML na pasta
    arquivos_xml = [os.path.join(pasta_xmls, arquivo) for arquivo in os.listdir(pasta_xmls) if arquivo.endswith('.xml')]
    for arquivo_xml in arquivos_xml:
        print(f"Lendo arquivo: {arquivo_xml}")
        ide_evento, matricula, retorno_evento_id, protocolo_envio_lote, nr_recibo = extrair_dados_arquivo_xml(arquivo_xml)
        if ide_evento is not None:
            # Armazenar os dados correspondentes no dicionário
            mapeamento_dados[ide_evento] = {'matricula': matricula, 'retornoEventoId': retorno_evento_id, 'protocoloEnvioLote': protocolo_envio_lote, 'nrRecibo': nr_recibo}

            # Escreve os dados no arquivo de saída
            arquivo_saida.write(f"UPDATE esocial.historico SET IDEVENTO='{retorno_evento_id}', nr_recibo='{nr_recibo}', protocolo='{protocolo_envio_lote}', status='P', message='201 - Lote processado com sucesso. Sucesso' where status='E' and evento='S2200' and idevento in (select idevento from esocial.s2200 where matricula='{matricula}');\n")
            
            
            #arquivo_saida_normal.write(f"Matricula: {matricula}, IDEVENTO: {retorno_evento_id}, ProtocoloEnvioLote: {protocolo_envio_lote}, NrRecibo: {nr_recibo}\n")

if not mapeamento_dados:
    print("Nenhum dado encontrado nos arquivos XML.")
else:
    print("Mapeamentos de dados foram salvos no arquivo de saída único.")
