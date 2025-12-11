import streamlit as st
import time
import datetime
import pandas as pd
import os
import altair as alt  # グラフ描画用ライブラリ

# -------------------
# ページ設定
# -------------------
st.set_page_config(
    page_title="進化版 集中タイマー",
    page_icon="⏱️",
    layout="centered"
)

# タイマーの文字を大きくするためのCSS
st.markdown("""
    <style>
    .timer-font {
        font-size: 60px !important;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
    }
    .stButton button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------
# 初期設定・関数
# -------------------
CSV_FILE = "data/focus_log.csv"

# データフォルダ作成
if not os.path.exists("data"):
    os.makedirs("data")

def load_data():
    """CSVデータの読み込み"""
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["date", "task", "work_min"])
        df.to_csv(CSV_FILE, index=False)
        return df
    return pd.read_csv(CSV_FILE)

def save_log(task, minutes):
    """ログの保存（pd.concatを使用）"""
    df = load_data()
    new_row = pd.DataFrame({
        "date": [datetime.date.today()],
        "task": [task],
        "work_min": [minutes]
    })
    # appendは廃止されたためconcatを使用
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# -------------------
# サイドバー（設定）
# -------------------
with st.sidebar:
    st.header("⚙️ 設定")
    WORK_MIN = st.slider("作業時間（分）", 1, 90, 25)
    BREAK_MIN = st.slider("休憩時間（分）", 1, 30, 5)
    st.markdown("---")
    
    if st.button("履歴を全削除"):
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
            st.success("履歴を削除しました")
            time.sleep(1)
            st.rerun() # 画面を更新            

# -------------------
# メイン画面
# -------------------
st.title("⏱️ 作業集中タイマー ツダ")

# タブ機能で画面を切り替え
tab1, tab2 = st.tabs(["⏳ タイマー", "📊 実績・分析"])

# === タブ1：タイマー機能 ===
with tab1:
    st.subheader("集中セッション開始")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        task = st.text_input("作業内容を入力", placeholder="例：Pythonの勉強、レポート作成...")
    with col2:
        st.write("") # レイアウト調整
        st.write("") 
        start_btn = st.button("▶ スタート", type="primary")

    if start_btn:
        if task == "":
            st.warning("⚠️ 作業内容を入力してください！")
        else:
            # タイマー表示エリア
            status_text = st.empty()
            timer_display = st.empty()
            progress_bar = st.progress(0)
            
            total_seconds = WORK_MIN * 60
            
            status_text.info(f"🔥 **{task}** に集中中...")

            # カウントダウンループ
            for i in range(total_seconds):
                remaining = total_seconds - i
                mins, secs = divmod(remaining, 60)
                
                # 大きな文字でタイマー表示
                timer_display.markdown(f'<p class="timer-font">{mins:02}:{secs:02}</p>', unsafe_allow_html=True)
                
                # プログレスバー更新 (0.0 〜 1.0)
                progress_bar.progress((i + 1) / total_seconds)
                time.sleep(1)

            # --- 終了後の処理 ---
            progress_bar.progress(1.0)
            timer_display.markdown('<p class="timer-font">00:00</p>', unsafe_allow_html=True)
            
            # 通知音（HTML5 Audioを使用）
            audio_html = """
                <audio autoplay>
                <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
            
            st.success("🎉 作業完了！お疲れ様でした。")
            st.balloons() # 風船エフェクト
            
            # 休憩時間の案内
            st.info(f"☕ 次は {BREAK_MIN} 分間の休憩です。")
            
            # データ保存
            save_log(task, WORK_MIN)


# === タブ2：実績・分析機能 ===
with tab2:
    st.subheader("📅 集中記録ログ")
    
    df = load_data()
    
    if not df.empty:
        # 今日の日付データ
        today_str = str(datetime.date.today())
        df_today = df[df['date'] == today_str]
        
        # --- メトリクス（数値）表示 ---
        col1, col2, col3 = st.columns(3)
        col1.metric("今日の作業時間", f"{df_today['work_min'].sum()} 分")
        col2.metric("今日のセッション数", f"{len(df_today)} 回")
        col3.metric("総作業時間", f"{df['work_min'].sum()} 分")
        
        st.markdown("---")

        # --- グラフ表示 (Altair) ---
        st.write("📈 **日別の作業時間推移**")
        
        # 日付ごとに集計
        daily_data = df.groupby("date")["work_min"].sum().reset_index()
        
        chart = alt.Chart(daily_data).mark_bar().encode(
            x=alt.X('date', title='日付'),
            y=alt.Y('work_min', title='作業時間(分)'),
            tooltip=['date', 'work_min']
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)

        # --- 詳細データテーブル ---
        st.write("📋 **履歴一覧**")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        
    else:
        st.info("まだ記録がありません。タイマーを使って作業を記録しましょう！")