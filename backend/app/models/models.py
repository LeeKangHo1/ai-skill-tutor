# backend/app/models/models.py
"""
데이터베이스 모델 클래스들을 정의하는 모듈
사용자 관련 모델: User, UserAuthToken, UserProgress, UserStatistics
학습 세션 관련 모델: LearningSession, SessionConversation, SessionQuiz
"""

from datetime import datetime
from typing import Optional, Dict, Any
import time


class User:
    """사용자 기본 정보를 관리하는 모델 클래스"""
    
    def __init__(self, user_id: Optional[int] = None, login_id: str = "", 
                 username: str = "", email: str = "", password_hash: str = "",
                 user_type: str = "unassigned", diagnosis_completed: bool = False,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        self.user_id = user_id
        self.login_id = login_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.user_type = user_type
        self.diagnosis_completed = diagnosis_completed
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'user_id': self.user_id,
            'login_id': self.login_id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'user_type': self.user_type,
            'diagnosis_completed': self.diagnosis_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        created_at = None
        updated_at = None
        
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        if data.get('updated_at'):
            if isinstance(data['updated_at'], str):
                updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
            else:
                updated_at = data['updated_at']
        
        return cls(
            user_id=data.get('user_id'),
            login_id=data.get('login_id', ''),
            username=data.get('username', ''),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            user_type=data.get('user_type', 'unassigned'),
            diagnosis_completed=data.get('diagnosis_completed', False),
            created_at=created_at,
            updated_at=updated_at
        )


class UserAuthToken:
    """사용자 인증 토큰을 관리하는 모델 클래스"""
    
    def __init__(self, token_id: Optional[int] = None, user_id: int = 0,
                 refresh_token: str = "", expires_at: Optional[datetime] = None,
                 is_active: bool = True, device_info: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self.token_id = token_id
        self.user_id = user_id
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.is_active = is_active
        self.device_info = device_info
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'token_id': self.token_id,
            'user_id': self.user_id,
            'refresh_token': self.refresh_token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'device_info': self.device_info,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserAuthToken':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        expires_at = None
        created_at = None
        
        if data.get('expires_at'):
            if isinstance(data['expires_at'], str):
                expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
            else:
                expires_at = data['expires_at']
        
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        return cls(
            token_id=data.get('token_id'),
            user_id=data.get('user_id', 0),
            refresh_token=data.get('refresh_token', ''),
            expires_at=expires_at,
            is_active=data.get('is_active', True),
            device_info=data.get('device_info'),
            created_at=created_at
        )


class UserProgress:
    """사용자 학습 진행 상태를 관리하는 모델 클래스"""
    
    def __init__(self, progress_id: Optional[int] = None, user_id: int = 0,
                 current_chapter: int = 1, last_study_date: Optional[datetime] = None,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        self.progress_id = progress_id
        self.user_id = user_id
        self.current_chapter = current_chapter
        self.last_study_date = last_study_date
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'progress_id': self.progress_id,
            'user_id': self.user_id,
            'current_chapter': self.current_chapter,
            'last_study_date': self.last_study_date.date().isoformat() if self.last_study_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProgress':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        last_study_date = None
        created_at = None
        updated_at = None
        
        if data.get('last_study_date'):
            if isinstance(data['last_study_date'], str):
                # DATE 타입은 날짜만 포함하므로 시간 부분을 추가
                last_study_date = datetime.fromisoformat(data['last_study_date'])
            else:
                last_study_date = data['last_study_date']
        
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        if data.get('updated_at'):
            if isinstance(data['updated_at'], str):
                updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
            else:
                updated_at = data['updated_at']
        
        return cls(
            progress_id=data.get('progress_id'),
            user_id=data.get('user_id', 0),
            current_chapter=data.get('current_chapter', 1),
            last_study_date=last_study_date,
            created_at=created_at,
            updated_at=updated_at
        )


class UserStatistics:
    """사용자 학습 통계를 관리하는 모델 클래스"""
    
    def __init__(self, stats_id: Optional[int] = None, user_id: int = 0,
                 total_study_time_minutes: int = 0, total_study_sessions: int = 0,
                 total_completed_sessions: int = 0, total_correct_answers: int = 0,
                 average_accuracy: float = 0.00, last_study_date: Optional[datetime] = None,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        self.stats_id = stats_id
        self.user_id = user_id
        self.total_study_time_minutes = total_study_time_minutes
        self.total_study_sessions = total_study_sessions
        self.total_completed_sessions = total_completed_sessions
        self.total_correct_answers = total_correct_answers
        self.average_accuracy = average_accuracy
        self.last_study_date = last_study_date
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'stats_id': self.stats_id,
            'user_id': self.user_id,
            'total_study_time_minutes': self.total_study_time_minutes,
            'total_study_sessions': self.total_study_sessions,
            'total_completed_sessions': self.total_completed_sessions,
            'total_correct_answers': self.total_correct_answers,
            'average_accuracy': float(self.average_accuracy),
            'last_study_date': self.last_study_date.date().isoformat() if self.last_study_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserStatistics':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        last_study_date = None
        created_at = None
        updated_at = None
        
        if data.get('last_study_date'):
            if isinstance(data['last_study_date'], str):
                last_study_date = datetime.fromisoformat(data['last_study_date'])
            else:
                last_study_date = data['last_study_date']
        
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        if data.get('updated_at'):
            if isinstance(data['updated_at'], str):
                updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
            else:
                updated_at = data['updated_at']
        
        return cls(
            stats_id=data.get('stats_id'),
            user_id=data.get('user_id', 0),
            total_study_time_minutes=data.get('total_study_time_minutes', 0),
            total_study_sessions=data.get('total_study_sessions', 0),
            total_completed_sessions=data.get('total_completed_sessions', 0),
            total_correct_answers=data.get('total_correct_answers', 0),
            average_accuracy=float(data.get('average_accuracy', 0.00)),
            last_study_date=last_study_date,
            created_at=created_at,
            updated_at=updated_at
        )


def generate_session_id(user_id: int, chapter: int, session_count: int) -> str:
    """
    세션 ID를 생성하는 함수
    형식: user{id}_ch{chapter}_session{count:03d}_{timestamp}
    
    Args:
        user_id: 사용자 ID
        chapter: 챕터 번호
        session_count: 세션 순서 번호
    
    Returns:
        생성된 세션 ID 문자열
    """
    timestamp = int(time.time())
    return f"user{user_id}_ch{chapter}_session{session_count:03d}_{timestamp}"


class LearningSession:
    """학습 세션 정보를 관리하는 모델 클래스"""
    
    def __init__(self, session_id: str = "", user_id: int = 0,
                 chapter_number: int = 1, session_sequence: int = 1,
                 session_start_time: Optional[datetime] = None,
                 session_end_time: Optional[datetime] = None,
                 study_duration_minutes: Optional[int] = None,
                 session_decision_result: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.chapter_number = chapter_number
        self.session_sequence = session_sequence
        self.session_start_time = session_start_time
        self.session_end_time = session_end_time
        self.study_duration_minutes = study_duration_minutes
        self.session_decision_result = session_decision_result
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'chapter_number': self.chapter_number,
            'session_sequence': self.session_sequence,
            'session_start_time': self.session_start_time.isoformat() if self.session_start_time else None,
            'session_end_time': self.session_end_time.isoformat() if self.session_end_time else None,
            'study_duration_minutes': self.study_duration_minutes,
            'session_decision_result': self.session_decision_result,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningSession':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        session_start_time = None
        session_end_time = None
        created_at = None
        
        if data.get('session_start_time'):
            if isinstance(data['session_start_time'], str):
                session_start_time = datetime.fromisoformat(data['session_start_time'].replace('Z', '+00:00'))
            else:
                session_start_time = data['session_start_time']
        
        if data.get('session_end_time'):
            if isinstance(data['session_end_time'], str):
                session_end_time = datetime.fromisoformat(data['session_end_time'].replace('Z', '+00:00'))
            else:
                session_end_time = data['session_end_time']
        
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        return cls(
            session_id=data.get('session_id', ''),
            user_id=data.get('user_id', 0),
            chapter_number=data.get('chapter_number', 1),
            session_sequence=data.get('session_sequence', 1),
            session_start_time=session_start_time,
            session_end_time=session_end_time,
            study_duration_minutes=data.get('study_duration_minutes'),
            session_decision_result=data.get('session_decision_result'),
            created_at=created_at
        )


class SessionConversation:
    """세션 대화 기록을 관리하는 모델 클래스"""
    
    def __init__(self, conversation_id: Optional[int] = None, session_id: str = "",
                 message_sequence: int = 1, agent_name: str = "",
                 message_type: str = "user", message_content: str = "",
                 message_timestamp: Optional[datetime] = None,
                 session_progress_stage: Optional[str] = None,
                 created_at: Optional[datetime] = None):
        self.conversation_id = conversation_id
        self.session_id = session_id
        self.message_sequence = message_sequence
        self.agent_name = agent_name
        self.message_type = message_type  # 'user', 'system', 'tool'
        self.message_content = message_content
        self.message_timestamp = message_timestamp or datetime.now()
        self.session_progress_stage = session_progress_stage
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'conversation_id': self.conversation_id,
            'session_id': self.session_id,
            'message_sequence': self.message_sequence,
            'agent_name': self.agent_name,
            'message_type': self.message_type,
            'message_content': self.message_content,
            'message_timestamp': self.message_timestamp.isoformat() if self.message_timestamp else None,
            'session_progress_stage': self.session_progress_stage,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionConversation':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        message_timestamp = None
        created_at = None
        
        if data.get('message_timestamp'):
            if isinstance(data['message_timestamp'], str):
                message_timestamp = datetime.fromisoformat(data['message_timestamp'].replace('Z', '+00:00'))
            else:
                message_timestamp = data['message_timestamp']
        
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        return cls(
            conversation_id=data.get('conversation_id'),
            session_id=data.get('session_id', ''),
            message_sequence=data.get('message_sequence', 1),
            agent_name=data.get('agent_name', ''),
            message_type=data.get('message_type', 'user'),
            message_content=data.get('message_content', ''),
            message_timestamp=message_timestamp,
            session_progress_stage=data.get('session_progress_stage'),
            created_at=created_at
        )


class SessionQuiz:
    """세션 퀴즈 정보를 관리하는 모델 클래스"""
    
    def __init__(self, quiz_id: Optional[int] = None, session_id: str = "",
                 question_number: Optional[int] = None, question_type: Optional[str] = None,
                 question_content: Optional[str] = None, user_answer: Optional[str] = None,
                 is_answer_correct: Optional[int] = None, evaluation_feedback: Optional[str] = None,
                 hint_usage_count: int = 0, created_at: Optional[datetime] = None):
        self.quiz_id = quiz_id
        self.session_id = session_id
        self.question_number = question_number
        self.question_type = question_type
        self.question_content = question_content
        self.user_answer = user_answer
        self.is_answer_correct = is_answer_correct  # 0: 틀림, 1: 맞음, None: 미평가
        self.evaluation_feedback = evaluation_feedback
        self.hint_usage_count = hint_usage_count
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'quiz_id': self.quiz_id,
            'session_id': self.session_id,
            'question_number': self.question_number,
            'question_type': self.question_type,
            'question_content': self.question_content,
            'user_answer': self.user_answer,
            'is_answer_correct': self.is_answer_correct,
            'evaluation_feedback': self.evaluation_feedback,
            'hint_usage_count': self.hint_usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionQuiz':
        """딕셔너리에서 모델 객체를 생성"""
        # datetime 문자열을 datetime 객체로 변환
        created_at = None
        
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            else:
                created_at = data['created_at']
        
        return cls(
            quiz_id=data.get('quiz_id'),
            session_id=data.get('session_id', ''),
            question_number=data.get('question_number'),
            question_type=data.get('question_type'),
            question_content=data.get('question_content'),
            user_answer=data.get('user_answer'),
            is_answer_correct=data.get('is_answer_correct'),
            evaluation_feedback=data.get('evaluation_feedback'),
            hint_usage_count=data.get('hint_usage_count', 0),
            created_at=created_at
        )