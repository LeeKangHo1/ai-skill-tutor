# backend/app/models/learning/quiz.py
"""
세션 퀴즈 모델 v2.0
객관식/주관식 분리 구조와 JSON 필드를 지원합니다.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import json


class SessionQuiz:
    """세션 퀴즈 정보를 관리하는 모델 클래스 - v2.0 객관식/주관식 분리 구조"""
    
    def __init__(self, quiz_id: Optional[int] = None, session_id: Optional[int] = None,
                 # 퀴즈 기본 정보
                 quiz_type: str = "multiple_choice", quiz_content: str = "",
                 # 객관식 전용 필드
                 quiz_options: Optional[List[str]] = None, quiz_correct_answer: Optional[int] = None,
                 quiz_explanation: Optional[str] = None,
                 # 주관식 전용 필드
                 quiz_sample_answer: Optional[str] = None, quiz_evaluation_criteria: Optional[List[str]] = None,
                 # 공통 필드
                 quiz_hint: Optional[str] = None, user_answer: Optional[str] = None,
                 # 평가 결과 분리
                 multiple_answer_correct: Optional[bool] = None, subjective_answer_score: Optional[int] = None,
                 evaluation_feedback: Optional[str] = None, hint_usage_count: int = 0,
                 created_at: Optional[datetime] = None):
        self.quiz_id = quiz_id
        self.session_id = session_id  # v2.0: INT 타입으로 변경
        
        # 퀴즈 기본 정보
        self.quiz_type = quiz_type  # 'multiple_choice' 또는 'subjective'
        self.quiz_content = quiz_content
        
        # 객관식 전용 필드
        self.quiz_options = quiz_options or []  # JSON 배열
        self.quiz_correct_answer = quiz_correct_answer
        self.quiz_explanation = quiz_explanation
        
        # 주관식 전용 필드
        self.quiz_sample_answer = quiz_sample_answer
        self.quiz_evaluation_criteria = quiz_evaluation_criteria or []  # JSON 배열
        
        # 공통 필드
        self.quiz_hint = quiz_hint
        self.user_answer = user_answer
        
        # v2.0: 평가 결과 분리
        self.multiple_answer_correct = multiple_answer_correct  # 객관식: True/False
        self.subjective_answer_score = subjective_answer_score  # 주관식: 0-100 점수
        
        self.evaluation_feedback = evaluation_feedback
        self.hint_usage_count = hint_usage_count
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """모델 객체를 딕셔너리로 변환"""
        return {
            'quiz_id': self.quiz_id,
            'session_id': self.session_id,
            # 퀴즈 기본 정보
            'quiz_type': self.quiz_type,
            'quiz_content': self.quiz_content,
            # 객관식 전용 필드
            'quiz_options': self.quiz_options,
            'quiz_correct_answer': self.quiz_correct_answer,
            'quiz_explanation': self.quiz_explanation,
            # 주관식 전용 필드
            'quiz_sample_answer': self.quiz_sample_answer,
            'quiz_evaluation_criteria': self.quiz_evaluation_criteria,
            # 공통 필드
            'quiz_hint': self.quiz_hint,
            'user_answer': self.user_answer,
            # 평가 결과 분리
            'multiple_answer_correct': self.multiple_answer_correct,
            'subjective_answer_score': self.subjective_answer_score,
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
            session_id=data.get('session_id'),  # v2.0: INT 타입으로 변경
            # 퀴즈 기본 정보
            quiz_type=data.get('quiz_type', 'multiple_choice'),
            quiz_content=data.get('quiz_content', ''),
            # 객관식 전용 필드
            quiz_options=data.get('quiz_options', []),
            quiz_correct_answer=data.get('quiz_correct_answer'),
            quiz_explanation=data.get('quiz_explanation'),
            # 주관식 전용 필드
            quiz_sample_answer=data.get('quiz_sample_answer'),
            quiz_evaluation_criteria=data.get('quiz_evaluation_criteria', []),
            # 공통 필드
            quiz_hint=data.get('quiz_hint'),
            user_answer=data.get('user_answer'),
            # 평가 결과 분리
            multiple_answer_correct=data.get('multiple_answer_correct'),
            subjective_answer_score=data.get('subjective_answer_score'),
            evaluation_feedback=data.get('evaluation_feedback'),
            hint_usage_count=data.get('hint_usage_count', 0),
            created_at=created_at
        )
    
    def set_quiz_options_json(self, options: List[str]) -> None:
        """객관식 선택지를 JSON 형태로 설정 - v2.0 강화된 검증"""
        if self.quiz_type != 'multiple_choice':
            raise ValueError("객관식 퀴즈가 아닙니다")
        
        if not options or len(options) < 2:
            raise ValueError("객관식 선택지는 최소 2개 이상이어야 합니다")
        
        if len(options) > 10:
            raise ValueError("객관식 선택지는 최대 10개까지 가능합니다")
        
        # 빈 선택지 검증
        for i, option in enumerate(options):
            if not option or not option.strip():
                raise ValueError(f"선택지 {i+1}번이 비어있습니다")
        
        self.quiz_options = [option.strip() for option in options]
    
    def get_quiz_options_json(self) -> List[str]:
        """객관식 선택지를 JSON에서 파싱하여 반환 - v2.0 안전한 파싱"""
        if self.quiz_type != 'multiple_choice':
            return []
        
        if not self.quiz_options:
            return []
        
        # 문자열로 저장된 JSON을 파싱하는 경우 처리
        if isinstance(self.quiz_options, str):
            try:
                return json.loads(self.quiz_options)
            except (json.JSONDecodeError, TypeError):
                return []
        
        return self.quiz_options or []
    
    def set_evaluation_criteria_json(self, criteria: List[str]) -> None:
        """주관식 평가 기준을 JSON 형태로 설정 - v2.0 강화된 검증"""
        if self.quiz_type != 'subjective':
            raise ValueError("주관식 퀴즈가 아닙니다")
        
        if not criteria:
            raise ValueError("주관식 평가 기준은 최소 1개 이상이어야 합니다")
        
        if len(criteria) > 20:
            raise ValueError("주관식 평가 기준은 최대 20개까지 가능합니다")
        
        # 빈 기준 검증
        for i, criterion in enumerate(criteria):
            if not criterion or not criterion.strip():
                raise ValueError(f"평가 기준 {i+1}번이 비어있습니다")
        
        self.quiz_evaluation_criteria = [criterion.strip() for criterion in criteria]
    
    def get_evaluation_criteria_json(self) -> List[str]:
        """주관식 평가 기준을 JSON에서 파싱하여 반환 - v2.0 안전한 파싱"""
        if self.quiz_type != 'subjective':
            return []
        
        if not self.quiz_evaluation_criteria:
            return []
        
        # 문자열로 저장된 JSON을 파싱하는 경우 처리
        if isinstance(self.quiz_evaluation_criteria, str):
            try:
                return json.loads(self.quiz_evaluation_criteria)
            except (json.JSONDecodeError, TypeError):
                return []
        
        return self.quiz_evaluation_criteria or []
    
    def validate_quiz_type_fields(self) -> Dict[str, Any]:
        """퀴즈 타입별 필수 필드 검증 - v2.0 상세한 검증 결과 반환"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 기본 필드 검증
        if not self.quiz_content or not self.quiz_content.strip():
            validation_result['is_valid'] = False
            validation_result['errors'].append("퀴즈 내용이 비어있습니다")
        
        if self.quiz_type not in ['multiple_choice', 'subjective']:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"지원하지 않는 퀴즈 타입입니다: {self.quiz_type}")
            return validation_result
        
        if self.quiz_type == 'multiple_choice':
            # 객관식 필수 필드 검증
            if not self.quiz_options:
                validation_result['is_valid'] = False
                validation_result['errors'].append("객관식 선택지가 없습니다")
            elif len(self.quiz_options) < 2:
                validation_result['is_valid'] = False
                validation_result['errors'].append("객관식 선택지는 최소 2개 이상이어야 합니다")
            
            if self.quiz_correct_answer is None:
                validation_result['is_valid'] = False
                validation_result['errors'].append("객관식 정답 번호가 설정되지 않았습니다")
            elif self.quiz_options and not (1 <= self.quiz_correct_answer <= len(self.quiz_options)):
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"정답 번호({self.quiz_correct_answer})가 선택지 범위(1-{len(self.quiz_options)})를 벗어났습니다")
            
            # 객관식에서 주관식 필드가 설정된 경우 경고
            if self.quiz_sample_answer:
                validation_result['warnings'].append("객관식 퀴즈에 주관식 예시 답안이 설정되어 있습니다")
            if self.quiz_evaluation_criteria:
                validation_result['warnings'].append("객관식 퀴즈에 주관식 평가 기준이 설정되어 있습니다")
        
        elif self.quiz_type == 'subjective':
            # 주관식 필수 필드 검증
            if not self.quiz_sample_answer or not self.quiz_sample_answer.strip():
                validation_result['is_valid'] = False
                validation_result['errors'].append("주관식 예시 답안이 비어있습니다")
            
            # 주관식에서 객관식 필드가 설정된 경우 경고
            if self.quiz_options:
                validation_result['warnings'].append("주관식 퀴즈에 객관식 선택지가 설정되어 있습니다")
            if self.quiz_correct_answer is not None:
                validation_result['warnings'].append("주관식 퀴즈에 객관식 정답 번호가 설정되어 있습니다")
        
        return validation_result
    
    def validate_answer_score(self, score: int) -> bool:
        """주관식 답안 점수 범위 검증 (0-100)"""
        return 0 <= score <= 100
    
    def set_multiple_choice_result(self, user_answer_index: int) -> None:
        """객관식 퀴즈 결과 설정"""
        if self.quiz_type != 'multiple_choice':
            raise ValueError("객관식 퀴즈가 아닙니다")
        
        self.multiple_answer_correct = (user_answer_index == self.quiz_correct_answer)
        self.subjective_answer_score = None  # 주관식 점수는 null로 설정
    
    def set_subjective_result(self, score: int) -> None:
        """주관식 퀴즈 결과 설정"""
        if self.quiz_type != 'subjective':
            raise ValueError("주관식 퀴즈가 아닙니다")
        
        if not self.validate_answer_score(score):
            raise ValueError("주관식 점수는 0-100 범위여야 합니다")
        
        self.subjective_answer_score = score
        self.multiple_answer_correct = None  # 객관식 정답 여부는 null로 설정
    
    def prepare_for_database_insert(self) -> Dict[str, Any]:
        """데이터베이스 삽입을 위한 데이터 준비 - v2.0 JSON 직렬화"""
        data = self.to_dict()
        
        # JSON 필드를 문자열로 직렬화 (MySQL JSON 컬럼용)
        if self.quiz_options:
            data['quiz_options'] = json.dumps(self.quiz_options, ensure_ascii=False)
        else:
            data['quiz_options'] = None
        
        if self.quiz_evaluation_criteria:
            data['quiz_evaluation_criteria'] = json.dumps(self.quiz_evaluation_criteria, ensure_ascii=False)
        else:
            data['quiz_evaluation_criteria'] = None
        
        # 퀴즈 타입별 필드 정리
        if self.quiz_type == 'multiple_choice':
            # 주관식 전용 필드는 None으로 설정
            data['quiz_sample_answer'] = None
            data['quiz_evaluation_criteria'] = None
            data['subjective_answer_score'] = None
        elif self.quiz_type == 'subjective':
            # 객관식 전용 필드는 None으로 설정
            data['quiz_options'] = None
            data['quiz_correct_answer'] = None
            data['quiz_explanation'] = None
            data['multiple_answer_correct'] = None
        
        return data
    
    @classmethod
    def from_database_row(cls, row_data: Dict[str, Any]) -> 'SessionQuiz':
        """데이터베이스 행에서 모델 객체 생성 - v2.0 JSON 역직렬화"""
        # JSON 필드 역직렬화
        if row_data.get('quiz_options') and isinstance(row_data['quiz_options'], str):
            try:
                row_data['quiz_options'] = json.loads(row_data['quiz_options'])
            except (json.JSONDecodeError, TypeError):
                row_data['quiz_options'] = []
        
        if row_data.get('quiz_evaluation_criteria') and isinstance(row_data['quiz_evaluation_criteria'], str):
            try:
                row_data['quiz_evaluation_criteria'] = json.loads(row_data['quiz_evaluation_criteria'])
            except (json.JSONDecodeError, TypeError):
                row_data['quiz_evaluation_criteria'] = []
        
        return cls.from_dict(row_data)
    
    def get_quiz_summary(self) -> Dict[str, Any]:
        """퀴즈 요약 정보 반환 - v2.0 디버깅 및 로깅용"""
        summary = {
            'quiz_id': self.quiz_id,
            'session_id': self.session_id,
            'quiz_type': self.quiz_type,
            'content_length': len(self.quiz_content) if self.quiz_content else 0,
            'has_user_answer': bool(self.user_answer),
            'hint_usage_count': self.hint_usage_count
        }
        
        if self.quiz_type == 'multiple_choice':
            summary.update({
                'options_count': len(self.quiz_options) if self.quiz_options else 0,
                'correct_answer': self.quiz_correct_answer,
                'is_correct': self.multiple_answer_correct
            })
        elif self.quiz_type == 'subjective':
            summary.update({
                'criteria_count': len(self.quiz_evaluation_criteria) if self.quiz_evaluation_criteria else 0,
                'has_sample_answer': bool(self.quiz_sample_answer),
                'score': self.subjective_answer_score
            })
        
        return summary