"""
BIM 数据处理器：BIM/IFC/JSON → 统一 JSON 格式 → 可入库
支持：.json（BIM 导出）、.ifc（可选 ifcopenshell）
"""
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# 允许的 BIM 相关扩展
BIM_EXTENSIONS = {'.json', '.ifc'}


def bim_to_json(raw: bytes, filename: str) -> Dict[str, Any]:
    """
    将 BIM 数据转为统一 JSON 结构并返回。
    
    :param raw: 文件字节
    :param filename: 文件名（用于判断格式）
    :return: 标准化后的 JSON 字典，用于入库 content 与向量化
    """
    ext = (filename or '').lower()
    if not ext.endswith('.json') and not ext.endswith('.ifc'):
        if '.json' in ext:
            ext = '.json'
        elif '.ifc' in ext:
            ext = '.ifc'
        else:
            ext = '.' + ext.split('.')[-1] if '.' in ext else ''

    if ext.endswith('.json'):
        return _json_file_to_bim_json(raw, filename)
    if ext.endswith('.ifc'):
        return _ifc_file_to_bim_json(raw, filename)
    raise ValueError(f"不支持的 BIM 格式，仅支持 .json / .ifc，当前: {filename}")


def _json_file_to_bim_json(raw: bytes, filename: str) -> Dict[str, Any]:
    """BIM 导出的 JSON 文件 → 统一 JSON（校验并补全元数据）"""
    try:
        data = json.loads(raw.decode('utf-8'))
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {e}")
    if not isinstance(data, (dict, list)):
        raise ValueError("BIM JSON 应为对象或数组")
    return _normalize_bim_json(data, filename, source_format='json')


def _ifc_file_to_bim_json(raw: bytes, filename: str) -> Dict[str, Any]:
    """IFC 文件 → 统一 JSON（依赖 ifcopenshell，可选）"""
    try:
        import ifcopenshell
    except ImportError:
        raise ValueError(
            "IFC 转换需要安装 ifcopenshell，请执行: pip install ifcopenshell ，或直接上传 BIM 导出的 .json 文件"
        )
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(delete=False, suffix='.ifc') as f:
        f.write(raw)
        path = f.name
    try:
        ifc_file = ifcopenshell.open(path)
        # 提取常用实体为可检索的 JSON
        elements = []
        for product in ifc_file.by_type("IfcProduct"):
            try:
                info = product.get_info(recursive=False, include_identifier=True)
                # 转成可 JSON 序列化的类型
                elem = {
                    "type": product.is_a(),
                    "id": str(product.id()),
                    "name": getattr(product, "Name", None) or info.get("Name"),
                    "description": getattr(product, "Description", None) or info.get("Description"),
                }
                if elem["name"] is None:
                    elem["name"] = ""
                elements.append(elem)
            except Exception as e:
                logger.debug("skip product %s: %s", product, e)
        out = {
            "source": filename,
            "format": "ifc",
            "schema": getattr(ifc_file, "schema", None) or "IFC4",
            "elements": elements,
            "element_count": len(elements),
        }
        return _normalize_bim_json(out, filename, source_format='ifc')
    finally:
        if os.path.exists(path):
            os.unlink(path)


def _normalize_bim_json(data: Any, filename: str, source_format: str) -> Dict[str, Any]:
    """统一为带元数据的 BIM JSON 结构，便于入库与检索"""
    if isinstance(data, list):
        payload = {"items": data, "count": len(data)}
    elif isinstance(data, dict):
        payload = dict(data)
        if "items" not in payload and "elements" not in payload:
            payload["items"] = [data]
        if "count" not in payload:
            payload["count"] = len(payload.get("items") or payload.get("elements") or [])
    else:
        payload = {"items": [], "count": 0}
    return {
        "bim_meta": {
            "source_file": filename,
            "source_format": source_format,
        },
        **payload,
    }


def bim_json_to_searchable_text(bim_json: Dict[str, Any], max_length: int = 50000) -> str:
    """
    将 BIM JSON 转为可向量化的纯文本（用于 content 或仅用于 embedding）。
    控制长度避免超长导致向量化失败。会输出 type/name/description 以及 properties 内键值，便于检索如「最小安全回转半径」等参数。
    """
    parts = []
    meta = bim_json.get("bim_meta") or {}
    parts.append(f"BIM来源: {meta.get('source_file', '')} 格式: {meta.get('source_format', '')}")
    elements = bim_json.get("elements") or bim_json.get("items") or []
    for i, el in enumerate(elements):
        if not isinstance(el, dict):
            parts.append(json.dumps(el, ensure_ascii=False))
            continue
        line_parts = []
        for k in ("type", "name", "description", "Type", "Name", "Description"):
            if k in el and el[k] is not None and str(el[k]).strip():
                line_parts.append(f"{k}: {el[k]}")
        # 展平 properties 便于检索「最小安全回转半径」等参数
        props = el.get("properties") or el.get("Properties")
        if isinstance(props, dict):
            for pk, pv in props.items():
                if pv is not None and str(pv).strip():
                    line_parts.append(f"{pk}: {pv}")
        if not line_parts:
            line_parts.append(json.dumps(el, ensure_ascii=False)[:200])
        parts.append(" | ".join(line_parts))
        if len("\n".join(parts)) > max_length:
            break
    text = "\n".join(parts)
    return text[:max_length] if len(text) > max_length else text


def bim_json_to_elements_list(bim_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """从 BIM JSON 提取元素列表（type/name），用于 metadata.bim_elements 与检索摘要。"""
    elements = bim_json.get("elements") or bim_json.get("items") or []
    out = []
    for el in elements:
        if not isinstance(el, dict):
            continue
        item = {}
        for k in ("type", "name", "Type", "Name"):
            if k in el and el[k] is not None and str(el[k]).strip():
                item["type" if k in ("type", "Type") else "name"] = el[k]
        if item:
            out.append(item)
    return out
