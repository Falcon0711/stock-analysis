"""
项目检查Skill
用于在添加新模块或文件之前检查项目全局，避免冗余创建
"""

import os
import glob
from pathlib import Path
from typing import List, Dict, Tuple
import re


class ProjectCheckSkill:
    """
    项目检查技能类
    提供在创建新模块/文件前检查项目全局的功能，避免重复创建
    """
    
    def __init__(self, project_root: str = "/home/admin/clawd/daily_stock_analysis"):
        self.project_root = Path(project_root)
        
    def scan_project_files(self, patterns: List[str] = None) -> List[Path]:
        """
        扫描项目中的文件
        
        Args:
            patterns: 文件模式列表，如 ['*.py', '*.md', '*.json']
            
        Returns:
            匹配的文件路径列表
        """
        if patterns is None:
            patterns = ['*.py', '*.md', '*.json', '*.txt', '*.cfg', '*.conf']
        
        files = []
        for pattern in patterns:
            files.extend(self.project_root.rglob(pattern))
        
        return sorted(set(files))  # 去重并排序
    
    def search_content(self, search_term: str, file_extensions: List[str] = None) -> List[Tuple[Path, int, str]]:
        """
        在项目文件中搜索指定内容
        
        Args:
            search_term: 搜索词
            file_extensions: 文件扩展名列表，如 ['.py', '.md']
            
        Returns:
            匹配结果列表，每个元素为 (文件路径, 行号, 匹配行内容)
        """
        if file_extensions is None:
            file_extensions = ['.py', '.md', '.json', '.txt', '.cfg', '.conf']
        
        results = []
        
        for file_path in self.scan_project_files([f"*{ext}" for ext in file_extensions]):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if search_term.lower() in line.lower():
                                results.append((file_path, line_num, line.strip()))
                except Exception:
                    continue  # 跳过无法读取的文件
        
        return results
    
    def find_similar_content(self, content: str, threshold: int = 3) -> List[Tuple[Path, int, str, int]]:
        """
        查找与给定内容相似的内容
        
        Args:
            content: 要比较的内容
            threshold: 相似度阈值（共同单词数量）
            
        Returns:
            相似内容列表，每个元素为 (文件路径, 行号, 匹配行内容, 相似度得分)
        """
        # 将内容分割为单词集合
        content_words = set(re.findall(r'\w+', content.lower()))
        
        results = []
        
        # 扫描所有相关文件
        for file_path in self.scan_project_files(['*.py', '*.md', '*.json', '*.txt']):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            line_words = set(re.findall(r'\w+', line.lower()))
                            common_words = content_words.intersection(line_words)
                            
                            if len(common_words) >= threshold:
                                results.append((file_path, line_num, line.strip(), len(common_words)))
                except Exception:
                    continue
        
        # 按相似度得分降序排列
        results.sort(key=lambda x: x[3], reverse=True)
        return results
    
    def check_redundancy_before_creation(self, proposed_name: str, content_hint: str = None) -> Dict:
        """
        在创建新文件/模块前检查冗余
        
        Args:
            proposed_name: 提议的文件/模块名称
            content_hint: 内容提示（用于相似性检查）
            
        Returns:
            检查结果字典
        """
        result = {
            'proposed_name': proposed_name,
            'exact_matches': [],
            'similar_names': [],
            'similar_content': [],
            'recommendation': 'proceed',
            'existing_functions': []
        }
        
        # 检查确切匹配
        for file_path in self.scan_project_files():
            if proposed_name.lower() in file_path.name.lower():
                result['exact_matches'].append(str(file_path))
        
        # 检查相似名称（忽略扩展名和下划线等）
        name_pattern = re.sub(r'[_\-\.]', '', proposed_name.lower())
        for file_path in self.scan_project_files():
            file_name_clean = re.sub(r'[_\-\.]', '', file_path.stem.lower())
            if name_pattern in file_name_clean or file_name_clean in name_pattern:
                if str(file_path) not in result['exact_matches']:
                    result['similar_names'].append(str(file_path))
        
        # 如果提供了内容提示，检查相似内容
        if content_hint:
            similar_contents = self.find_similar_content(content_hint, threshold=2)
            result['similar_content'] = [(str(path), line_num, content, score) 
                                       for path, line_num, content, score in similar_contents[:10]]
        
        # 检查是否存在类似功能
        if 'skill' in proposed_name.lower() or 'analyzer' in proposed_name.lower():
            # 搜索现有的技能或分析器
            skill_matches = self.search_content(r'class.*Skill|def.*analyzer|class.*Analyzer', ['.py'])
            result['existing_functions'] = [str(path) for path, _, _ in skill_matches]
        
        # 生成建议
        issues_count = len(result['exact_matches']) + len(result['similar_names']) + len(result['similar_content'])
        if issues_count > 0:
            result['recommendation'] = 'review_before_proceeding'
        else:
            result['recommendation'] = 'proceed'
        
        return result
    
    def generate_report(self, check_result: Dict) -> str:
        """
        生成检查报告
        
        Args:
            check_result: 检查结果字典
            
        Returns:
            格式化的报告字符串
        """
        report = []
        report.append("="*60)
        report.append(f"项目冗余检查报告 - {check_result['proposed_name']}")
        report.append("="*60)
        
        if check_result['exact_matches']:
            report.append("\n🔍 发现确切匹配:")
            for match in check_result['exact_matches']:
                report.append(f"  • {match}")
        
        if check_result['similar_names']:
            report.append("\n🔍 发现相似名称:")
            for match in check_result['similar_names']:
                report.append(f"  • {match}")
        
        if check_result['similar_content']:
            report.append("\n🔍 发现相似内容:")
            for path, line_num, content, score in check_result['similar_content']:
                report.append(f"  • {path}:{line_num} (相似度: {score})")
                report.append(f"    {content[:100]}{'...' if len(content) > 100 else ''}")
        
        if check_result['existing_functions']:
            report.append("\n🔍 存在类似功能:")
            for func in check_result['existing_functions']:
                report.append(f"  • {func}")
        
        report.append(f"\n📋 建议: {check_result['recommendation']}")
        
        if check_result['recommendation'] == 'review_before_proceeding':
            report.append("⚠️  在创建前请仔细审查以上匹配项，确认是否真的需要新创建")
        else:
            report.append("✅ 未发现明显冗余，可以继续创建")
        
        report.append("="*60)
        
        return "\n".join(report)


