# backend/app/utils/common/graph_visualizer.py

import os
from typing import Any, Optional
from datetime import datetime


class GraphVisualizer:
    """
    LangGraph 시각화 유틸리티
    
    LangGraph 워크플로우를 이미지로 저장하고 관리하는 기능 제공
    """
    
    def __init__(self, output_dir: str = None):
        """
        GraphVisualizer 초기화
        
        Args:
            output_dir: 이미지 저장 디렉토리 (기본값: backend/data)
        """
        if output_dir is None:
            # 현재 파일 기준으로 backend/data 경로 설정
            current_dir = os.path.dirname(__file__)  # utils/common
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))  # backend
            self.output_dir = os.path.join(backend_dir, "data")
        else:
            self.output_dir = output_dir
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_graph_image(
        self, 
        graph: Any, 
        filename: str = "workflow_graph.png",
        add_timestamp: bool = False
    ) -> Optional[str]:
        """
        LangGraph를 이미지로 저장
        
        Args:
            graph: 컴파일된 LangGraph 객체
            filename: 저장할 파일명 (기본값: workflow_graph.png)
            add_timestamp: 파일명에 타임스탬프 추가 여부
            
        Returns:
            저장된 파일의 전체 경로 (실패 시 None)
        """
        try:
            # 타임스탬프 추가 옵션
            if add_timestamp:
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}{ext}"
            
            # 파일 경로 생성
            output_path = os.path.join(self.output_dir, filename)
            
            # 그래프 이미지 저장
            graph.get_graph().draw_mermaid_png(output_file_path=output_path)
            
            print(f"[GraphVisualizer] 그래프 이미지 저장 완료: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"[GraphVisualizer] 그래프 시각화 저장 실패: {e}")
            return None
    
    def save_tutor_graph(self, graph: Any) -> Optional[str]:
        """
        튜터 워크플로우 그래프 저장 (전용 메서드)
        
        Args:
            graph: 컴파일된 LangGraph 객체
            
        Returns:
            저장된 파일의 전체 경로 (실패 시 None)
        """
        return self.save_graph_image(
            graph=graph,
            filename="tutor_workflow_graph.png",
            add_timestamp=False
        )
    
    def save_graph_with_version(self, graph: Any, version: str = "v1") -> Optional[str]:
        """
        버전 정보가 포함된 그래프 저장
        
        Args:
            graph: 컴파일된 LangGraph 객체
            version: 버전 정보 (예: "v1", "v2")
            
        Returns:
            저장된 파일의 전체 경로 (실패 시 None)
        """
        return self.save_graph_image(
            graph=graph,
            filename=f"workflow_graph_{version}.png",
            add_timestamp=True
        )
    
    def list_saved_graphs(self) -> list:
        """
        저장된 그래프 이미지 목록 반환
        
        Returns:
            저장된 PNG 파일 목록
        """
        try:
            if not os.path.exists(self.output_dir):
                return []
            
            png_files = [
                f for f in os.listdir(self.output_dir) 
                if f.endswith('.png') and 'graph' in f.lower()
            ]
            
            return sorted(png_files)
            
        except Exception as e:
            print(f"[GraphVisualizer] 파일 목록 조회 실패: {e}")
            return []
    
    def get_output_directory(self) -> str:
        """
        출력 디렉토리 경로 반환
        
        Returns:
            출력 디렉토리 전체 경로
        """
        return self.output_dir
    
    def clean_old_graphs(self, keep_latest: int = 5) -> int:
        """
        오래된 그래프 이미지 정리
        
        Args:
            keep_latest: 보관할 최신 파일 개수
            
        Returns:
            삭제된 파일 개수
        """
        try:
            graph_files = self.list_saved_graphs()
            
            if len(graph_files) <= keep_latest:
                return 0
            
            # 파일 수정 시간 기준으로 정렬
            files_with_time = []
            for filename in graph_files:
                filepath = os.path.join(self.output_dir, filename)
                mtime = os.path.getmtime(filepath)
                files_with_time.append((filename, mtime))
            
            # 수정 시간 기준 내림차순 정렬 (최신 파일이 앞에)
            files_with_time.sort(key=lambda x: x[1], reverse=True)
            
            # 오래된 파일 삭제
            deleted_count = 0
            for filename, _ in files_with_time[keep_latest:]:
                filepath = os.path.join(self.output_dir, filename)
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"[GraphVisualizer] 오래된 파일 삭제: {filename}")
                except Exception as e:
                    print(f"[GraphVisualizer] 파일 삭제 실패 {filename}: {e}")
            
            return deleted_count
            
        except Exception as e:
            print(f"[GraphVisualizer] 파일 정리 중 오류: {e}")
            return 0


# 전역 시각화 인스턴스
graph_visualizer = GraphVisualizer()

def save_tutor_workflow_graph(graph: Any) -> Optional[str]:
    """
    튜터 워크플로우 그래프 저장 (편의 함수)
    
    Args:
        graph: 컴파일된 LangGraph 객체
        
    Returns:
        저장된 파일의 전체 경로 (실패 시 None)
    """
    return graph_visualizer.save_tutor_graph(graph)