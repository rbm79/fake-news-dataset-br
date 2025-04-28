import pandas as pd
import os
from datetime import datetime
import argparse

# Importar as classes dos outros scripts
# Nota: Esses scripts devem estar no mesmo diretório
from fato_ou_fake_scraper import FatoOuFakeScraper
from fato_ou_fake_api import FatoOuFakeAPIExtractor

class ExtratorCombinado:
    """
    Classe para combinar diferentes métodos de extração de notícias Fato ou Fake
    do G1 e criar um dataset unificado.
    """
    
    def __init__(self, num_paginas=5, metodo='todos'):
        """
        Inicializa o extrator combinado.
        
        Parâmetros:
        num_paginas (int): Número de páginas para extrair no método de scraping
        metodo (str): Método de extração a ser usado ('scraping', 'api' ou 'todos')
        """
        self.num_paginas = num_paginas
        self.metodo = metodo.lower()
        self.scraper = None
        self.api_extractor = None
        
        # Validar o método
        if self.metodo not in ['scraping', 'api', 'todos']:
            raise ValueError("Método inválido. Use 'scraping', 'api' ou 'todos'.")
        
        # Inicializar os extratores conforme o método escolhido
        if self.metodo in ['scraping', 'todos']:
            self.scraper = FatoOuFakeScraper(num_pages=num_paginas)
        
        if self.metodo in ['api', 'todos']:
            self.api_extractor = FatoOuFakeAPIExtractor()
    
    def executar_extracao(self):
        """
        Executa a extração de dados usando o(s) método(s) selecionado(s).
        
        Retorna:
        DataFrame: DataFrame pandas com todas as notícias extraídas
        """
        dfs = []
        
        # Extrair via scraping se aplicável
        if self.scraper:
            print("\n===== EXTRAÇÃO VIA SCRAPING DIRETO =====")
            df_scraping = self.scraper.executar_extracao()
            
            if not df_scraping.empty:
                # Adicionar coluna para identificar a fonte dos dados
                df_scraping['metodo_extracao'] = 'scraping'
                dfs.append(df_scraping)
                
                print(f"Extraídas {len(df_scraping)} notícias via scraping direto.")
            else:
                print("Nenhuma notícia extraída via scraping.")
        
        # Extrair via API/RSS se aplicável
        if self.api_extractor:
            print("\n===== EXTRAÇÃO VIA API/RSS =====")
            df_api = self.api_extractor.executar_extracao()
            
            if not df_api.empty:
                # Adicionar coluna para identificar a fonte dos dados
                df_api['metodo_extracao'] = 'api/rss'
                dfs.append(df_api)
                
                print(f"Extraídas {len(df_api)} notícias via API/RSS.")
            else:
                print("Nenhuma notícia extraída via API/RSS.")
        
        # Combinar os DataFrames, se houver mais de um
        if len(dfs) > 1:
            # Verificar para garantir que as colunas sejam compatíveis
            colunas_comuns = set(dfs[0].columns).intersection(set(dfs[1].columns))
            
            # Se houver colunas incompatíveis, usar apenas as comuns
            if len(colunas_comuns) < len(dfs[0].columns) or len(colunas_comuns) < len(dfs[1].columns):
                print(f"Aviso: Alguns campos são incompatíveis entre os métodos. Usando apenas {len(colunas_comuns)} colunas comuns.")
                dfs = [df[list(colunas_comuns)] for df in dfs]
            
            # Concatenar os DataFrames
            df_combinado = pd.concat(dfs, ignore_index=True)
            
            # Remover duplicatas com base no link (URL)
            df_combinado_sem_duplicatas = df_combinado.drop_duplicates(subset=['link'])
            
            # Verificar quantas duplicatas foram removidas
            num_duplicatas = len(df_combinado) - len(df_combinado_sem_duplicatas)
            if num_duplicatas > 0:
                print(f"Removidas {num_duplicatas} notícias duplicadas.")
            
            return df_combinado_sem_duplicatas
        
        # Se houver apenas um DataFrame, retorná-lo
        elif len(dfs) == 1:
            return dfs[0]
        
        # Se não houver nenhum DataFrame, retornar um vazio
        else:
            print("Nenhum dado extraído por qualquer método.")
            return pd.DataFrame()
    
    def salvar_dataset(self, df, formato='csv'):
        """
        Salva o dataset combinado no formato especificado.
        
        Parâmetros:
        df (DataFrame): DataFrame com os dados
        formato (str): Formato de saída ('csv' ou 'json')
        
        Retorna:
        str: Caminho do arquivo salvo
        """
        if df.empty:
            print("Dataset vazio. Nada para salvar.")
            return None
        
        # Criar pasta 'datasets' se não existir
        if not os.path.exists('datasets'):
            os.makedirs('datasets')
        
        # Gerar nome do arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if formato.lower() == 'csv':
            filepath = f'datasets/fato_ou_fake_combinado_{timestamp}.csv'
            df.to_csv(filepath, index=False, encoding='utf-8')
        elif formato.lower() == 'json':
            filepath = f'datasets/fato_ou_fake_combinado_{timestamp}.json'
            df.to_json(filepath, orient='records', force_ascii=False, indent=4)
        else:
            raise ValueError(f"Formato '{formato}' não suportado. Use 'csv' ou 'json'.")
        
        print(f"Dataset combinado salvo com sucesso em {filepath}")
        return filepath


