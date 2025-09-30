import streamlit as st
import pandas as pd
from small_business_scoring_engine import SmallBusinessScoringEngine
from small_business_analyzer import SmallBusinessAnalyzer
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

class SmallBusinessScoringApp:
    def __init__(self):
        self.scoring_engine = SmallBusinessScoringEngine()
        self.analyzer = SmallBusinessAnalyzer()
        
    def setup_page(self):
        st.set_page_config(
            page_title="小規模事業者持続化補助金 模擬採点システム",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # カスタムCSS
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #4CAF50, #45a049);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .score-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #4CAF50;
        }
        .improvement-card {
            background: #fff3cd;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            margin: 0.5rem 0;
        }
        .warning-card {
            background: #f8d7da;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #dc3545;
            margin: 0.5rem 0;
        }
        .success-card {
            background: #d4edda;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #28a745;
            margin: 0.5rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

    def render_header(self):
        st.markdown("""
        <div class="main-header">
            <h1>📊 小規模事業者持続化補助金 模擬採点システム</h1>
            <p>公募要領の審査基準に基づく正確な採点と具体的な改善提案</p>
        </div>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        with st.sidebar:
            st.markdown("## 📋 システム概要")
            st.markdown("""
            **審査基準（公募要領準拠）**
            - 基礎審査（必須要件）
            - 計画審査（4つの評価軸）
            - 加点審査（政策加点）
            
            **評価項目**
            - 経営状況分析の妥当性
            - 経営方針・目標の適切性  
            - 補助事業計画の有効性
            - 積算の透明・適切性
            """)
            
            st.markdown("## ⚙️ 採点設定")
            self.strict_mode = st.checkbox("厳格採点モード", value=True, help="実際の審査に近い厳しい基準で採点")
            self.show_details = st.checkbox("詳細分析表示", value=True, help="項目別の詳細分析を表示")
            
            st.markdown("## 📊 採点基準")
            st.markdown("""
            - **優秀 (80-100点)**: 採択可能性 高
            - **良好 (65-79点)**: 採択可能性 中
            - **普通 (50-64点)**: 改善必要
            - **不十分 (35-49点)**: 大幅改善必要
            - **不適格 (0-34点)**: 申請要件未充足
            """)

    def render_file_upload(self):
        st.markdown("## 📄 申請書類アップロード")
        
        uploaded_file = st.file_uploader(
            "経営計画書兼補助事業計画書（PDF）をアップロードしてください",
            type=['pdf'],
            help="様式2の経営計画書・補助事業計画書をPDF形式でアップロードしてください"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ ファイル '{uploaded_file.name}' がアップロードされました")
            
            # ファイル情報表示
            file_details = {"ファイル名": uploaded_file.name, "ファイルサイズ": f"{uploaded_file.size} bytes"}
            st.json(file_details)
            
            return uploaded_file
        
        return None

    def render_scoring_results(self, results):
        # 総合スコア表示
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # スコアゲージ
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=results['total_score'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "総合スコア"},
                delta={'reference': 65},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 35], 'color': "lightgray"},
                        {'range': [35, 50], 'color': "yellow"},
                        {'range': [50, 65], 'color': "orange"},
                        {'range': [65, 80], 'color': "lightgreen"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 65
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            <div class="score-card">
                <h3>📊 採点結果</h3>
                <h2 style="color: #4CAF50;">{results['total_score']:.1f}点</h2>
                <p><strong>評価レベル:</strong> {results['evaluation_level']}</p>
                <p><strong>採択可能性:</strong> {results['adoption_probability']:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="score-card">
                <h3>🎯 審査状況</h3>
                <p><strong>基礎審査:</strong> {'✅ 通過' if results['basic_requirements_passed'] else '❌ 要改善'}</p>
                <p><strong>計画審査:</strong> {results['total_score']:.1f}/100点</p>
                <p><strong>加点項目:</strong> {results['bonus_points']:.1f}点</p>
            </div>
            """, unsafe_allow_html=True)

    def render_detailed_scores(self, results):
        st.markdown("## 📋 項目別採点詳細")
        
        # 4つの主要評価軸
        criteria_data = []
        for criterion, score_info in results['detailed_scores'].items():
            criteria_data.append({
                '評価項目': criterion,
                '得点': f"{score_info['score']:.1f}",
                '満点': f"{score_info['max_score']:.1f}",
                '達成率': f"{(score_info['score']/score_info['max_score']*100):.1f}%"
            })
        
        df = pd.DataFrame(criteria_data)
        st.dataframe(df, use_container_width=True)
        
        # レーダーチャート
        categories = list(results['detailed_scores'].keys())
        scores = [results['detailed_scores'][cat]['score'] for cat in categories]
        max_scores = [results['detailed_scores'][cat]['max_score'] for cat in categories]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=categories,
            fill='toself',
            fillcolor='rgba(76, 175, 80, 0.3)',
            line=dict(color='rgb(76, 175, 80)'),
            name='実際のスコア'
        ))
        fig.add_trace(go.Scatterpolar(
            r=max_scores,
            theta=categories,
            fill='toself',
            fillcolor='rgba(200, 200, 200, 0.2)',
            line=dict(color='rgb(200, 200, 200)'),
            name='満点'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 30]
                )),
            showlegend=True,
            title="評価項目別スコア比較"
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_improvements(self, results):
        st.markdown("## 🔧 改善提案")
        
        improvements = results['improvements']
        
        # 重要度別に分類
        critical_improvements = [imp for imp in improvements if imp['priority'] == '緊急']
        important_improvements = [imp for imp in improvements if imp['priority'] == '重要']
        recommended_improvements = [imp for imp in improvements if imp['priority'] == '推奨']
        
        if critical_improvements:
            st.markdown("### 🚨 緊急改善項目")
            for imp in critical_improvements:
                st.markdown(f"""
                <div class="warning-card">
                    <h4>❌ {imp['item']}</h4>
                    <p><strong>現状の問題:</strong> {imp['current_issue']}</p>
                    <p><strong>改善方法:</strong> {imp['improvement_method']}</p>
                    <p><strong>具体例:</strong> {imp['example']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        if important_improvements:
            st.markdown("### ⚠️ 重要改善項目")
            for imp in important_improvements:
                st.markdown(f"""
                <div class="improvement-card">
                    <h4>🔧 {imp['item']}</h4>
                    <p><strong>現状の問題:</strong> {imp['current_issue']}</p>
                    <p><strong>改善方法:</strong> {imp['improvement_method']}</p>
                    <p><strong>具体例:</strong> {imp['example']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        if recommended_improvements:
            st.markdown("### 💡 推奨改善項目")
            for imp in recommended_improvements:
                st.markdown(f"""
                <div class="success-card">
                    <h4>✨ {imp['item']}</h4>
                    <p><strong>改善効果:</strong> {imp['current_issue']}</p>
                    <p><strong>実施方法:</strong> {imp['improvement_method']}</p>
                    <p><strong>具体例:</strong> {imp['example']}</p>
                </div>
                """, unsafe_allow_html=True)

    def render_bonus_analysis(self, results):
        st.markdown("## ⭐ 加点項目分析")
        
        bonus_analysis = results.get('bonus_analysis', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 重点政策加点")
            priority_bonuses = bonus_analysis.get('priority_bonuses', [])
            if priority_bonuses:
                for bonus in priority_bonuses:
                    status = "✅ 該当" if bonus['eligible'] else "❌ 非該当"
                    st.markdown(f"**{bonus['name']}**: {status}")
                    if not bonus['eligible'] and bonus.get('requirements'):
                        st.markdown(f"要件: {bonus['requirements']}")
            else:
                st.info("重点政策加点の分析結果がありません")
        
        with col2:
            st.markdown("### 🏆 政策加点")
            policy_bonuses = bonus_analysis.get('policy_bonuses', [])
            if policy_bonuses:
                for bonus in policy_bonuses:
                    status = "✅ 該当" if bonus['eligible'] else "❌ 非該当"
                    st.markdown(f"**{bonus['name']}**: {status}")
                    if not bonus['eligible'] and bonus.get('requirements'):
                        st.markdown(f"要件: {bonus['requirements']}")
            else:
                st.info("政策加点の分析結果がありません")

    def render_export_options(self, results):
        st.markdown("## 📤 結果エクスポート")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 詳細レポート（JSON）", use_container_width=True):
                json_data = json.dumps(results, ensure_ascii=False, indent=2)
                st.download_button(
                    "ダウンロード",
                    data=json_data,
                    file_name=f"scoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📋 改善提案（CSV）", use_container_width=True):
                improvements_df = pd.DataFrame(results['improvements'])
                csv_data = improvements_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    "ダウンロード",
                    data=csv_data,
                    file_name=f"improvements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("📈 採点結果（CSV）", use_container_width=True):
                scores_data = []
                for criterion, score_info in results['detailed_scores'].items():
                    scores_data.append({
                        '評価項目': criterion,
                        '得点': score_info['score'],
                        '満点': score_info['max_score'],
                        '達成率': score_info['score']/score_info['max_score']*100
                    })
                scores_df = pd.DataFrame(scores_data)
                csv_data = scores_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    "ダウンロード",
                    data=csv_data,
                    file_name=f"scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

    def run(self):
        self.setup_page()
        self.render_header()
        self.render_sidebar()
        
        # メインコンテンツ
        uploaded_file = self.render_file_upload()
        
        if uploaded_file is not None:
            with st.spinner("📄 PDF解析中..."):
                try:
                    # PDF解析
                    document_analysis = self.analyzer.analyze_pdf(uploaded_file)
                    
                    if document_analysis and document_analysis.get('success'):
                        st.success("✅ PDF解析が完了しました")
                        
                        if self.show_details:
                            with st.expander("📄 解析結果詳細"):
                                st.json(document_analysis)
                        
                        with st.spinner("🔍 採点中..."):
                            # 採点実行
                            scoring_results = self.scoring_engine.score_application(
                                document_analysis,
                                strict_mode=self.strict_mode
                            )
                            
                            if scoring_results:
                                st.success("✅ 採点が完了しました")
                                
                                # 結果表示
                                self.render_scoring_results(scoring_results)
                                
                                # 詳細スコア
                                if self.show_details:
                                    self.render_detailed_scores(scoring_results)
                                
                                # 改善提案
                                self.render_improvements(scoring_results)
                                
                                # 加点分析
                                self.render_bonus_analysis(scoring_results)
                                
                                # エクスポート
                                self.render_export_options(scoring_results)
                                
                            else:
                                st.error("❌ 採点処理でエラーが発生しました")
                    else:
                        st.error("❌ PDF解析でエラーが発生しました")
                        if document_analysis and document_analysis.get('error'):
                            st.error(f"エラー詳細: {document_analysis['error']}")
                
                except Exception as e:
                    st.error(f"❌ 処理中にエラーが発生しました: {str(e)}")
        else:
            # サンプル結果表示（デモ用）
            st.markdown("## 📋 サンプル採点結果")
            st.info("PDFファイルをアップロードすると、実際の採点結果がここに表示されます")
            
            # デモ用のサンプルデータ
            sample_results = {
                'total_score': 68.5,
                'evaluation_level': '良好',
                'adoption_probability': 72.3,
                'basic_requirements_passed': True,
                'bonus_points': 5.0,
                'detailed_scores': {
                    '経営状況分析の妥当性': {'score': 18.5, 'max_score': 25},
                    '経営方針・目標の適切性': {'score': 20.0, 'max_score': 25},
                    '補助事業計画の有効性': {'score': 22.0, 'max_score': 30},
                    '積算の透明・適切性': {'score': 8.0, 'max_score': 20}
                },
                'improvements': [
                    {
                        'item': '市場分析の深化',
                        'priority': '重要',
                        'current_issue': '競合分析が表面的で、市場規模や成長性の具体的データが不足',
                        'improvement_method': '統計データや業界レポートを活用した定量的な市場分析を追加',
                        'example': '「○○業界の市場規模は○○億円で、年成長率○%。主要競合3社の売上・シェア分析...」'
                    }
                ]
            }
            self.render_scoring_results(sample_results)

if __name__ == "__main__":
    app = SmallBusinessScoringApp()
    app.run()