# Extrator de Notícias Fato ou Fake do G1

Este projeto é uma ferramenta para extrair notícias da seção "Fato ou Fake" do portal G1 e criar um dataset estruturado de checagens de notícias, classificadas como verdadeiras (FATO) ou falsas (FAKE).

## Descrição

O objetivo deste projeto é facilitar a criação de um dataset confiável de notícias verificadas por jornalistas profissionais, que pode ser usado para:

- Treinamento de modelos de detecção de fake news
- Análise de padrões e características de notícias falsas
- Pesquisas sobre desinformação
- Educação sobre verificação de fatos

A ferramenta utiliza diferentes abordagens para extrair informações, oferecendo flexibilidade e robustez.

## Estrutura do Projeto

O projeto contém três scripts principais:

1. **fato_ou_fake_scraper.py**: Extrai notícias através de web scraping direto da página do G1.
2. **fato_ou_fake_api.py**: Tenta extrair notícias através de API ou feed RSS do G1 (quando disponíveis).
3. **extrator_combinado.py**: Combina os métodos anteriores para criar um dataset mais completo.

## Requisitos

- Python 3.6+
- Bibliotecas requeridas (instale com `pip install -r requirements.txt`):
  - requests
  - beautifulsoup4
  - pandas
  - feedparser

## Instalação

1. Clone este repositório:
   ```
   git clone https://github.com/seu-usuario/extrator-fato-ou-fake.git
   cd extrator-fato-ou-fake
   ```

2. Crie e ative um ambiente virtual:

   **No Windows:**
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

   **No macOS/Linux:**
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Para desativar o ambiente virtual quando terminar:
   ```
   deactivate
   ```

## Uso

### Extração por Web Scraping

Para extrair notícias diretamente do site usando web scraping:

```python
from fato_ou_fake_scraper import FatoOuFakeScraper

# Criar instância do scraper (padrão: 5 páginas)
scraper = FatoOuFakeScraper(num_pages=10)

# Executar extração
df_noticias = scraper.executar_extracao()

# Salvar em CSV e JSON
scraper.salvar_dataset(df_noticias, formato='csv')
scraper.salvar_dataset(df_noticias, formato='json')
```

Também pode ser executado diretamente:

```
python fato_ou_fake_scraper.py
```

### Extração via API/RSS

Para tentar extrair notícias via API ou feed RSS:

```python
from fato_ou_fake_api import FatoOuFakeAPIExtractor

# Criar instância do extrator
extrator = FatoOuFakeAPIExtractor()

# Executar extração
df_noticias = extrator.executar_extracao()

# Salvar em CSV e JSON
extrator.salvar_dataset(df_noticias, formato='csv')
extrator.salvar_dataset(df_noticias, formato='json')
```

Também pode ser executado diretamente:

```
python fato_ou_fake_api.py
```

### Extração Combinada

Para usar ambos os métodos e criar um dataset unificado:

```python
from extrator_combinado import ExtratorCombinado

# Criar instância do extrator combinado
extrator = ExtratorCombinado(num_paginas=10, metodo='todos')

# Executar extração
df_noticias = extrator.executar_extracao()

# Salvar em CSV e JSON
extrator.salvar_dataset(df_noticias, formato='csv')
extrator.salvar_dataset(df_noticias, formato='json')
```

Ou através da linha de comando:

```
python extrator_combinado.py --metodo todos --paginas 10 --formato ambos
```

Opções disponíveis:
- `--metodo`: `scraping`, `api` ou `todos` (padrão: `todos`)
- `--paginas`: número de páginas a serem extraídas (padrão: 5)
- `--formato`: `csv`, `json` ou `ambos` (padrão: `csv`)

## Estrutura do Dataset

O dataset gerado contém os seguintes campos:

- **titulo**: Título da notícia
- **link**: URL da notícia
- **data_publicacao**: Data de publicação
- **resumo**: Resumo ou subtítulo da notícia
- **classificacao**: Classificação como 'FATO', 'FAKE' ou 'INDETERMINADO'
- **imagem_url**: URL da imagem principal (se disponível)
- **conteudo**: Texto completo da notícia
- **tags**: Tags associadas à notícia
- **autor**: Autor da notícia (se disponível)
- **data_extracao**: Data e hora da extração
- **metodo_extracao**: Método usado para extrair a notícia

## Limitações

- O web scraping pode ser afetado por mudanças na estrutura do site do G1.
- Os feeds RSS ou APIs podem estar indisponíveis ou ter limitações de acesso.
- A classificação automática de notícias como FATO ou FAKE é baseada em padrões de texto e pode não ser 100% precisa.

## Uso Ético

Este projeto destina-se a fins educacionais, de pesquisa e para combater a desinformação. Ao utilizar esta ferramenta, lembre-se de:

- Respeitar os termos de serviço do site G1
- Não sobrecarregar os servidores com requisições excessivas
- Utilizar os dados extraídos de forma ética e responsável

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.