def main():
    """
    Função principal para executar o extrator a partir da linha de comando.
    """
    # Configurar o parser de argumentos
    parser = argparse.ArgumentParser(description='Extrator de notícias Fato ou Fake do G1')
    
    parser.add_argument('--metodo', type=str, default='todos',
                        choices=['scraping', 'api', 'todos'],
                        help='Método de extração (scraping, api ou todos)')
    
    parser.add_argument('--paginas', type=int, default=5,
                        help='Número de páginas para extrair no modo scraping')
    
    parser.add_argument('--formato', type=str, default='csv',
                        choices=['csv', 'json', 'ambos'],
                        help='Formato de saída (csv, json ou ambos)')
    
    args = parser.parse_args()
    
    # Inicializar o extrator combinado
    extrator = ExtratorCombinado(num_paginas=args.paginas, metodo=args.metodo)
    
    # Executar extração
    print(f"\nIniciando extração usando método(s): {args.metodo}")
    df_noticias = extrator.executar_extracao()
    
    if not df_noticias.empty:
        # Exibir estatísticas básicas
        total_noticias = len(df_noticias)
        total_fake = len(df_noticias[df_noticias['classificacao'] == 'FAKE'])
        total_fato = len(df_noticias[df_noticias['classificacao'] == 'FATO'])
        total_indeterminado = len(df_noticias[df_noticias['classificacao'] == 'INDETERMINADO'])
        
        print(f"\nEstatísticas do Dataset Combinado:")
        print(f"Total de notícias: {total_noticias}")
        print(f"Classificadas como FAKE: {total_fake} ({total_fake/total_noticias*100:.1f}%)")
        print(f"Classificadas como FATO: {total_fato} ({total_fato/total_noticias*100:.1f}%)")
        print(f"Classificação indeterminada: {total_indeterminado} ({total_indeterminado/total_noticias*100:.1f}%)")
        
        # Distribuição por método de extração (se ambos os métodos foram usados)
        if args.metodo == 'todos':
            por_metodo = df_noticias['metodo_extracao'].value_counts()
            print("\nDistribuição por método de extração:")
            for metodo, count in por_metodo.items():
                print(f"- {metodo}: {count} notícias ({count/total_noticias*100:.1f}%)")
        
        # Salvar dataset conforme formato especificado
        if args.formato in ['csv', 'ambos']:
            extrator.salvar_dataset(df_noticias, formato='csv')
        
        if args.formato in ['json', 'ambos']:
            extrator.salvar_dataset(df_noticias, formato='json')
    
    print("\nProcesso de extração concluído!")


if __name__ == "__main__":
    main()
