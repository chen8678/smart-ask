"""
清理聊天数据的Django管理命令
类似NotebookLM的临时存储策略
"""
from django.core.management.base import BaseCommand
from apps.chat.models import QARecord, ChatSession
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = '清理过期的聊天数据，实现类似NotebookLM的临时存储策略'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='清理多少天前的数据 (默认: 7天)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将要删除的数据，不实际删除'
        )
        parser.add_argument(
            '--cleanup-sessions',
            action='store_true',
            help='同时清理不活跃的会话'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cleanup_sessions = options['cleanup_sessions']
        
        self.stdout.write(f"开始清理 {days} 天前的聊天数据...")
        
        # 清理旧的问答记录
        if not dry_run:
            deleted_records = QARecord.cleanup_old_records(days)
            self.stdout.write(
                self.style.SUCCESS(f'已删除 {deleted_records} 条问答记录')
            )
        else:
            cutoff_date = timezone.now() - timedelta(days=days)
            old_records = QARecord.objects.filter(created_at__lt=cutoff_date)
            count = old_records.count()
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] 将删除 {count} 条问答记录')
            )
        
        # 清理不活跃的会话
        if cleanup_sessions:
            if not dry_run:
                deleted_sessions = QARecord.cleanup_inactive_sessions(30)
                self.stdout.write(
                    self.style.SUCCESS(f'已标记 {deleted_sessions} 个会话为不活跃')
                )
            else:
                cutoff_date = timezone.now() - timedelta(days=30)
                inactive_sessions = ChatSession.objects.filter(
                    last_activity__lt=cutoff_date,
                    is_active=True
                )
                count = inactive_sessions.count()
                self.stdout.write(
                    self.style.WARNING(f'[DRY RUN] 将标记 {count} 个会话为不活跃')
                )
        
        # 显示统计信息
        total_sessions = ChatSession.objects.filter(is_active=True).count()
        total_messages = QARecord.objects.count()
        
        self.stdout.write(f"当前活跃会话数: {total_sessions}")
        self.stdout.write(f"当前消息总数: {total_messages}")
        
        self.stdout.write(
            self.style.SUCCESS('数据清理完成！')
        )
