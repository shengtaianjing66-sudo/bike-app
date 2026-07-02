import streamlit as st
import pandas as pd
import math
import os

# ページの初期設定
st.set_page_config(page_title="プロ仕様 専属メカニック AI", page_icon="🚴", layout="centered")

# ==========================================
# データベースの読み込み（CSV連携）
# ==========================================
CSV_FILE = "bike_components.csv"

# 万が一CSVがない場合の簡易フォールバック（バックアップ用）
if not os.path.exists(CSV_FILE):
    st.error(f"エラー: {CSV_FILE} が見つかりません。")
    st.stop()

# PandasでCSVを読み込む
df = pd.read_csv(CSV_FILE)

# シマノスプロケットデータベース（固定値）
SHIMANO_SPROCKETS = [
    {"name": "CS-R8101-12 (11-30T)", "max_teeth": 30},
    {"name": "CS-R8101-12 (11-34T)", "max_teeth": 34},
    {"name": "CS-HG710-12 (11-36T)", "max_teeth": 36},
    {"name": "CS-R8000-11 (11-28T)", "max_teeth": 28},
    {"name": "CS-R8000-11 (11-32T)", "max_teeth": 32},
    {"name": "CS-R8000-11 (11-34T)", "max_teeth": 34},
]

# ==========================================
# メイン画面デザイン
# ==========================================
st.title("🚴 プロ仕様 専属メカニック AI")
st.write("メーカー別の本格データベースから、あなたの愛車を完全再現します。")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.header("🎛️ ライダー & コース")
    user_weight = st.slider("あなたの体重 (kg)", min_value=40.0, max_value=120.0, value=60.0, step=0.5)
    max_grade = st.slider("コースの最大勾配 (%)", min_value=0.0, max_value=25.0, value=8.0, step=0.5)
    style = st.selectbox(
        "走りのスタイル",
        ["楽に登りたい（完走・マイペース重視）", "ガシガシ踏みたい（ヒルクライムタイム重視）"]
    )

with col2:
    st.header("🔧 バイク & 機材選択")

    # --- ① フレーム選択 ---
    frames_df = df[df['type'] == 'frame']
    frame_brands = sorted(frames_df['brand'].unique())
    selected_frame_brand = st.selectbox("フレームのメーカー", frame_brands)

    # 選んだメーカーのモデルだけに絞り込む
    filtered_frames = frames_df[frames_df['brand'] == selected_frame_brand]
    selected_frame_model = st.selectbox("フレームのモデル", filtered_frames['model'].tolist())
    frame_weight = filtered_frames[filtered_frames['model'] == selected_frame_model]['weight'].values[0]

    # --- ② ホイール選択 ---
    wheels_df = df[df['type'] == 'wheel']
    wheel_brands = sorted(wheels_df['brand'].unique())
    selected_wheel_brand = st.selectbox("ホイールのメーカー", wheel_brands)

    # 選んだメーカーのモデルだけに絞り込む
    filtered_wheels = wheels_df[wheels_df['brand'] == selected_wheel_brand]
    selected_wheel_model = st.selectbox("ホイールのモデル", filtered_wheels['model'].tolist())
    wheel_weight = filtered_wheels[filtered_wheels['model'] == selected_wheel_model]['weight'].values[0]

    # --- ③ コンポーネント選択 ---
    comps_df = df[df['type'] == 'comp']
    selected_comp_model = st.selectbox("メインコンポ（変速機等）", comps_df['model'].tolist())
    comp_weight = comps_df[comps_df['model'] == selected_comp_model]['weight'].values[0]

    # その他パーツの固定重量（サドル、ハンドル、ペダル、サイコン等: 目安1.8kg）
    accessories_weight = 1.8

    # バイク総重量の自動計算
    bike_weight = frame_weight + wheel_weight + comp_weight + accessories_weight

    # 計算された重量を表示
    st.info(f"⚙️ **推定バイク重量: {bike_weight:.2f} kg**  \n(内訳: フレーム {frame_weight}kg / ホイール {wheel_weight}kg / コンポ {comp_weight}kg / 小物他 {accessories_weight}kg)")

st.markdown("---")

st.header("⚙️ ギヤ比セッティング")
col_gear1, col_gear2 = st.columns(2)

with col_gear1:
    front_inner = st.selectbox("フロントインナー歯数 (T)", options=[30, 34, 36, 39, 42], index=1)

with col_gear2:
    rear_max = st.selectbox("現在のリア最大歯数 (T)", options=[25, 28, 30, 32, 34, 36, 40], index=2)

st.markdown("---")

