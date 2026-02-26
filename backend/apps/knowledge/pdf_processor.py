"""
PDF文件处理工具
"""
import logging
from typing import Optional
import PyPDF2
import pdfplumber
from io import BytesIO

logger = logging.getLogger(__name__)


class PDFProcessor:
    """PDF文件处理器"""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> Optional[str]:
        """
        从PDF文件中提取文本内容
        
        Args:
            file_content: PDF文件的字节内容
            
        Returns:
            提取的文本内容，如果失败返回None
        """
        try:
            # 首先尝试使用pdfplumber（更好的表格和布局处理）
            with pdfplumber.open(BytesIO(file_content)) as pdf:
                text_content = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                
                if text_content:
                    return '\n\n'.join(text_content)
            
            # 如果pdfplumber失败，尝试PyPDF2
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text_content = []
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
            
            if text_content:
                return '\n\n'.join(text_content)
            
            logger.warning("PDF文件没有提取到文本内容")
            return None
            
        except Exception as e:
            logger.error(f"PDF文本提取失败: {str(e)}")
            return None
    
    @staticmethod
    def is_pdf_file(file_content: bytes) -> bool:
        """
        检查文件是否为PDF格式
        
        Args:
            file_content: 文件字节内容
            
        Returns:
            是否为PDF文件
        """
        return file_content.startswith(b'%PDF-')
    
    @staticmethod
    def get_pdf_info(file_content: bytes) -> dict:
        """
        获取PDF文件信息
        
        Args:
            file_content: PDF文件字节内容
            
        Returns:
            PDF文件信息字典
        """
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            return {
                'page_count': len(pdf_reader.pages),
                'is_encrypted': pdf_reader.is_encrypted,
                'metadata': pdf_reader.metadata
            }
        except Exception as e:
            logger.error(f"获取PDF信息失败: {str(e)}")
            return {
                'page_count': 0,
                'is_encrypted': False,
                'metadata': None
            }

