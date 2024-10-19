import os
from notion_client import Client
from dotenv import load_dotenv
from fpdf import FPDF


class PageNotion:
    def __init__(self, api_key, pageId):
        self.api_key = api_key
        self.page_id = pageId
        self.notion = Client(auth=self.api_key)  # Cria um cliente do Notion autenticado

    # extrai o texto simples
    def get_plain_text_from_rich_text(self, rich_text):
        return ''.join([t['plain_text'] for t in rich_text])

    # Extrai a URL e a legenda de blocos de mídia
    def get_media_source_text(self, block):

        source = None
        caption = None
        block_type = block[block['type']]  # Obtém o tipo do bloco

        # Verifica o tipo de fonte de mídia
        if 'external' in block_type:
            source = block_type['external']['url']
        elif 'file' in block_type:
            source = block_type['file']['url']
        elif 'url' in block_type:
            source = block_type['url']
        else:
            source = f"[Missing case for media block types]: {block['type']}"

        # Extrai legenda
        if block_type.get('caption'):
            caption = self.get_plain_text_from_rich_text(block_type['caption'])
            return f"{caption}: {source}"

        return source

    # Extrai texto de um bloco específico com base no seu tipo
    def get_text_from_block(self, block):

        block_type = block['type']
        block_data = block[block_type]

        if 'rich_text' in block_data:
            text = self.get_plain_text_from_rich_text(block_data['rich_text'])  # Texto rico
        else:
            if block_type == 'bookmark':
                text = block_data['url']
            elif block_type in ['child_database', 'child_page']:
                text = block_data['title']  # Título de páginas ou bancos de dados filhos
            elif block_type in ['embed', 'video', 'file', 'image', 'pdf']:
                text = self.get_media_source_text(block)  # Fonte de mídia
            elif block_type == 'equation':
                text = block_data['expression']  # Expressão matemática
            elif block_type == 'link_preview':
                text = block_data['url']  # URL
            elif block_type == 'synced_block':
                text = block_data.get('synced_from', {}).get(block_data['synced_from']['type'], '') if block_data.get('synced_from') else 'Source sync block'
            elif block_type == 'table':
                text = f"Table width: {block_data['table_width']}"
            elif block_type == 'table_of_contents':
                text = f"ToC color: {block_data['color']}"
            else:
                text = "[Unsupported block type or needs case added]"

        # Chama a função recursivamente em caso de blocos dentro de blocos
        if block['has_children']:
            children = self.retrieve_block_children(block['id'])
            text += " (Has children):\n" + "\n".join(self.get_text_from_block(child) for child in children)

        return f"{block_type}: {text}"

    def retrieve_block_children(self, block_id):

        blocks = []
        next_cursor = None

        while True:

            response = self.notion.blocks.children.list(block_id=block_id, start_cursor=next_cursor)
            blocks.extend(response['results'])
            next_cursor = response.get('next_cursor')
            if not next_cursor:
                break

        for block in blocks:
            if block['has_children']:
                block['children'] = self.retrieve_block_children(block['id'])

        return blocks

    # Obtém o texto completo da página
    def get_page_text(self):

        blocks = self.retrieve_block_children(self.page_id)
        page_text = "\n".join(self.get_text_from_block(block) for block in blocks)  # Junta o texto de todos os blocos
        return page_text

        # Salva o texto em um arquivo PDF
    def save_text_to_pdf(self, text, filename='Base/pagina_notion.pdf'):

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)

        # Quebra o texto em linhas e adiciona ao PDF
        for line in text.split('\n'):
            pdf.cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'), new_x='LMARGIN', new_y='NEXT')

        pdf.output(filename)


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("NOTION_API_KEY")
    avec_page_id = os.getenv("AVEC_PAGE_ID")
    page_notion = PageNotion(api_key, avec_page_id)


    texto_da_pagina = page_notion.get_page_text()


    page_notion.save_text_to_pdf(texto_da_pagina)
    print(texto_da_pagina)