# 診断実行ボタン
if st.button("🛠️ この機材セッティングで診断を開始する", type="primary", use_container_width=True):

    tire_width = 28.0  # デフォルトタイヤ幅(mm)
    current_ratio = front_inner / rear_max
    total_weight = user_weight + bike_weight

    st.header("🎯 メカニック診断結果")

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.metric(label="現在の最小ギヤ比", value=f"{current_ratio:.2f}", delta=f"{front_inner}T × {rear_max}T", delta_color="off")
    with col_res2:
        st.metric(label="総重量（ライダー＋バイク）", value=f"{total_weight:.1f} kg")

    # 必要なギヤ比の目安計算
    if "楽に登りたい" in style:
        required_ratio = 1.0 if max_grade >= 10.0 else 1.1
    else:
        required_ratio = 1.15 if max_grade >= 10.0 else 1.25

    # 診断結果のロジック
    if current_ratio > required_ratio:
        recommended_rear = math.ceil(front_inner / required_ratio)
        st.error(f"⚠️ **ギヤが重すぎます！**  \nこの最大勾配 {max_grade}% をそのスタイルで登るには、ギヤが重すぎます。(目標ギヤ比: {required_ratio:.2f} 以下 / 推奨リア最大: {recommended_rear}T以上)")

        # 現行機材でのサバイバルアドバイス
        st.markdown("### 🪵 現行機材でこの坂を乗り切るためのサバイバル戦術")
        ratio_gap = current_ratio - required_ratio

        if ratio_gap >= 0.2:
            st.warning(
                "🚨 **【深刻な超高負荷状態です】** \n"
                "普通にシッティングで登ると一瞬で足が限界（オールアウト）を迎えます。以下の戦術を徹底してください：\n\n"
                "1. **『体重を乗せる休むダンシング』**: 常に立ち漕ぎをする必要がありますが、腕の力でハンドルを引き上げるのではなく、自分の体重（60kg）を左右のペダルに交互に真上から『落とす』イメージで進みましょう。筋肉ではなく骨で踏む感覚です。\n"
                "2. **『ジグザグ走行（蛇行）』**: 道幅が広く、かつ対向車や後続車が絶対にいない安全な状況に限り、道路を斜めに蛇行して進んでください。斜度を物理的に数パーセント緩めることができます。\n"
                "3. **『絶対に心拍を上げない』**: ケイデンスが40〜50RPMまで落ち込むため筋肉への負荷が凄まじいです。呼吸がゼーゼーと乱れる手前のペースを死守し、どうしても無理なら足を着いて押し歩く勇気も立派な戦術です。"
            )
        else:
            st.info(
                "💡 **【やや重いギヤ比です：テクニックでカバー可能】** \n"
                "少しキツいですが、ペダリングの意識とフォームを変えれば十分攻略可能な範囲です！\n\n"
                "1. **『サドルの着座位置を後ろに』**: シッティングの際、サドルの少し後ろ側に深く座ってみてください。こうすることで、太ももの前（大腿四頭筋）ではなく、お尻やももの裏側（ハムストリング）の大きな筋肉を使って、トルクフルにペダルを『押し出す』ように回せます。\n"
                "2. **『キツくなる前の一歩貯金』**: 坂の斜度がガツンと上がる手前の、まだ緩やかな区間で少しだけ加速し、勢い（惰性）をつけてキツい区間に突入しましょう。ケイデンスの低下を最小限に抑えられます。\n"
                "3. **『体幹の固定』**: ハンドルを強く握りすぎると上半身が疲労します。腹筋と背筋に少し力を入れて体幹を安定させ、腕はリラックスした状態でペダルにパワーを集中させてください。"
            )

        st.subheader("🛠️ 将来的な交換パーツ提案")
        matching_parts = [s["name"] for s in SHIMANO_SPROCKETS if s["max_teeth"] >= recommended_rear]
        if matching_parts:
            st.write("次回、同じコースに挑戦する際は以下のスプロケットへの交換がおすすめです：")
            for part in matching_parts:
                st.markdown(f"- **{part}**")
    else:
        st.success(f"✅ **カンペキです！**  \n現在の最小ギヤ比（{current_ratio:.2f}）なら、最大勾配 {max_grade}% の坂道も足を残してクリアできます！そのまま走り出しましょう。")

    # 空気圧の計算
    base_pressure = (total_weight / tire_width) * 1.8
    recommended_bar = base_pressure * 0.95 if "楽に登りたい" in style else base_pressure * 1.02

    st.subheader("🎈 推奨タイヤ空気圧 (目安)")
    st.info(f"あなたの総重量（{total_weight:.1f}kg）に合わせた推奨空気圧は **{recommended_bar:.1f} bar** (約 {(recommended_bar * 14.5):.0f} PSI) です。")
