import json
import logging

try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(f):
            return f
        return decorator(args[0]) if args and callable(args[0]) else decorator

from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone
from typing import List
from .models import ImportJob, Document
from .vectorization_service import VectorizationService
from .import_utils import normalize_json_entry

logger = logging.getLogger(__name__)


@shared_task(bind=True, acks_late=True)
def process_import_job(self, job_id: str):
    try:
        job = ImportJob.objects.select_related('knowledge_base').get(id=job_id)
    except ImportJob.DoesNotExist:
        logger.warning(f"ImportJob {job_id} 不存在")
        return

    if job.is_final:
        return

    job.mark_processing()

    try:
        with default_storage.open(job.file_path, 'r') as fp:
            data = json.load(fp)
    except Exception as exc:
        logger.exception("读取 JSON 文件失败: %s", exc)
        job.mark_failed(f'读取 JSON 文件失败: {exc}')
        return

    # 支持多种 JSON 结构
    entries = []
    if isinstance(data, dict):
        # 结构1: {"documents": [...]}
        if 'documents' in data:
            entries = data['documents']
        # 结构2: {"rows": [{"row": {...}, ...}]} - HuggingFace datasets 格式
        elif 'rows' in data:
            rows = data.get('rows', [])
            # 将 rows 转换为标准格式
            for row_item in rows:
                if isinstance(row_item, dict):
                    # 如果 row_item 有 'row' 键，提取其内容
                    if 'row' in row_item:
                        entries.append(row_item['row'])
                    else:
                        # 否则直接使用 row_item
                        entries.append(row_item)
        # 结构3: 直接是对象，尝试提取所有值作为条目
        else:
            # 如果只有一个顶层对象，尝试将其作为单个条目
            entries = [data]
    elif isinstance(data, list):
        # 结构4: 直接是数组
        entries = data
    else:
        job.mark_failed('JSON 格式不支持：必须是对象、数组或包含 documents/rows 的对象')
        return

    if not isinstance(entries, list) or len(entries) == 0:
        job.mark_failed('JSON 中未找到可导入的条目（documents/rows 数组为空）')
        return

    total = len(entries)
    job.total_documents = total
    job.save(update_fields=['total_documents'])

    vectorizer = VectorizationService()
    created = 0
    vectorized = 0
    skipped = 0
    skipped_samples: List[dict] = list(job.skipped_samples or [])

    def _flush_progress():
        """更新进度到数据库"""
        try:
            job.refresh_from_db(fields=['status'])
            if job.status == ImportJob.Status.CANCELED:
                return False
            job.update_progress(created, vectorized, skipped, skipped_samples)
            return True
        except Exception as exc:
            logger.error(f"更新进度失败: {exc}")
            return False

    # 初始进度更新
    _flush_progress()

    try:
        for index, entry in enumerate(entries):
            job.refresh_from_db(fields=['status'])
            if job.status == ImportJob.Status.CANCELED:
                logger.info("ImportJob %s 被取消", job.id)
                return

            if not isinstance(entry, dict):
                skipped += 1
                if len(skipped_samples) < 10:
                    skipped_samples.append({'index': index, 'reason': '条目必须是对象'})
                # 每 10 个条目更新一次进度
                if (index + 1) % 10 == 0:
                    _flush_progress()
                continue

            title, content, metadata, reason = normalize_json_entry(entry, index)
            if reason:
                skipped += 1
                if len(skipped_samples) < 10:
                    skipped_samples.append({'index': index, 'reason': reason})
                # 每 10 个条目更新一次进度
                if (index + 1) % 10 == 0:
                    _flush_progress()
                continue

            try:
                with transaction.atomic():
                    document = Document.objects.create(
                        knowledge_base=job.knowledge_base,
                        title=title[:200] if title else f'JSON 文档 {index + 1}',
                        content=content,
                        content_type='text',
                        metadata=metadata
                    )
                created += 1
            except Exception as exc:
                logger.error(f"创建文档失败 (index {index}): {exc}")
                skipped += 1
                if len(skipped_samples) < 10:
                    skipped_samples.append({'index': index, 'reason': f'保存失败: {exc}'})
                # 每 10 个条目更新一次进度
                if (index + 1) % 10 == 0:
                    _flush_progress()
                continue

            try:
                embedding = vectorizer.vectorize_text(content)
                document.vector_embedding = embedding.tolist()
                document.save(update_fields=['vector_embedding', 'updated_at'])
                vectorized += 1
            except Exception as exc:
                logger.warning("文档 %s 向量化失败: %s", document.id, exc)
                if len(skipped_samples) < 10:
                    skipped_samples.append({'index': index, 'reason': f'向量化失败: {exc}'})

            # 每 10 个条目更新一次进度（更频繁的更新）
            if (index + 1) % 10 == 0:
                _flush_progress()

        # 最终进度更新
        _flush_progress()
        job.mark_succeeded()
        logger.info(f"ImportJob {job.id} 完成: 创建 {created}, 向量化 {vectorized}, 跳过 {skipped}")
    except Exception as exc:
        logger.exception(f"ImportJob {job.id} 处理失败: {exc}")
        job.mark_failed(f'处理失败: {exc}')
        raise

