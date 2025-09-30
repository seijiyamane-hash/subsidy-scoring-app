import re
import math
from datetime import datetime
from typing import Dict, List, Any, Optional

class SmallBusinessScoringEngine:
    """小規模事業者持続化補助金の採点エンジン"""
    
    def __init__(self):
        self.scoring_criteria = self._initialize_scoring_criteria()
        self.bonus_criteria = self._initialize_bonus_criteria()
        
    def _initialize_scoring_criteria(self) -> Dict[str, Any]:
        """採点基準の初期化"""
        return {
            '経営状況分析の妥当性': {
                'max_score': 25,
                'weight': 0.25,
                'sub_criteria': {
                    '企業概要の充実度': {'weight': 0.3, 'keywords': ['事業内容', '創業', '沿革', '従業員', '売上', '顧客']},
                    '売上・財務分析': {'weight': 0.3, 'keywords': ['売上高', '利益', '推移', '増減', '要因', '財務']},
                    '強み・弱み分析': {'weight': 0.25, 'keywords': ['強み', '弱み', '特徴', '優位性', '課題', '問題']},
                    '市場・競合認識': {'weight': 0.15, 'keywords': ['市場', '競合', '業界', '動向', 'ライバル', 'シェア']}
                }
            },
            '経営方針・目標の適切性': {
                'max_score': 25,
                'weight': 0.25,
                'sub_criteria': {
                    '経営方針の明確性': {'weight': 0.3, 'keywords': ['方針', '理念', 'ビジョン', '目標', '戦略']},
                    '数値目標の具体性': {'weight': 0.4, 'keywords': ['売上目標', '集客', '単価', '年度', '増加', '○○円', '○○人']},
                    '市場・顧客対応': {'weight': 0.2, 'keywords': ['顧客ニーズ', '市場動向', 'ターゲット', '需要']},
                    '実現可能性': {'weight': 0.1, 'keywords': ['計画', '段階', 'ステップ', '期間', '実施']}
                }
            },
            '補助事業計画の有効性': {
                'max_score': 30,
                'weight': 0.3,
                'sub_criteria': {
                    '事業計画の具体性': {'weight': 0.3, 'keywords': ['具体的', '詳細', '内容', '方法', '手順']},
                    '販路開拓の有効性': {'weight': 0.25, 'keywords': ['販路', '新規', '開拓', '顧客獲得', 'PR', '宣伝']},
                    '新規性・独自性': {'weight': 0.2, 'keywords': ['新たな', '独自', '他社にない', '差別化', '特色']},
                    'デジタル活用': {'weight': 0.15, 'keywords': ['デジタル', 'IT', 'ホームページ', 'SNS', 'システム', 'DX']},
                    '効果・成果予測': {'weight': 0.1, 'keywords': ['効果', '成果', '売上増', '集客増', '効率化']}
                }
            },
            '積算の透明・適切性': {
                'max_score': 20,
                'weight': 0.2,
                'sub_criteria': {
                    '経費明細の妥当性': {'weight': 0.4, 'keywords': ['経費', '明細', '内訳', '単価', '数量']},
                    '必要性の説明': {'weight': 0.3, 'keywords': ['必要', '理由', '根拠', '効果', '目的']},
                    '計算の正確性': {'weight': 0.2, 'keywords': ['合計', '計算', '金額', '×', '円']},
                    '補助対象適合性': {'weight': 0.1, 'keywords': ['補助対象', '対象経費', '適用']}
                }
            }
        }
    
    def _initialize_bonus_criteria(self) -> Dict[str, Any]:
        """加点基準の初期化"""
        return {
            'priority_bonus': {
                '赤字賃上げ加点': {'keywords': ['赤字', '賃上げ', '賃金引上げ'], 'points': 5},
                '事業環境変化加点': {'keywords': ['物価高騰', 'コロナ', '環境変化', '影響'], 'points': 5},
                '東日本大震災加点': {'keywords': ['震災', '被災', '復興'], 'points': 3},
                'くるみん・えるぼし加点': {'keywords': ['くるみん', 'えるぼし', '女性活躍'], 'points': 3}
            },
            'policy_bonus': {
                '賃金引上げ加点': {'keywords': ['賃上げ', '30円', '時給', '昇給'], 'points': 3},
                '地方創生型加点': {'keywords': ['地域資源', '地方創生', '地域活性化'], 'points': 3},
                '経営力向上計画加点': {'keywords': ['経営力向上計画', '認定'], 'points': 2},
                '事業承継加点': {'keywords': ['事業承継', '後継者', '60歳'], 'points': 3},
                '過疎地域加点': {'keywords': ['過疎地域'], 'points': 2}
            }
        }
    
    def score_application(self, document_analysis: Dict[str, Any], strict_mode: bool = True) -> Dict[str, Any]:
        """申請書の採点を実行"""
        try:
            # 基礎審査
            basic_check = self._check_basic_requirements(document_analysis)
            
            if not basic_check['passed']:
                return {
                    'total_score': 0,
                    'evaluation_level': '不適格',
                    'adoption_probability': 0,
                    'basic_requirements_passed': False,
                    'detailed_scores': {},
                    'improvements': basic_check['improvements'],
                    'bonus_points': 0,
                    'error': '基礎審査で必須要件を満たしていません'
                }
            
            # 計画審査
            detailed_scores = self._score_detailed_criteria(document_analysis, strict_mode)
            
            # 加点審査
            bonus_analysis = self._analyze_bonus_points(document_analysis)
            bonus_points = bonus_analysis['total_points']
            
            # 総合スコア計算
            base_score = sum(score_info['score'] for score_info in detailed_scores.values())
            total_score = min(100, base_score + bonus_points)
            
            # 厳格モードでの調整
            if strict_mode:
                total_score = self._apply_strict_adjustment(total_score, document_analysis)
            
            # 評価レベル決定
            evaluation_level = self._determine_evaluation_level(total_score)
            adoption_probability = self._calculate_adoption_probability(total_score, bonus_points)
            
            # 改善提案生成
            improvements = self._generate_improvements(detailed_scores, document_analysis)
            
            return {
                'total_score': total_score,
                'evaluation_level': evaluation_level,
                'adoption_probability': adoption_probability,
                'basic_requirements_passed': True,
                'detailed_scores': detailed_scores,
                'improvements': improvements,
                'bonus_points': bonus_points,
                'bonus_analysis': bonus_analysis,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"採点処理でエラーが発生しました: {str(e)}",
                'total_score': 0,
                'evaluation_level': 'エラー',
                'adoption_probability': 0
            }
    
    def _check_basic_requirements(self, document_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """基礎審査チェック"""
        issues = []
        passed = True
        
        text_content = document_analysis.get('text_content', '')
        
        # 必須項目チェック
        required_items = [
            ('企業概要', ['事業内容', '業種', '従業員']),
            ('売上情報', ['売上', '売上高', '利益']),
            ('経営方針', ['方針', '目標', '計画']),
            ('補助事業計画', ['補助事業', '計画', '内容'])
        ]
        
        for item_name, keywords in required_items:
            if not any(keyword in text_content for keyword in keywords):
                issues.append({
                    'item': f'{item_name}の記載不足',
                    'priority': '緊急',
                    'current_issue': f'{item_name}に関する記載が見つかりません',
                    'improvement_method': f'{item_name}の詳細な記載を追加してください',
                    'example': f'{item_name}について具体的な内容を記載する必要があります'
                })
                passed = False
        
        return {'passed': passed, 'improvements': issues}
    
    def _score_detailed_criteria(self, document_analysis: Dict[str, Any], strict_mode: bool) -> Dict[str, Dict]:
        """詳細な採点基準による評価"""
        detailed_scores = {}
        text_content = document_analysis.get('text_content', '').lower()
        
        for criterion_name, criterion_info in self.scoring_criteria.items():
            max_score = criterion_info['max_score']
            sub_scores = []
            
            for sub_name, sub_info in criterion_info['sub_criteria'].items():
                # キーワードマッチング
                keyword_matches = sum(1 for keyword in sub_info['keywords'] if keyword in text_content)
                keyword_score = min(1.0, keyword_matches / len(sub_info['keywords']) * 1.5)
                
                # 文書品質評価
                quality_score = self._evaluate_content_quality(text_content, sub_info['keywords'])
                
                # 具体性評価
                specificity_score = self._evaluate_specificity(text_content, sub_info['keywords'])
                
                # サブスコア計算
                sub_score = (keyword_score * 0.4 + quality_score * 0.3 + specificity_score * 0.3) * sub_info['weight']
                sub_scores.append(sub_score)
            
            # 基準スコア計算
            base_score = sum(sub_scores) * max_score
            
            # 厳格モード調整
            if strict_mode:
                base_score *= 0.8  # 20%厳格化
            
            detailed_scores[criterion_name] = {
                'score': round(base_score, 1),
                'max_score': max_score,
                'sub_scores': sub_scores
            }
        
        return detailed_scores
    
    def _evaluate_content_quality(self, text: str, keywords: List[str]) -> float:
        """コンテンツ品質の評価"""
        quality_score = 0.0
        
        # 文章量チェック
        if len(text) > 500:
            quality_score += 0.2
        if len(text) > 1000:
            quality_score += 0.2
        
        # 数値データの存在
        if re.search(r'\d+[万億千百十]?円|\d+[万千百十]?人|\d+%|\d+年', text):
            quality_score += 0.3
        
        # 具体的な表現
        concrete_patterns = ['具体的に', '詳細', '明確', '○○', 'について', 'により']
        concrete_matches = sum(1 for pattern in concrete_patterns if pattern in text)
        quality_score += min(0.3, concrete_matches / len(concrete_patterns))
        
        return min(1.0, quality_score)
    
    def _evaluate_specificity(self, text: str, keywords: List[str]) -> float:
        """具体性の評価"""
        specificity_score = 0.0
        
        # 数値の具体性
        numeric_patterns = [
            r'\d+年\d+月',  # 具体的な日付
            r'\d+[万億千]円',  # 具体的な金額
            r'\d+[万千]人',  # 具体的な人数
            r'\d+%',  # 具体的な割合
            r'\d+回',  # 具体的な回数
        ]
        
        for pattern in numeric_patterns:
            if re.search(pattern, text):
                specificity_score += 0.2
        
        return min(1.0, specificity_score)
    
    def _analyze_bonus_points(self, document_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """加点項目の分析"""
        text_content = document_analysis.get('text_content', '').lower()
        total_points = 0
        priority_bonuses = []
        policy_bonuses = []
        
        # 重点政策加点
        for bonus_name, bonus_info in self.bonus_criteria['priority_bonus'].items():
            eligible = any(keyword in text_content for keyword in bonus_info['keywords'])
            if eligible:
                total_points += bonus_info['points']
            
            priority_bonuses.append({
                'name': bonus_name,
                'eligible': eligible,
                'points': bonus_info['points'] if eligible else 0,
                'requirements': f"以下のキーワードに関する記載: {', '.join(bonus_info['keywords'])}"
            })
        
        # 政策加点
        for bonus_name, bonus_info in self.bonus_criteria['policy_bonus'].items():
            eligible = any(keyword in text_content for keyword in bonus_info['keywords'])
            if eligible:
                total_points += bonus_info['points']
            
            policy_bonuses.append({
                'name': bonus_name,
                'eligible': eligible,
                'points': bonus_info['points'] if eligible else 0,
                'requirements': f"以下のキーワードに関する記載: {', '.join(bonus_info['keywords'])}"
            })
        
        return {
            'total_points': total_points,
            'priority_bonuses': priority_bonuses,
            'policy_bonuses': policy_bonuses
        }
    
    def _apply_strict_adjustment(self, score: float, document_analysis: Dict[str, Any]) -> float:
        """厳格モードでの調整"""
        text_length = len(document_analysis.get('text_content', ''))
        
        # 文章量による調整
        if text_length < 500:
            score *= 0.7
        elif text_length < 1000:
            score *= 0.85
        
        # 具体性による調整
        text_content = document_analysis.get('text_content', '').lower()
        if not re.search(r'\d+[万億千]円|\d+[万千]人', text_content):
            score *= 0.9
        
        return round(score, 1)
    
    def _determine_evaluation_level(self, score: float) -> str:
        """評価レベルの決定"""
        if score >= 80:
            return '優秀'
        elif score >= 65:
            return '良好'
        elif score >= 50:
            return '普通'
        elif score >= 35:
            return '不十分'
        else:
            return '不適格'
    
    def _calculate_adoption_probability(self, score: float, bonus_points: float) -> float:
        """採択可能性の計算"""
        # 基本確率
        if score >= 80:
            base_probability = 85
        elif score >= 70:
            base_probability = 70
        elif score >= 60:
            base_probability = 50
        elif score >= 50:
            base_probability = 30
        else:
            base_probability = 10
        
        # 加点による調整
        bonus_adjustment = bonus_points * 2
        
        # 最終確率
        final_probability = min(95, base_probability + bonus_adjustment)
        
        return round(final_probability, 1)
    
    def _generate_improvements(self, detailed_scores: Dict[str, Dict], document_analysis: Dict[str, Any]) -> List[Dict]:
        """具体的な改善提案を生成"""
        improvements = []
        text_content = document_analysis.get('text_content', '').lower()
        
        # 各評価軸の改善提案
        improvement_templates = {
            '経営状況分析の妥当性': {
                'low_threshold': 18,
                'improvements': [
                    {
                        'item': '企業概要の詳細化',
                        'current_issue': '事業内容や特徴の説明が不十分',
                        'improvement_method': '創業年、従業員数、主要商品・サービス、事業規模を具体的に記載',
                        'example': '「創業○年、従業員○名の○○業。主力商品は○○で、年間売上○○万円」'
                    },
                    {
                        'item': '売上・財務分析の強化',
                        'current_issue': '売上推移や財務状況の分析が表面的',
                        'improvement_method': '過去3年間の売上推移を表形式で示し、増減要因を具体的に分析',
                        'example': '「2022年:○○万円→2023年:○○万円→2024年:○○万円。増加要因は○○」'
                    },
                    {
                        'item': '強み・弱みの明確化',
                        'current_issue': '自社の強み・弱みの分析が抽象的',
                        'improvement_method': '競合他社との比較を含めた客観的な強み・弱み分析',
                        'example': '「強み:他社にない○○技術、弱み:認知度不足(市場シェア○%)」'
                    }
                ]
            },
            '経営方針・目標の適切性': {
                'low_threshold': 18,
                'improvements': [
                    {
                        'item': '数値目標の具体化',
                        'current_issue': '売上目標や集客目標が曖昧',
                        'improvement_method': '年度別の具体的な数値目標を表形式で設定',
                        'example': '「2025年:売上○○万円(前年比○%増)、新規顧客○○人獲得」'
                    },
                    {
                        'item': '市場・顧客分析の深化',
                        'current_issue': 'ターゲット顧客や市場動向の分析が不足',
                        'improvement_method': '統計データを活用した市場規模・成長性・顧客特性の分析',
                        'example': '「○○市場規模○○億円、年成長率○%。主要顧客層は○○代○○」'
                    }
                ]
            },
            '補助事業計画の有効性': {
                'low_threshold': 22,
                'improvements': [
                    {
                        'item': '事業計画の具体化',
                        'current_issue': '補助事業の内容や手順が抽象的',
                        'improvement_method': '実施時期、実施方法、担当者を含む詳細な実行計画',
                        'example': '「○月:ホームページ制作開始、○月:完成・公開、担当:○○」'
                    },
                    {
                        'item': '販路開拓効果の明確化',
                        'current_issue': '販路開拓による効果の予測が不明確',
                        'improvement_method': '新規顧客獲得数、売上増加額を具体的に予測',
                        'example': '「HP経由で月○○件の問い合わせ、○○万円の売上増を見込む」'
                    },
                    {
                        'item': 'デジタル活用の強化',
                        'current_issue': 'デジタル技術の活用が限定的',
                        'improvement_method': 'SNS、ECサイト、顧客管理システム等の具体的活用計画',
                        'example': '「Instagram活用で若年層開拓、月○○投稿で○○フォロワー獲得目標」'
                    }
                ]
            },
            '積算の透明・適切性': {
                'low_threshold': 15,
                'improvements': [
                    {
                        'item': '経費明細の詳細化',
                        'current_issue': '経費の内訳や単価が不明確',
                        'improvement_method': '見積書を取得し、単価×数量の詳細な明細を作成',
                        'example': '「ホームページ制作 ○○円、保守費用 ○○円/年」'
                    },
                    {
                        'item': '必要性の根拠強化',
                        'current_issue': '各経費の必要性の説明が不十分',
                        'improvement_method': '各経費がなぜ必要か、どのような効果があるかを具体的に説明',
                        'example': '「○○導入により業務効率○%向上、年間○○時間削減効果」'
                    }
                ]
            }
        }
        
        # 各評価軸をチェックして改善提案を追加
        for criterion_name, score_info in detailed_scores.items():
            if criterion_name in improvement_templates:
                template = improvement_templates[criterion_name]
                if score_info['score'] < template['low_threshold']:
                    for improvement in template['improvements']:
                        improvement['priority'] = '重要' if score_info['score'] < template['low_threshold'] * 0.7 else '推奨'
                        improvements.append(improvement)
        
        # 全体的な改善提案
        if not re.search(r'\d+[万億千]円', text_content):
            improvements.append({
                'item': '数値データの充実',
                'priority': '重要',
                'current_issue': '具体的な金額や数量の記載が不足',
                'improvement_method': '売上、経費、目標値等を具体的な数値で記載',
                'example': '「現在の月商○○万円を○○万円に増加させる計画」'
            })
        
        if len(text_content) < 1000:
            improvements.append({
                'item': '記載内容の充実',
                'priority': '推奨',
                'current_issue': '全体的な記載量が不足している可能性',
                'improvement_method': '各項目について、より詳細で具体的な内容を記載',
                'example': '背景、現状、課題、解決策、効果を段階的に詳述'
            })
        
        return improvements