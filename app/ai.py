from typing import List
from openai import OpenAI
from pathlib import Path
import docx
from os import getenv


def convert_docx_to_txt(docx_path: str) -> str:
    '''Конвертирует DOCX в текст'''
    doc = docx.Document(docx_path)
    text = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)
    return '\n'.join(text)


def save_knowledge_base(text: str, output_path: str):
    '''Сохраняет текст в файл'''
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)


client = OpenAI(api_key=getenv('API_KEY'))


def upload_knowledge_files(file_paths: List[str]) -> List[str]:
    '''Загружает файлы в OpenAI и возвращает их ID'''
    file_ids = []

    for file_path in file_paths:
        with open(file_path, 'rb') as f:
            file = client.files.create(
                file=f,
                purpose='assistants'
            )
            file_ids.append(file.id)

    return file_ids


def create_vector_store(name: str, file_ids: List[str]) -> str:
    '''Создает векторное хранилище с файлами'''
    vector_store = client.beta.vector_stores.create(
        name=name,
        file_ids=file_ids
    )
    return vector_store.id


def create_assistant(vector_store_id: str) -> str:
    '''Создает ассистента с базой знаний'''

    # Критически важный промпт
    system_prompt = '''Ты - профессиональный консультант компании. 

СТРОГИЕ ПРАВИЛА:
1. Отвечай ТОЛЬКО на основе информации из базы знаний
2. Если информации нет в базе - четко скажи: 'К сожалению, такой информации нет в моей базе знаний'
3. НЕ придумывай информацию
4. НЕ используй общие знания - только база знаний
5. Отвечай конкретно и по существу
6. Если вопрос неясен - попроси уточнить

Твоя задача - давать точные ответы на основе документов.'''

    assistant = client.beta.assistants.create(
        name='Консультант',
        instructions=system_prompt,
        model='gpt-5-mini',
        tools=[{'type': 'file_search'}],
        tool_resources={
            'file_search': {
                'vector_store_ids': [vector_store_id]
            }
        }
    )

    return assistant.id


docx_files = ['knowledge/document1.docx']
txt_files = []
for docx_file in docx_files:
    text = convert_docx_to_txt(docx_file)
    txt_path = docx_file.replace('.docx', '.txt')
    save_knowledge_base(text, txt_path)
    txt_files.append(txt_path)

file_ids = upload_knowledge_files(txt_files)
vector_store_id = create_vector_store("My Knowledge Base", file_ids)
ASSISTANT_ID = create_assistant(vector_store_id)
