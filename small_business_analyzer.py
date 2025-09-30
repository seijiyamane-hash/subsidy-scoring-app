import PyPDF2
import re
from typing import Dict, List, Any, Optional
import io

class SmallBusinessAnalyzer:
    """小規模事業者持続化補助金申請書類の解析クラス"""
    
    def __init__(self):
        self.analysis_patterns = self._initialize_analysis_patterns()
    
    def _initialize_analysis_patterns(self) -> Dict[str, Any]:
        """解析パターンの初期化"""
        return {
            'company_info': {
                'patterns': [
                    r'(株式会社|有限会社|合同会社|個人事業主).*?([^\s]+)',
                    r'代表者.*?([^\s]+)',
                    r'従業員.*?(\d+).*?人',
                    r'資本金.*?(\d+).*?万円',
                    r'設立.*?(\d{4})年',
                    r'売上.*?(\d+).*?(万円|千円|億円)'
                ]
            },
            'business_content': {
                'keywords': [
                    '事業内容', '業種', '主力商品', 'サービス', '営業', '製造',
                    '販売', '顧客', '市場', '地域', '特徴', '強み'
                ]
            },
            'financial_data': {
                'patterns': [
                    r'売上.*?(\d{1,3}(?:,\d{3})*|\d+).*?(万円|千円|億円)',
                    r'利益.*?(\d{1,3}(?:,\d{3})*|\d+).*?(万円|千円|億円)',
                    r'(\d{4})年.*?(\d{1,3}(?:,\d{3})*|\d+).*?(万円|千円|億円)',
                    r'前年比.*?(\d+).*?%',
                    r'増加.*?(\d+).*?%',
                    r'減少.*?(\d+).*?%'
                ]
            },
            'market_analysis': {
                'keywords': [
                    '市場', '競合', '顧客ニーズ', '業界動向', 'ライバル', 'シェア',
                    '需要', '供給', 'トレンド', '成長', '縮小', '変化'
                ]
            },
            'strengths_weaknesses': {
                'keywords': [
                    '強み', '弱み', '優位性', '特徴', '差別化', '課題', '問題点',
                    '改善', '解決', '対策', '独自', '他社にない'
                ]
            },
            'business_plan': {
                'keywords': [
                    '計画', '目標', '方針', '戦略', '取組', '実施', '予定',
                    '新規', '開拓', '拡大', '改善', '効率', 'デジタル'
                ]
            },
            'subsidy_plan': {
                'keywords': [
                    '補助事業', '販路開拓', '業務効率', 'ホームページ', 'チラシ',
                    '看板', '設備', '機械', 'システム', '広告', 'PR'
                ]
            },
            'cost_breakdown': {
                'patterns': [
                    r'(\w+).*?(\d{1,3}(?:,\d{3})*|\d+).*?円',
                    r'合計.*?(\d{1,3}(?:,\d{3})*|\d+).*?円',
                    r'補助.*?(\d{1,3}(?:,\d{3})*|\d+).*?円',
                    r'自己資金.*?(\d{1,3}(?:,\d{3})*|\d+).*?円'
                ]
            },
            'bonus_indicators': {
                'keywords': [
                    '赤字', '賃上げ', '賃金引上げ', '物価高騰', 'コロナ', '震災',
                    '地域資源', '地方創生', '経営力向上', '事業承継', '後継者',
                    'くるみん', 'えるぼし', '過疎地域'
                ]
            }
        }
    
    def analyze_pdf(self, uploaded_file) -> Dict[str, Any]:
        """PDFファイルの解析"""
        try:
            # PDFからテキストを抽出
            text_content = self._extract_text_from_pdf(uploaded_file)
            
            if not text_content:
                return {
                    'success': False,
                    'error': 'PDFからテキストを抽出できませんでした',
                    'text_content': ''
                }
            
            # 各項目の解析
            analysis_result = {
                'success': True,
                'text_content': text_content,
                'extracted_length': len(text_content),
                'company_info': self._extract_company_info(text_content),
                'financial_data': self._extract_financial_data(text_content),
                'market_analysis': self._analyze_market_content(text_content),
                'strengths_weaknesses': self._analyze_strengths_weaknesses(text_content),
                'business_plan': self._analyze_business_plan(text_content),
                'subsidy_plan': self._analyze_subsidy_plan(text_content),
                'cost_breakdown': self._extract_cost_breakdown(text_content),
                'bonus_indicators': self._detect_bonus_indicators(text_content),
                'content_quality': self._assess_content_quality(text_content),
                'completeness_score': self._calculate_completeness(text_content)
            }
            
            return analysis_result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'PDF解析中にエラーが発生しました: {str(e)}',
                'text_content': ''
            }
    
    def _extract_text_from_pdf(self, uploaded_file) -> str:
        """PDFからテキストを抽出"""
        try:
            # ファイルポインタを先頭に戻す
            uploaded_file.seek(0)
            
            # PDFファイルを読み込み
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_content = ""
            
            # 全ページからテキストを抽出
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"
            
            # テキストのクリーニング
            text_content = self._clean_text(text_content)
            
            return text_content
            
        except Exception as e:
            raise Exception(f"PDFテキスト抽出エラー: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """抽出したテキストのクリーニング"""
        # 改行の正規化
        text = re.sub(r'\n+', '\n', text)
        
        # 不要な空白の除去
        text = re.sub(r' +', ' ', text)
        
        # 制御文字の除去
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    def _extract_company_info(self, text: str) -> Dict[str, Any]:
        """企業情報の抽出"""
        company_info = {
            'company_name': None,
            'representative': None,
            'employees': None,
            'capital': None,
            'established': None,
            'sales': []
        }
        
        # 会社名
        company_pattern = r'(株式会社|有限会社|合同会社|個人事業主)\s*([^\s\n]+)'
        company_match = re.search(company_pattern, text)
        if company_match:
            company_info['company_name'] = company_match.group(1) + company_match.group(2)
        
        # 代表者
        rep_pattern = r'代表者.*?([^\s\n]+)'
        rep_match = re.search(rep_pattern, text)
        if rep_match:
            company_info['representative'] = rep_match.group(1)
        
        # 従業員数
        emp_pattern = r'従業員.*?(\d+).*?人'
        emp_match = re.search(emp_pattern, text)
        if emp_match:
            company_info['employees'] = int(emp_match.group(1))
        
        # 資本金
        capital_pattern = r'資本金.*?(\d+).*?万円'
        capital_match = re.search(capital_pattern, text)
        if capital_match:
            company_info['capital'] = int(capital_match.group(1))
        
        # 設立年
        est_pattern = r'設立.*?(\d{4})年'
        est_match = re.search(est_pattern, text)
        if est_match:
            company_info['established'] = int(est_match.group(1))
        
        # 売上情報
        sales_patterns = [
            r'(\d{4})年.*?売上.*?(\d{1,3}(?:,\d{3})*|\d+).*?(万円|千円|億円)',
            r'売上.*?(\d{1,3}(?:,\d{3})*|\d+).*?(万円|千円|億円)'
        ]
        
        for pattern in sales_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 3:  # 年度付き
                    company_info['sales'].append({
                        'year': int(match[0]),
                        'amount': match[1].replace(',', ''),
                        'unit': match[2]
                    })
                else:  # 年度なし
                    company_info['sales'].append({
                        'amount': match[0].replace(',', ''),
                        'unit': match[1]
                    })
        
        return company_info
    
    def _extract_financial_data(self, text: str) -> Dict[str, Any]:
        """財務データの抽出"""
        financial_data = {
            'sales_history': [],
            'profit_data': [],
            'growth_rates': [],
            'financial_indicators': []
        }
        
        # 売上履歴
        sales_pattern = r'(\d{4})年.*?(\d{1,3}(?:,\d{3})*|\d+).*?(万円|千円|億円)'
        sales_matches = re.findall(sales_pattern, text)
        for match in sales_matches:
            financial_data['sales_history'].append({
                'year': int(match[0]),
                'amount': match[1].replace(',', ''),
                'unit': match[2]
            })
        
        # 利益データ
        profit_pattern = r'利益.*?(\d{1,3}(?:,\d{3})*|\d+).*?(万円|千円|億円)'
        profit_matches = re.findall(profit_pattern, text)
        for match in profit_matches:
            financial_data['profit_data'].append({
                'amount': match[0].replace(',', ''),
                'unit': match[1]
            })
        
        # 成長率
        growth_pattern = r'(前年比|増加|減少|成長).*?(\d+).*?%'
        growth_matches = re.findall(growth_pattern, text)
        for match in growth_matches:
            financial_data['growth_rates'].append({
                'type': match[0],
                'rate': float(match[1])
            })
        
        return financial_data
    
    def _analyze_market_content(self, text: str) -> Dict[str, Any]:
        """市場分析内容の解析"""
        market_keywords = self.analysis_patterns['market_analysis']['keywords']
        
        market_content = {
            'keyword_matches': [],
            'market_size_mentions': [],
            'competitor_analysis': False,
            'customer_needs': False,
            'market_trends': False
        }
        
        text_lower = text.lower()
        
        # キーワードマッチング
        for keyword in market_keywords:
            if keyword in text_lower:
                market_content['keyword_matches'].append(keyword)
        
        # 市場規模言及
        market_size_pattern = r'市場.*?(\d+).*?(億円|万円|兆円)'
        market_size_matches = re.findall(market_size_pattern, text)
        market_content['market_size_mentions'] = market_size_matches
        
        # 競合分析の有無
        competitor_keywords = ['競合', 'ライバル', '他社', '同業']
        market_content['competitor_analysis'] = any(kw in text_lower for kw in competitor_keywords)
        
        # 顧客ニーズ分析の有無
        customer_keywords = ['顧客ニーズ', 'お客様', '利用者', 'ユーザー']
        market_content['customer_needs'] = any(kw in text_lower for kw in customer_keywords)
        
        # 市場トレンド分析の有無
        trend_keywords = ['トレンド', '動向', '変化', '成長', '拡大']
        market_content['market_trends'] = any(kw in text_lower for kw in trend_keywords)
        
        return market_content
    
    def _analyze_strengths_weaknesses(self, text: str) -> Dict[str, Any]:
        """強み・弱み分析"""
        strengths_weaknesses = {
            'strengths_mentioned': [],
            'weaknesses_mentioned': [],
            'differentiation': False,
            'competitive_advantage': False
        }
        
        text_lower = text.lower()
        
        # 強みの検出
        strength_keywords = ['強み', '優位性', '特徴', '差別化', '独自', '他社にない']
        for keyword in strength_keywords:
            if keyword in text_lower:
                strengths_weaknesses['strengths_mentioned'].append(keyword)
        
        # 弱みの検出
        weakness_keywords = ['弱み', '課題', '問題', '改善', '不足']
        for keyword in weakness_keywords:
            if keyword in text_lower:
                strengths_weaknesses['weaknesses_mentioned'].append(keyword)
        
        # 差別化要素
        diff_keywords = ['差別化', '独自', '他社との違い', 'オリジナル']
        strengths_weaknesses['differentiation'] = any(kw in text_lower for kw in diff_keywords)
        
        # 競争優位性
        advantage_keywords = ['優位性', 'アドバンテージ', '競争力', '強み']
        strengths_weaknesses['competitive_advantage'] = any(kw in text_lower for kw in advantage_keywords)
        
        return strengths_weaknesses
    
    def _analyze_business_plan(self, text: str) -> Dict[str, Any]:
        """事業計画の解析"""
        business_plan = {
            'goals_mentioned': [],
            'numerical_targets': [],
            'timeline': [],
            'strategies': [],
            'implementation_plan': False
        }
        
        text_lower = text.lower()
        
        # 目標の検出
        goal_keywords = ['目標', '計画', '予定', '方針', '戦略']
        for keyword in goal_keywords:
            if keyword in text_lower:
                business_plan['goals_mentioned'].append(keyword)
        
        # 数値目標
        numerical_pattern = r'(売上|顧客|集客|利益).*?(\d+).*?(万円|千円|億円|人|件)'
        numerical_matches = re.findall(numerical_pattern, text)
        business_plan['numerical_targets'] = numerical_matches
        
        # タイムライン
        timeline_pattern = r'(\d{4})年|(\d+)月|(\d+)年後'
        timeline_matches = re.findall(timeline_pattern, text)
        business_plan['timeline'] = [match for match in timeline_matches if any(match)]
        
        # 実施計画の詳細度
        implementation_keywords = ['実施', '開始', '完了', '段階', 'ステップ', 'スケジュール']
        business_plan['implementation_plan'] = any(kw in text_lower for kw in implementation_keywords)
        
        return business_plan
    
    def _analyze_subsidy_plan(self, text: str) -> Dict[str, Any]:
        """補助事業計画の解析"""
        subsidy_plan = {
            'subsidy_items': [],
            'sales_development': False,
            'efficiency_improvement': False,
            'digital_utilization': False,
            'expected_effects': []
        }
        
        text_lower = text.lower()
        
        # 補助事業項目
        subsidy_keywords = self.analysis_patterns['subsidy_plan']['keywords']
        for keyword in subsidy_keywords:
            if keyword in text_lower:
                subsidy_plan['subsidy_items'].append(keyword)
        
        # 販路開拓
        sales_keywords = ['販路', '新規', '開拓', '顧客獲得', '営業']
        subsidy_plan['sales_development'] = any(kw in text_lower for kw in sales_keywords)
        
        # 業務効率化
        efficiency_keywords = ['効率', '省力', '自動', '時短', '合理化']
        subsidy_plan['efficiency_improvement'] = any(kw in text_lower for kw in efficiency_keywords)
        
        # デジタル活用
        digital_keywords = ['デジタル', 'it', 'ホームページ', 'sns', 'システム', 'dx']
        subsidy_plan['digital_utilization'] = any(kw in text_lower for kw in digital_keywords)
        
        # 期待効果
        effect_pattern = r'効果.*?(\d+).*?(万円|人|件|%)'
        effect_matches = re.findall(effect_pattern, text)
        subsidy_plan['expected_effects'] = effect_matches
        
        return subsidy_plan
    
    def _extract_cost_breakdown(self, text: str) -> Dict[str, Any]:
        """経費明細の抽出"""
        cost_breakdown = {
            'total_cost': None,
            'subsidy_amount': None,
            'self_funding': None,
            'cost_items': []
        }
        
        # 合計金額
        total_pattern = r'合計.*?(\d{1,3}(?:,\d{3})*|\d+).*?円'
        total_match = re.search(total_pattern, text)
        if total_match:
            cost_breakdown['total_cost'] = total_match.group(1).replace(',', '')
        
        # 補助金額
        subsidy_pattern = r'補助.*?(\d{1,3}(?:,\d{3})*|\d+).*?円'
        subsidy_match = re.search(subsidy_pattern, text)
        if subsidy_match:
            cost_breakdown['subsidy_amount'] = subsidy_match.group(1).replace(',', '')
        
        # 自己資金
        self_fund_pattern = r'自己.*?(\d{1,3}(?:,\d{3})*|\d+).*?円'
        self_fund_match = re.search(self_fund_pattern, text)
        if self_fund_match:
            cost_breakdown['self_funding'] = self_fund_match.group(1).replace(',', '')
        
        # 個別経費項目
        cost_item_pattern = r'([^\d\n]+?)(\d{1,3}(?:,\d{3})*|\d+).*?円'
        cost_items = re.findall(cost_item_pattern, text)
        cost_breakdown['cost_items'] = [
            {'item': item[0].strip(), 'amount': item[1].replace(',', '')}
            for item in cost_items
        ]
        
        return cost_breakdown
    
    def _detect_bonus_indicators(self, text: str) -> Dict[str, Any]:
        """加点指標の検出"""
        bonus_indicators = {
            'detected_bonuses': [],
            'priority_bonus': False,
            'policy_bonus': False
        }
        
        text_lower = text.lower()
        bonus_keywords = self.analysis_patterns['bonus_indicators']['keywords']
        
        for keyword in bonus_keywords:
            if keyword in text_lower:
                bonus_indicators['detected_bonuses'].append(keyword)
        
        # 重点政策加点
        priority_keywords = ['赤字', '賃上げ', '物価高騰', 'コロナ', '震災']
        bonus_indicators['priority_bonus'] = any(kw in text_lower for kw in priority_keywords)
        
        # 政策加点
        policy_keywords = ['地域資源', '地方創生', '経営力向上', '事業承継']
        bonus_indicators['policy_bonus'] = any(kw in text_lower for kw in policy_keywords)
        
        return bonus_indicators
    
    def _assess_content_quality(self, text: str) -> Dict[str, Any]:
        """コンテンツ品質の評価"""
        quality_assessment = {
            'text_length': len(text),
            'paragraph_count': len(text.split('\n\n')),
            'numerical_data_count': len(re.findall(r'\d+', text)),
            'concrete_expressions': 0,
            'quality_score': 0.0
        }
        
        # 具体的表現のカウント
        concrete_patterns = [
            r'具体的に',
            r'詳細',
            r'\d+年\d+月',
            r'\d+[万億千]円',
            r'\d+人'
        ]
        
        for pattern in concrete_patterns:
            quality_assessment['concrete_expressions'] += len(re.findall(pattern, text))
        
        # 品質スコア計算
        length_score = min(1.0, len(text) / 2000)  # 2000文字を満点とする
        numerical_score = min(1.0, quality_assessment['numerical_data_count'] / 20)  # 20個の数値データを満点とする
        concrete_score = min(1.0, quality_assessment['concrete_expressions'] / 10)  # 10個の具体的表現を満点とする
        
        quality_assessment['quality_score'] = (length_score + numerical_score + concrete_score) / 3
        
        return quality_assessment
    
    def _calculate_completeness(self, text: str) -> float:
        """記載内容の完成度計算"""
        required_sections = [
            ['企業概要', '事業内容', '会社'],
            ['売上', '財務', '業績'],
            ['強み', '弱み', '特徴'],
            ['市場', '競合', '顧客'],
            ['目標', '計画', '方針'],
            ['補助事業', '販路', '開拓']
        ]
        
        text_lower = text.lower()
        completed_sections = 0
        
        for section in required_sections:
            if any(keyword in text_lower for keyword in section):
                completed_sections += 1
        
        completeness_score = completed_sections / len(required_sections)
        return round(completeness_score, 2)