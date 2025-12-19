import streamlit as st
import random

st.set_page_config(page_title="세포 키우기")
st.title("세포 키우기")

# =====================
# 공통 설정
# =====================
BOX_SIZE = 500
CELL_SIZE = 80
OBJ_SIZE = 40

CELL_R = CELL_SIZE / 2
OBJ_R = OBJ_SIZE / 2

STEP = 20

# =====================
# 세션 초기화
# =====================
if "stage" not in st.session_state:
    st.session_state.stage = 1
if "top" not in st.session_state:
    st.session_state.top = 200
if "left" not in st.session_state:
    st.session_state.left = 200
if "gauge" not in st.session_state:
    st.session_state.gauge = 100
if "objects" not in st.session_state:
    st.session_state.objects = []
if "game_over" not in st.session_state:   # ✅ 추가
    st.session_state.game_over = False

# =====================
# 오브젝트 생성
# =====================
def spawn(color, count):
    objs = []
    while len(objs) < count:
        t = random.randint(0, BOX_SIZE - OBJ_SIZE)
        l = random.randint(0, BOX_SIZE - OBJ_SIZE)
        d = ((st.session_state.top - t)**2 + (st.session_state.left - l)**2)**0.5
        if d > CELL_R + OBJ_R:
            objs.append((t, l, color))
    return objs

# =====================
# 단계별 초기화
# =====================
if "initialized_stage" not in st.session_state:
    st.session_state.initialized_stage = 0

if st.session_state.stage != st.session_state.initialized_stage:
    st.session_state.top = 200
    st.session_state.left = 200
    st.session_state.gauge = 100

    if st.session_state.stage == 1:
        st.session_state.objects = spawn("#c8b9ee", 10)
    elif st.session_state.stage == 2:
        st.session_state.objects = spawn("#ff4d4d", 10)
    elif st.session_state.stage == 3:
        st.session_state.objects = []
    elif st.session_state.stage == 4:
        st.session_state.objects = (
            spawn("#ffd700", 6) +
            spawn("#2ecc71", 6)
        )
    elif st.session_state.stage == 5:
        st.session_state.objects = []

    st.session_state.initialized_stage = st.session_state.stage

# =====================
# 이동 버튼
# =====================
if st.session_state.stage <= 4 and not st.session_state.game_over:
    c1, c2, c3 = st.columns([1, 2, 1])

    def move(dt, dl):
        st.session_state.top += dt
        st.session_state.left += dl
        if st.session_state.stage <= 2:
            st.session_state.gauge -= 2

    with c1:
        if st.button("←"):
            move(0, -STEP)
    with c2:
        if st.button("↑"):
            move(-STEP, 0)
        if st.button("↓"):
            move(STEP, 0)
    with c3:
        if st.button("→"):
            move(0, STEP)

# =====================
# 충돌 판정
# =====================
new_objs = []
yellow_left = 0

for t, l, color in st.session_state.objects:
    d = ((st.session_state.top - t)**2 + (st.session_state.left - l)**2)**0.5
    if d <= CELL_R + OBJ_R:
        if st.session_state.stage <= 2:
            st.session_state.gauge += 10
        elif st.session_state.stage == 4:
            if color == "#ffd700":
                st.session_state.gauge += 10
            elif color == "#2ecc71":
                st.session_state.gauge -= 10
    else:
        new_objs.append((t, l, color))
        if color == "#ffd700":
            yellow_left += 1

st.session_state.objects = new_objs

# =====================
# ✅ 게임 오버 판정 (추가)
# =====================
if st.session_state.gauge <= 0:
    st.session_state.game_over = True

# =====================
# 단계 전환
# =====================
if st.session_state.stage in [1, 2] and len(st.session_state.objects) == 0:
    st.session_state.stage += 1
    st.rerun()

if st.session_state.stage == 4 and yellow_left == 0:
    st.session_state.stage = 5
    st.rerun()

# =====================
# 게이지
# =====================
if st.session_state.stage <= 4 and not st.session_state.game_over:
    st.progress(max(0, min(st.session_state.gauge / 200, 1)))

# =====================
# 안내 문구
# =====================
# =====================
# 3단계 pH 선택
# =====================
if st.session_state.stage == 3:
    st.markdown(
        "<div style='color:white; font-size:20px; margin-bottom:10px;'>"
        "🧪 세포에 적절한 pH를 선택하세요 (중성)"
        "</div>",
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("산성 (pH ↓)"):
            st.error("❌ 효소가 변성되었습니다. 게임 오버!")
            st.stop()

    with c2:
        if st.button("중성 (pH 7)"):
            st.success("✅ 최적의 pH입니다!")
            st.session_state.stage = 4
            st.rerun()

    with c3:
        if st.button("염기성 (pH ↑)"):
            st.error("❌ 세포 기능이 손상되었습니다. 게임 오버!")
            st.stop()

guide = ""
if st.session_state.stage == 1:
    guide = "🟣 포도당을 모두 먹어 ATP를 생성하세요."
elif st.session_state.stage == 2:
    guide = "🔴 산소를 먹어 에너지 생산을 유지하세요."
elif st.session_state.stage == 3:
    guide = "🧪 적절한 pH(중성)를 선택하세요."
elif st.session_state.stage == 4:
    guide = "🟡 효소는 도움, 🟢 해로운 요소는 피하세요."

if guide and not st.session_state.game_over:
    st.markdown(
        f"<div style='color:white; font-size:20px; margin-bottom:10px;'>{guide}</div>",
        unsafe_allow_html=True
    )

# =====================
# 메인 화면 / 게임 오버
# =====================
if st.session_state.game_over:
    st.markdown(
        """
        <div style="color:white; font-size:36px; text-align:center; margin-top:100px;">
        💀 GAME OVER 💀<br><br>
        세포의 에너지가 모두 소모되었습니다.
        </div>
        """,
        unsafe_allow_html=True
    )

elif st.session_state.stage <= 4:
    objs_html = ""
    for t, l, color in st.session_state.objects:
        objs_html += f"""
        <div style="
            width:{OBJ_SIZE}px;
            height:{OBJ_SIZE}px;
            background:{color};
            border-radius:50%;
            position:absolute;
            top:{t}px;
            left:{l}px;
        "></div>
        """

    st.markdown(
        f"""
        <div style="position:relative; width:{BOX_SIZE}px; height:{BOX_SIZE}px; border:1px solid #555;">
            <div style="
                width:{CELL_SIZE}px;
                height:{CELL_SIZE}px;
                background:#eaaea3;
                border-radius:50%;
                position:absolute;
                top:{st.session_state.top}px;
                left:{st.session_state.left}px;
            "></div>
            {objs_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================
# 5단계 요약
# =====================
if st.session_state.stage == 5:
    st.markdown(
        """
        <div style="color:white; font-size:18px; text-align:center;">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:30px;">
            <div><b>1단계</b><br>포도당을 분해해 ATP 생성</div>
            <div><b>2단계</b><br>산소를 이용해 에너지 효율 증가</div>
            <div><b>3단계</b><br>pH 균형으로 효소 활성 유지</div>
            <div><b>4단계</b><br>효소는 보호, 해로운 요소는 회피</div>
        </div>
        <br><br>
        세포는 영양분, 산소, 효소, 환경 조건이 모두 조화될 때
        정상적인 생명 활동을 유지할 수 있다.
        </div>
        """,
        unsafe_allow_html=True
    )