# 便捷函数
def check_project_before_creation(proposed_name: str, content_hint: str = None, 
                                project_root: str = "/home/admin/clawd/daily_stock_analysis") -> str:
    """
    便捷函数：在创建前检查项目冗余
    
    Args:
        proposed_name: 提议的文件/模块名称
        content_hint: 内容提示
        project_root: 项目根目录
        
    Returns:
        检查报告字符串
    """
    checker = ProjectCheckSkill(project_root)
    result = checker.check_redundancy_before_creation(proposed_name, content_hint)
    return checker.generate_report(result)


def scan_project_content(search_term: str, project_root: str = "/home/admin/clawd/daily_stock_analysis") -> List[Tuple[str, int, str]]:
    """
    便捷函数：搜索项目内容
    
    Args:
        search_term: 搜索词
        project_root: 项目根目录
        
    Returns:
        搜索结果列表
    """
    checker = ProjectCheckSkill(project_root)
    results = checker.search_content(search_term)
    return [(str(path), line_num, content) for path, line_num, content in results]


def find_existing_skills(project_root: str = "/home/admin/clawd/daily_stock_analysis") -> List[str]:
    """
    便捷函数：查找现有技能模块
    
    Args:
        project_root: 项目根目录
        
    Returns:
        现有技能模块列表
    """
    checker = ProjectCheckSkill(project_root)
    results = checker.search_content(r'class.*Skill|def.*skill', ['.py'])
    return list(set([str(path) for path, _, _ in results]))  # 去重