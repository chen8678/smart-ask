from typing import Any, Dict, Optional, Tuple


def normalize_json_entry(entry: Dict[str, Any], index: int) -> Tuple[Optional[str], Optional[str], Dict[str, Any], Optional[str]]:
    """
    根据用户提供的 JSON 条目生成 title/content/metadata。
    支持 question/answer 结构或直接提供 content。
    返回 (title, content, metadata, skip_reason)
    """
    metadata = entry.get('metadata')
    if metadata is None or not isinstance(metadata, dict):
        metadata = {}

    content = entry.get('content')

    if not content:
        # 支持 text 字段（HuggingFace datasets 格式）
        text_keys = ['text', 'content', 'body', 'document']
        text_value = next((entry.get(key) for key in text_keys if entry.get(key)), None)
        if text_value:
            if isinstance(text_value, str):
                content = text_value.strip()
            elif isinstance(text_value, list):
                content = '\n'.join(str(item).strip() for item in text_value if str(item).strip())
            else:
                content = str(text_value).strip()
        
        # 如果没有 text，尝试 question/answer 结构
        if not content:
            question_keys = ['question', 'q', 'prompt', 'ask']
            answer_keys = ['answer', 'answers', 'response', 'responses', 'a']

            question = next((entry.get(key) for key in question_keys if entry.get(key)), '')
            question = question.strip() if isinstance(question, str) else ''

            answer_value = next((entry.get(key) for key in answer_keys if entry.get(key)), None)
            answer_text = ''
            if isinstance(answer_value, list):
                answer_text = '\n'.join(str(item).strip() for item in answer_value if str(item).strip())
            elif isinstance(answer_value, str):
                answer_text = answer_value.strip()

            if question or answer_text:
                if question and answer_text:
                    content = f"问题：{question}\n回答：{answer_text}"
                elif question:
                    content = question
                else:
                    content = answer_text

                metadata.setdefault('json_import', {})
                metadata['json_import']['question'] = question
                metadata['json_import']['answer'] = answer_value

    if not content:
        return None, None, metadata, '无法从条目中提取 content / text / question / answer'

    title = entry.get('title')
    if not title:
        question_preview = metadata.get('json_import', {}).get('question') if metadata.get('json_import') else ''
        source_text = question_preview or content
        stripped = str(source_text).replace('\n', ' ').strip()
        if stripped:
            title = stripped[:40] + ('...' if len(stripped) > 40 else '')
        else:
            title = f'JSON 文档 {index + 1}'

    metadata.setdefault('json_import', {})
    metadata['json_import']['original_index'] = index
    return title, content, metadata, None

