import requests
import pandas as pd
import json
from datetime import datetime
import os
import feedparser
import re
from bs4 import BeautifulSoup
import time
import random

class FatoOuFakeAPIExtractor:
    """
    Classe para extrair notícias da seção Fato ou Fake do G1
    utilizando API ou feed RSS, quando disponíveis.
    """
    
    def __init__(self):
        """
        Inicializa o extrator.
        """
        self.base_url = "https://g1.globo.com/fato-ou-fake/"
        self.rss_url = "https://g1.globo.com/rss/g1/fato-ou-fake/"  # URL potencial do feed RSS
        self.api_url = "https://api.globo.com/fato-ou-fake"  # URL potencial da API
        self.dataset = []
        
    def tentar_api(self):
        """
        Tenta extrair dados através da API do G1 (se disponível).
        
        Retorna:
        list: Lista de notícias extraídas ou lista vazia se falhar
        """
        print("Tentando acessar dados via API...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json'
        }
        
        try:
            # Esta é uma URL hipotética - precisaria ser ajustada conforme documentação real da API
            response = requests.get(self.api_url, headers=headers)
            
            if response.status_code == 200:
                # Tentar extrair os dados JSON
                data = response.json()
                
                # Processar os dados conforme a estrutura da API
                # Essa estrutura dependeria da documentação real da API
                noticias = []
                
                # Exemplo hipotético de como seria o processamento
                if 'items' in data:
                    for item in data['items']:
                        noticia = {
                            'titulo': item.get('title', ''),
                            'link': item.get('url', ''),
                            'data_publicacao': item.get('published', ''),
                            'resumo': item.get('summary', ''),
                            'classificacao': self._classificar_checagem_api(item),
                            'imagem_url': item.get('image', {}).get('url', ''),
                            'conteudo': item.get('content', ''),
                            'tags': item.get('tags', []),
                            'autor': item.get('author', ''),
                            'data_extracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'fonte': 'API'
                        }
                        noticias.append(noticia)
                
                print(f"Extraídas {len(noticias)} notícias via API.")
                return noticias
                
            else:
                print(f"Falha ao acessar API. Status code: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Erro ao tentar acessar API: {e}")
            return []
    
    def tentar_rss(self):
        """
        Tenta extrair dados através do feed RSS do G1 (se disponível).
        
        Retorna:
        list: Lista de notícias extraídas ou lista vazia se falhar
        """
        print("Tentando acessar dados via RSS...")
        
        try:
            # Usar feedparser para processar o feed RSS
            feed = feedparser.parse(self.rss_url)
            
            # Verificar se o feed foi processado com sucesso
            if feed.status == 200 and feed.entries:
                print("Connectado ao feed RSS iniciando processamento...")
                noticias = []
                
                for entry in feed.entries:
                    # Determinar se é uma checagem Fato ou Fake
                    if not self._eh_checagem_fato_ou_fake(entry.title, entry.link):
                        continue
                    
                    # Extrair conteúdo completo da notícia
                    conteudo = self._extrair_conteudo_da_noticia(entry.link)
                    
                    # Classificar como FATO ou FAKE
                    classificacao = self._classificar_checagem(entry.title, entry.summary if hasattr(entry, 'summary') else '')
                    
                    noticia = {
                        'titulo': entry.title,
                        'link': entry.link,
                        'data_publicacao': entry.published if hasattr(entry, 'published') else '',
                        'resumo': entry.summary if hasattr(entry, 'summary') else '',
                        'classificacao': classificacao,
                        'imagem_url': self._extrair_imagem_do_feed(entry),
                        'conteudo': conteudo,
                        'tags': [tag.term for tag in entry.tags] if hasattr(entry, 'tags') else [],
                        'autor': entry.author if hasattr(entry, 'author') else '',
                        'data_extracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'fonte': 'RSS'
                    }
                    
                    noticias.append(noticia)
                
                print(f"Extraídas {len(noticias)} notícias via RSS.")
                return noticias
                
            else:
                print(f"Feed RSS não disponível ou vazio.")
                return []
                
        except Exception as e:
            print(f"Erro ao tentar acessar feed RSS: {e}")
            return []
    
    def _extrair_imagem_do_feed(self, entry):
        """
        Extrai a URL da imagem de uma entrada do feed RSS.
        
        Parâmetros:
        entry: Entrada do feed RSS
        
        Retorna:
        str: URL da imagem ou string vazia
        """
        # Tentar diferentes locais onde a imagem pode estar no feed
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if 'url' in media:
                    return media['url']
        
        if hasattr(entry, 'links'):
            for link in entry.links:
                if link.get('type', '').startswith('image/'):
                    return link.get('href', '')
        
        if hasattr(entry, 'content') and entry.content:
            for content in entry.content:
                if 'value' in content:
                    # Procurar URLs de imagem no conteúdo HTML
                    soup = BeautifulSoup(content['value'], 'html.parser')
                    img = soup.find('img')
                    if img and 'src' in img.attrs:
                        return img['src']
        
        return ''
    
    def _eh_checagem_fato_ou_fake(self, titulo, link):
        """
        Verifica se a notícia é uma checagem Fato ou Fake.
        
        Parâmetros:
        titulo (str): Título da notícia
        link (str): Link da notícia
        
        Retorna:
        bool: True se for uma checagem, False caso contrário
        """
        # Verificar pelo link se contém 'fato-ou-fake'
        if 'fato-ou-fake' in link.lower():
            return True
        
        # Verificar por palavras-chave no título
        keywords = ['fato', 'fake', 'falso', 'verdade', 'é falso que', 'é verdade que', 'checamos']
        for keyword in keywords:
            if keyword.lower() in titulo.lower():
                return True
        
        return False
    
    def _classificar_checagem(self, titulo, resumo):
        """
        Determina se o conteúdo foi classificado como FATO ou FAKE.
        
        Parâmetros:
        titulo (str): Título da notícia
        resumo (str): Resumo da notícia (não utilizado na classificação)
        
        Retorna:
        str: 'FATO', 'FAKE' ou 'INDETERMINADO'
        """
        # Considerar apenas o título para a classificação
        texto_titulo = titulo.lower()
        
        # Padrões comuns usados pelo G1 para indicar FAKE no título
        padroes_fake = [
            'é fake',
            'é falso', 
            'não é verdade', 
            'não é verdadeiro',
            'falso que', 
            'fake news',
            'boato', 
            'mentira', 
            'enganoso', 
            'não é real', 
            'não aconteceu',
            'não procede',
            'não existe',
            'não é fato'
        ]
        
        # Padrões comuns usados pelo G1 para indicar FATO no título
        padroes_fato = [
            'é fato', 
            'é verdade', 
            'verdadeiro', 
            'aconteceu', 
            'é real',
            'confirmado', 
            'verificado', 
            'comprovado',
            'procede',
            'é verdadeiro'
        ]
        
        # Verificar se é FAKE
        for padrao in padroes_fake:
            if padrao in texto_titulo:
                return 'FAKE'
        
        # Verificar se é FATO
        for padrao in padroes_fato:
            if padrao in texto_titulo:
                return 'FATO'
        
        # Verificar se é FAKE com base em apenas "fake" isolado
        if re.search(r'\bfake\b', texto_titulo, re.IGNORECASE):
            return 'FAKE'
            
        # Verificar se é FATO com base em apenas "fato" isolado
        if re.search(r'\bfato\b', texto_titulo, re.IGNORECASE):
            return 'FATO'
        
        # Se não foi possível determinar com certeza
        return 'INDETERMINADO'
    
    def _classificar_checagem_api(self, item):
        """
        Determina se o conteúdo foi classificado como FATO ou FAKE com base nos dados da API.
        
        Parâmetros:
        item (dict): Item da API
        
        Retorna:
        str: 'FATO', 'FAKE' ou 'INDETERMINADO'
        """
        # Verificar se a API já fornece a classificação diretamente
        if 'classification' in item:
            classification = item['classification'].upper()
            if classification in ['FATO', 'FAKE']:
                return classification
        
        # Se não, tentar classificar baseado no título e resumo
        titulo = item.get('title', '')
        resumo = item.get('summary', '')
        
        return self._classificar_checagem(titulo, resumo)
    
    def _extrair_conteudo_da_noticia(self, url):
        """
        Extrai o conteúdo completo de uma notícia a partir da URL.
        
        Parâmetros:
        url (str): URL da notícia
        
        Retorna:
        str: Conteúdo da notícia
        """
        try:
            # Adicionar um delay para evitar sobrecarga de requisições
            time.sleep(random.uniform(1, 3))
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrair o conteúdo principal da notícia
            # Ajuste os seletores conforme necessário para corresponder à estrutura da página
            conteudo_elements = soup.select('.content-text__container p')
            
            if conteudo_elements:
                return ' '.join([p.get_text().strip() for p in conteudo_elements])
            else:
                # Tentar outros seletores comuns
                conteudo_elements = soup.select('article p')
                if conteudo_elements:
                    return ' '.join([p.get_text().strip() for p in conteudo_elements])
            
            return ""
            
        except Exception as e:
            print(f"Erro ao extrair conteúdo da notícia {url}: {e}")
            return ""
    
    def executar_extracao(self):
        """
        Executa o processo completo de extração, tentando diferentes métodos.
        
        Retorna:
        DataFrame: DataFrame pandas com todas as notícias extraídas
        """
        print(f"Iniciando extração de notícias Fato ou Fake do G1 via API/RSS...")
        
        # Tentar primeiro via API
        noticias = self.tentar_api()
        
        # Se a API falhar, tentar via RSS
        if not noticias:
            noticias = self.tentar_rss()
        
        # Se ambos falharem, avisar e retornar DataFrame vazio
        if not noticias:
            print("Não foi possível extrair dados via API ou RSS. Considere usar o método de scraping direto.")
            return pd.DataFrame()
        
        # Atribuir ao dataset
        self.dataset = noticias
        
        # Converter para DataFrame
        df = pd.DataFrame(noticias)
        
        print(f"Total de {len(df)} notícias extraídas com sucesso.")
        return df
    
    def salvar_dataset(self, df, formato='csv'):
        """
        Salva o dataset no formato especificado.
        
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
            filepath = f'datasets/fato_ou_fake_api_{timestamp}.csv'
            df.to_csv(filepath, index=False, encoding='utf-8')
        elif formato.lower() == 'json':
            filepath = f'datasets/fato_ou_fake_api_{timestamp}.json'
            df.to_json(filepath, orient='records', force_ascii=False, indent=4)
        else:
            raise ValueError(f"Formato '{formato}' não suportado. Use 'csv' ou 'json'.")
        
        print(f"Dataset salvo com sucesso em {filepath}")
        return filepath


# Exemplo de uso
if __name__ == "__main__":
    # Criar instância do extrator
    extrator = FatoOuFakeAPIExtractor()
    
    # Executar extração
    df_noticias = extrator.executar_extracao()
    
    if not df_noticias.empty:
        # Exibir estatísticas básicas
        total_noticias = len(df_noticias)
        total_fake = len(df_noticias[df_noticias['classificacao'] == 'FAKE'])
        total_fato = len(df_noticias[df_noticias['classificacao'] == 'FATO'])
        total_indeterminado = len(df_noticias[df_noticias['classificacao'] == 'INDETERMINADO'])
        
        print(f"\nEstatísticas do Dataset:")
        print(f"Total de notícias: {total_noticias}")
        print(f"Classificadas como FAKE: {total_fake} ({total_fake/total_noticias*100:.1f}%)")
        print(f"Classificadas como FATO: {total_fato} ({total_fato/total_noticias*100:.1f}%)")
        print(f"Classificação indeterminada: {total_indeterminado} ({total_indeterminado/total_noticias*100:.1f}%)")
        
        # Salvar em CSV e JSON
        extrator.salvar_dataset(df_noticias, formato='csv')
        extrator.salvar_dataset(df_noticias, formato='json')
    else:
        print("Nenhum dado extraído para salvar.")