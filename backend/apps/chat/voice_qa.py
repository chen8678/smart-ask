"""
语音问答API - 演示版本
功能：
1. 语音转文字（STT）
2. 文字转语音（TTS）
3. 基于知识库的问答
"""
import os
import base64
import tempfile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .services import QAService
from apps.knowledge.models import KnowledgeBase
import requests
import json


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voice_to_text(request):
    """
    语音转文字（STT）
    
    请求格式：
    {
        "audio_data": "base64编码的音频数据",
        "format": "wav" 或 "mp3"
    }
    
    返回格式：
    {
        "text": "转换后的文字"
    }
    """
    try:
        audio_data = request.data.get('audio_data')
        audio_format = request.data.get('format', 'wav')
        
        if not audio_data:
            return Response(
                {'error': '请提供音频数据'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 解码base64音频数据
        try:
            audio_bytes = base64.b64decode(audio_data)
        except Exception as e:
            return Response(
                {'error': f'音频数据解码失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{audio_format}') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        try:
            # 使用百度语音识别API（免费版）
            # 也可以使用其他服务：Google Speech-to-Text, Azure Speech等
            baidu_api_key = os.getenv('BAIDU_STT_API_KEY', '')
            baidu_secret_key = os.getenv('BAIDU_STT_SECRET_KEY', '')
            
            if baidu_api_key and baidu_secret_key:
                # 使用百度语音识别
                text = _baidu_speech_to_text(tmp_file_path, baidu_api_key, baidu_secret_key)
            else:
                # 简化版本：返回提示信息（实际应该调用语音识别服务）
                text = "请配置语音识别API密钥（百度、Google、Azure等）"
                # 或者使用本地语音识别库
                # text = _local_speech_to_text(tmp_file_path)
            
            return Response({
                'text': text,
                'format': audio_format
            })
        finally:
            # 清理临时文件
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    except Exception as e:
        return Response(
            {'error': f'语音转文字失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _baidu_speech_to_text(audio_path, api_key, secret_key):
    """使用百度语音识别API"""
    try:
        # 获取access_token
        token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
        token_response = requests.post(token_url)
        access_token = token_response.json().get('access_token')
        
        if not access_token:
            return "百度语音识别API配置错误"
        
        # 调用语音识别接口
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        stt_url = f"https://vop.baidu.com/server_api?access_token={access_token}"
        headers = {'Content-Type': 'audio/wav;rate=16000'}
        response = requests.post(stt_url, headers=headers, data=audio_data)
        
        result = response.json()
        if result.get('err_no') == 0:
            return result.get('result', [''])[0]
        else:
            return f"识别失败: {result.get('err_msg', '未知错误')}"
    except Exception as e:
        return f"语音识别错误: {str(e)}"


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def text_to_voice(request):
    """
    文字转语音（TTS）
    
    请求格式：
    {
        "text": "要转换的文字",
        "voice": "zh-CN-XiaoxiaoNeural"  # 可选，语音类型
    }
    
    返回格式：
    {
        "audio_data": "base64编码的音频数据",
        "format": "mp3"
    }
    """
    try:
        text = request.data.get('text', '').strip()
        
        if not text:
            return Response(
                {'error': '请提供要转换的文字'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 使用百度TTS API（免费版）
        baidu_api_key = os.getenv('BAIDU_TTS_API_KEY', '')
        baidu_secret_key = os.getenv('BAIDU_TTS_SECRET_KEY', '')
        
        if baidu_api_key and baidu_secret_key:
            audio_data = _baidu_text_to_speech(text, baidu_api_key, baidu_secret_key)
        else:
            # 简化版本：返回提示
            audio_data = None
            # 或者使用本地TTS库
            # audio_data = _local_text_to_speech(text)
        
        if audio_data:
            # 编码为base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            return Response({
                'audio_data': audio_base64,
                'format': 'mp3',
                'text': text
            })
        else:
            return Response(
                {'error': '请配置TTS API密钥（百度、Google、Azure等）'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'error': f'文字转语音失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _baidu_text_to_speech(text, api_key, secret_key):
    """使用百度TTS API"""
    try:
        # 获取access_token
        token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
        token_response = requests.post(token_url)
        access_token = token_response.json().get('access_token')
        
        if not access_token:
            return None
        
        # 调用TTS接口
        tts_url = f"https://tsn.baidu.com/text2audio?access_token={access_token}"
        params = {
            'tex': text,
            'tok': access_token,
            'cuid': 'demo',
            'ctp': 1,
            'lan': 'zh',
            'per': 0,  # 0-女声，1-男声
            'spd': 5,  # 语速 0-15
            'pit': 5,  # 音调 0-15
            'vol': 5,  # 音量 0-15
        }
        
        response = requests.post(tts_url, data=params)
        
        # 检查是否是音频数据
        if response.headers.get('Content-Type', '').startswith('audio'):
            return response.content
        else:
            # 可能是错误信息
            result = response.json()
            print(f"TTS错误: {result}")
            return None
    except Exception as e:
        print(f"TTS错误: {e}")
        return None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voice_qa(request):
    """
    语音问答（完整流程）
    
    请求格式：
    {
        "audio_data": "base64编码的音频数据",
        "knowledge_base_id": "知识库ID（可选）"
    }
    
    返回格式：
    {
        "question": "识别的问题",
        "answer": "AI回答",
        "audio_data": "base64编码的语音回答",
        "sources": ["文档1", "文档2"]
    }
    """
    try:
        audio_data = request.data.get('audio_data')
        knowledge_base_id = request.data.get('knowledge_base_id')
        
        if not audio_data:
            return Response(
                {'error': '请提供音频数据'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 1. 语音转文字（直接调用内部函数）
        try:
            # 解码base64音频数据
            audio_bytes = base64.b64decode(audio_data)
            
            # 保存临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            try:
                # 使用百度语音识别API
                baidu_api_key = os.getenv('BAIDU_STT_API_KEY', '')
                baidu_secret_key = os.getenv('BAIDU_STT_SECRET_KEY', '')
                
                if baidu_api_key and baidu_secret_key:
                    question = _baidu_speech_to_text(tmp_file_path, baidu_api_key, baidu_secret_key)
                else:
                    question = "请配置语音识别API密钥（百度、Google、Azure等）"
            finally:
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
        except Exception as e:
            return Response({
                'error': f'语音识别失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not question or question.startswith('请配置'):
            return Response({
                'error': '语音识别失败，请配置语音识别API',
                'question': question
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. 获取知识库ID
        if not knowledge_base_id:
            user_kb = KnowledgeBase.objects.filter(owner=request.user).first()
            if not user_kb:
                return Response(
                    {'error': '请先创建知识库并上传文档'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            knowledge_base_id = str(user_kb.id)
        
        # 3. 问答
        qa_service = QAService(model='deepseek-chat')
        qa_result = qa_service.ask_question(
            question=question,
            knowledge_base_id=knowledge_base_id,
            user=request.user
        )
        
        answer = qa_result.get('answer', '')
        sources = qa_result.get('sources', [])
        
        # 4. 文字转语音（直接调用内部函数）
        audio_data_result = None
        try:
            baidu_api_key = os.getenv('BAIDU_TTS_API_KEY', '')
            baidu_secret_key = os.getenv('BAIDU_TTS_SECRET_KEY', '')
            
            if baidu_api_key and baidu_secret_key:
                audio_bytes = _baidu_text_to_speech(answer, baidu_api_key, baidu_secret_key)
                if audio_bytes:
                    audio_data_result = base64.b64encode(audio_bytes).decode('utf-8')
        except Exception as e:
            print(f"TTS错误: {e}")
        
        audio_data_result = None
        if tts_response.status_code == status.HTTP_200_OK:
            audio_data_result = tts_response.data.get('audio_data')
        
        return Response({
            'question': question,
            'answer': answer,
            'audio_data': audio_data_result,
            'sources': sources,
            'from_private_kb': True
        })
        
    except Exception as e:
        return Response(
            {'error': f'语音问答失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

