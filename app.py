import base64
import json
import math
from datetime import date, datetime
from pathlib import Path

import streamlit as st
from streamlit_js_eval import streamlit_js_eval

APP_TITLE = "쫄지마"
LOCAL_STORAGE_KEY = "jjol_jima_state_v1"
TOP_IMAGE_PATH = Path("top_jjol.png")

ASSET_FIELDS = ["현금", "통장 잔고", "비상금", "받을 돈", "기타 자산"]
FIXED_FIELDS = [
    "월세",
    "대출 상환",
    "보험",
    "통신비",
    "공과금",
    "구독 서비스",
    "병원/약값",
    "마운자로/건강관리",
    "교통비",
    "기타 고정비",
]
EXPENSE_CATEGORIES = [
    "식비",
    "장보기",
    "외식",
    "배달",
    "커피/간식",
    "생필품",
    "쇼핑",
    "미용",
    "병원 추가비",
    "약속/여행",
    "기타",
]
INCOME_MODES = {
    "무수입 모드": 0,
    "실업급여 모드": 1_800_000,
    "사무직 취업 모드": 2_200_000,
    "직접 입력 모드": 0,
}
STATUS_COPY = {
    "안정": "쫄지마. 생각보다 잘 버티고 있어.",
    "주의": "아직 괜찮아. 이번 달만 살짝 조절하자.",
    "위험": "쫄지는 말고 계산해보자. 줄일 곳은 보인다.",
    "긴급": "겁먹지 말고 움직이자. 지금은 계획이 필요해.",
}

st.set_page_config(page_title=APP_TITLE, page_icon="쫄", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --yellow: #ffd84d;
        --yellow-soft: #fff7d6;
        --navy: #081b3f;
        --navy-soft: #17345f;
        --ink: #111827;
        --muted: #6b7280;
        --soft-muted: #98a2b3;
        --line: #e7ebf2;
        --card: #ffffff;
        --bg: #f7f8fb;
    }
    html, body, [data-testid="stAppViewContainer"] {
        font-family: Pretendard, "Apple SD Gothic Neo", "Malgun Gothic", "Segoe UI", sans-serif;
        background: var(--bg);
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="block-container"] {
        padding-top: 1.15rem;
        padding-bottom: 4rem;
        max-width: 1120px;
    }
    h1, h2, h3 { color: var(--navy); letter-spacing: 0; }
    .top-jjol {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 0 18px;
    }
    .top-jjol img {
        width: clamp(118px, 22vw, 172px);
        height: auto;
        display: block;
        filter: drop-shadow(0 14px 26px rgba(8, 27, 63, 0.12));
    }
    .runway-card {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 28px;
        padding: 30px;
        min-height: 262px;
        box-shadow: 0 20px 52px rgba(8, 27, 63, 0.08);
        position: relative;
        overflow: hidden;
    }
    .runway-card::after {
        content: "";
        position: absolute;
        right: 26px;
        top: 26px;
        width: 11px;
        height: 11px;
        border-radius: 999px;
        background: var(--yellow);
        box-shadow: 0 0 0 8px rgba(255, 216, 77, 0.22);
    }
    .runway-label {
        color: var(--muted);
        font-size: 0.96rem;
        font-weight: 760;
        margin-bottom: 16px;
    }
    .runway-value {
        color: var(--navy);
        font-size: clamp(3.3rem, 9vw, 6.8rem);
        line-height: 0.95;
        font-weight: 920;
        letter-spacing: 0;
        word-break: keep-all;
    }
    .runway-note {
        color: var(--muted);
        font-size: 0.96rem;
        line-height: 1.55;
        margin-top: 20px;
        max-width: 620px;
    }
    .hero-metric-card {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 22px;
        box-shadow: 0 12px 30px rgba(8, 27, 63, 0.055);
        min-height: 126px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .hero-metric-card.accent {
        border-color: rgba(255, 216, 77, 0.72);
        background: #ffffff;
    }
    .hero-metric-label {
        color: var(--muted);
        font-size: 0.9rem;
        font-weight: 760;
        margin-bottom: 10px;
    }
    .hero-metric-value {
        color: var(--navy);
        font-size: clamp(1.75rem, 3vw, 2.55rem);
        line-height: 1.05;
        font-weight: 900;
        word-break: keep-all;
    }
    .hero-metric-note {
        color: var(--soft-muted);
        font-size: 0.84rem;
        margin-top: 10px;
    }
    div[data-testid="stMetric"] {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 16px 16px 14px;
        box-shadow: none;
        min-height: 106px;
    }
    div[data-testid="stMetricLabel"] p {
        color: var(--muted);
        font-size: 0.88rem;
    }
    div[data-testid="stMetricValue"] {
        color: var(--navy);
        font-weight: 820;
    }
    .status-card {
        border-radius: 24px;
        padding: 22px;
        background: #ffffff;
        color: var(--ink);
        border: 1px solid var(--line);
        box-shadow: 0 12px 30px rgba(8, 27, 63, 0.055);
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 7px 12px;
        background: var(--yellow-soft);
        color: var(--navy);
        font-weight: 840;
        margin-bottom: 14px;
    }
    .status-card h2 {
        color: var(--navy);
        font-size: 1.35rem;
        margin: 0 0 10px;
    }
    .status-card p { margin: 0; color: var(--muted); }
    .bar-wrap {
        width: 100%;
        height: 10px;
        background: #eef2f7;
        border-radius: 999px;
        overflow: hidden;
        margin: 18px 0 10px;
    }
    .bar-fill {
        height: 100%;
        background: var(--yellow);
        border-radius: 999px;
    }
    .soft-card {
        border-radius: 24px;
        padding: 20px;
        background: #ffffff;
        border: 1px solid var(--line);
        box-shadow: 0 12px 30px rgba(8, 27, 63, 0.055);
    }
    .soft-card h3 { margin-top: 0; }
    .insight-title {
        margin: 0;
        color: var(--navy);
        font-size: 1.55rem;
        font-weight: 900;
        line-height: 1.1;
    }
    .check-row {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        border-bottom: 1px solid var(--line);
        padding: 12px 0;
    }
    .check-row:last-child { border-bottom: 0; }
    .check-label { color: var(--muted); }
    .check-value { color: var(--navy); font-weight: 840; text-align: right; }
    .mini-note {
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.55;
    }
    .expense-item {
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 13px 15px;
        background: #fff;
        margin-bottom: 10px;
    }
    .expense-top {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        color: var(--navy);
        font-weight: 840;
    }
    .expense-bottom { color: var(--muted); font-size: 0.9rem; margin-top: 4px; }
    .stButton > button, .stFormSubmitButton > button {
        border-radius: 12px;
        border: 0;
        background: var(--navy);
        color: white;
        font-weight: 800;
        padding: 0.65rem 1rem;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        border: 0;
        background: #102d66;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 5px;
        width: fit-content;
        max-width: 100%;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        background: transparent;
        border: 0;
        padding: 7px 13px;
        color: var(--muted);
    }
    .stTabs [aria-selected="true"] {
        background: var(--navy);
        color: white;
    }
    @media (max-width: 720px) {
        [data-testid="block-container"] { padding-left: 1rem; padding-right: 1rem; padding-top: 0.85rem; }
        .runway-card { padding: 24px; min-height: 228px; }
        .hero-metric-card { min-height: 112px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_top_image() -> None:
    image_uri = image_data_uri(TOP_IMAGE_PATH)
    if not image_uri:
        return
    st.markdown(
        f"""
        <div class="top-jjol">
            <img src="{image_uri}" alt="쫄지마">
        </div>
        """,
        unsafe_allow_html=True,
    )


def won(value: float | int) -> str:
    return f"{int(round(value)):,}원"


def plain_number(value: float | int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def default_state() -> dict:
    return {
        "assets": {name: 0 for name in ASSET_FIELDS},
        "fixed_costs": {name: 0 for name in FIXED_FIELDS},
        "income_mode": "무수입 모드",
        "custom_income": 0,
        "expenses": [],
    }


def normalize_state(loaded: dict | None) -> dict:
    state = default_state()
    if not isinstance(loaded, dict):
        return state
    state.update({key: loaded.get(key, state[key]) for key in state.keys()})
    state["assets"] = {name: plain_number(state["assets"].get(name, 0)) for name in ASSET_FIELDS}
    state["fixed_costs"] = {name: plain_number(state["fixed_costs"].get(name, 0)) for name in FIXED_FIELDS}
    state["income_mode"] = state["income_mode"] if state["income_mode"] in INCOME_MODES else "무수입 모드"
    state["custom_income"] = plain_number(state.get("custom_income", 0))
    state["expenses"] = [expense for expense in state.get("expenses", []) if isinstance(expense, dict)]
    return state


def browser_state_json(state: dict) -> str:
    return json.dumps(normalize_state(state), ensure_ascii=False)


def persist_browser_state(state: dict, key_suffix: str) -> None:
    payload = json.dumps(browser_state_json(state), ensure_ascii=False)
    streamlit_js_eval(
        js_expressions=f"localStorage.setItem('{LOCAL_STORAGE_KEY}', {payload})",
        want_output=False,
        key=f"save_{key_suffix}_{datetime.now().timestamp()}",
    )


def clear_browser_state() -> None:
    streamlit_js_eval(
        js_expressions=f"localStorage.removeItem('{LOCAL_STORAGE_KEY}')",
        want_output=False,
        key=f"clear_{datetime.now().timestamp()}",
    )


def current_income(state: dict) -> int:
    if state["income_mode"] == "직접 입력 모드":
        return plain_number(state.get("custom_income", 0))
    return INCOME_MODES[state["income_mode"]]


def parse_expense_date(value: str) -> date | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def this_month_expenses(expenses: list[dict]) -> list[dict]:
    today = date.today()
    result = []
    for expense in expenses:
        expense_date = parse_expense_date(expense.get("date", ""))
        if expense_date and expense_date.year == today.year and expense_date.month == today.month:
            result.append(expense)
    return result


def category_totals(expenses: list[dict]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for expense in expenses:
        category = expense.get("category", "기타")
        totals[category] = totals.get(category, 0) + plain_number(expense.get("amount", 0))
    return totals


def get_status(runway_months: float) -> str:
    if math.isinf(runway_months) or runway_months >= 6:
        return "안정"
    if runway_months >= 3:
        return "주의"
    if runway_months >= 1:
        return "위험"
    return "긴급"


def fulltime_need(status: str, shortage: int) -> str:
    if status in ["안정", "주의"] and shortage <= 0:
        return "낮음"
    if status == "긴급" or shortage >= 1_000_000:
        return "높음"
    return "중간"


def calculate(state: dict) -> dict:
    total_assets = sum(plain_number(value) for value in state["assets"].values())
    income = current_income(state)
    fixed_total = sum(plain_number(value) for value in state["fixed_costs"].values())
    month_expenses = this_month_expenses(state["expenses"])
    variable_total = sum(plain_number(expense.get("amount", 0)) for expense in month_expenses)
    remaining_this_month = income - fixed_total - variable_total
    remaining_days = max(1, (date(date.today().year, date.today().month, 28) - date.today()).days + 4)
    daily_available = max(0, remaining_this_month) / remaining_days

    monthly_outflow = max(0, fixed_total + variable_total - income)
    if monthly_outflow <= 0:
        runway_months = math.inf if total_assets > 0 else 0
        survival_days = math.inf if total_assets > 0 else 0
    else:
        runway_months = total_assets / monthly_outflow
        survival_days = runway_months * 30

    status = get_status(runway_months)
    shortage = max(0, -remaining_this_month)
    part_time_days = math.ceil(shortage / 100_000) if shortage > 0 else 0
    category_map = category_totals(month_expenses)
    top_category = max(category_map, key=category_map.get) if category_map else "아직 없음"
    top_amount = category_map.get(top_category, 0) if category_map else 0

    fixed_top = max(state["fixed_costs"], key=state["fixed_costs"].get) if state["fixed_costs"] else "아직 없음"
    fixed_top_amount = plain_number(state["fixed_costs"].get(fixed_top, 0))
    if top_amount >= fixed_top_amount and top_amount > 0:
        leverage_category = top_category
    elif fixed_top_amount > 0:
        leverage_category = fixed_top
    else:
        leverage_category = "아직 없음"

    cash_bar = 100 if math.isinf(runway_months) else min(100, max(0, int((runway_months / 6) * 100)))

    return {
        "total_assets": total_assets,
        "income": income,
        "fixed_total": fixed_total,
        "variable_total": variable_total,
        "remaining_this_month": remaining_this_month,
        "daily_available": daily_available,
        "runway_months": runway_months,
        "survival_days": survival_days,
        "status": status,
        "shortage": shortage,
        "part_time_days": part_time_days,
        "fulltime_need": fulltime_need(status, shortage),
        "top_category": top_category,
        "leverage_category": leverage_category,
        "cash_bar": cash_bar,
        "month_expenses": month_expenses,
        "category_map": category_map,
    }


def format_months(value: float) -> str:
    if math.isinf(value):
        return "계속 유지 가능"
    return f"{value:.1f}개월"


def format_days(value: float) -> str:
    if math.isinf(value):
        return "계속 유지 가능"
    return f"{int(value):,}일"




def render_status_panel(calc: dict) -> None:
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-pill">Status: {calc['status']}</div>
            <h2>{STATUS_COPY[calc['status']]}</h2>
            <p>Cash Bar: {calc['cash_bar']}% · Survival Days: {format_days(calc['survival_days'])} · Runway: {format_months(calc['runway_months'])}</p>
            <div class="bar-wrap"><div class="bar-fill" style="width:{calc['cash_bar']}%"></div></div>
            <p>기준: 이번 달 입력된 지출과 고정비, 선택한 예상수입을 반영했어.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_reality_check(calc: dict) -> None:
    st.markdown(
        f"""
        <div class="soft-card">
            <h3>쫄지마 체크</h3>
            <div class="check-row"><span class="check-label">이번 달 부족 예상 금액</span><span class="check-value">{won(calc['shortage'])}</span></div>
            <div class="check-row"><span class="check-label">하루 사용 가능 금액</span><span class="check-value">{won(calc['daily_available'])}</span></div>
            <div class="check-row"><span class="check-label">단기 알바가 필요한 예상 일수</span><span class="check-value">{calc['part_time_days']}일</span></div>
            <div class="check-row"><span class="check-label">풀타임 복귀 필요도</span><span class="check-value">{calc['fulltime_need']}</span></div>
            <p class="mini-note">단기 알바는 하루 10만원 기준으로 가볍게 계산했어. 정확한 정답보다 움직일 타이밍을 보는 용도야.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


stored_state = streamlit_js_eval(
    js_expressions=f"localStorage.getItem('{LOCAL_STORAGE_KEY}') || '__JJOL_EMPTY__'",
    key="load_state",
)

if "state" not in st.session_state:
    st.session_state.state = default_state()
    st.session_state.storage_loaded = False

if not st.session_state.storage_loaded:
    if stored_state is None:
        st.info("브라우저 저장소를 확인하는 중이야.")
        st.stop()
    if stored_state != "__JJOL_EMPTY__":
        try:
            st.session_state.state = normalize_state(json.loads(stored_state))
        except json.JSONDecodeError:
            st.warning("브라우저에 저장된 데이터를 읽지 못해서 새 상태로 시작할게.")
            st.session_state.state = default_state()
    st.session_state.storage_loaded = True

state = st.session_state.state
calc = calculate(state)
render_top_image()
tabs = st.tabs(["대시보드", "자산 입력", "수입 모드", "고정비 입력", "지출 기록", "카테고리 분석", "데이터 관리"])

with tabs[0]:
    main_left, main_right = st.columns([1.45, 0.85], gap="large")
    with main_left:
        st.markdown(
            f"""
            <div class="runway-card">
                <div class="runway-label">생존 가능 개월 수</div>
                <div class="runway-value">{format_months(calc["runway_months"])}</div>
                <div class="runway-note">현재 자산, 이번 달 고정비, 기록된 지출, 선택한 수입 모드를 기준으로 계산했어. 월이 바뀌면 자산만 실제 잔액으로 갱신하면 돼.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with main_right:
        st.markdown(
            f"""
            <div class="hero-metric-card accent">
                <div class="hero-metric-label">이번 달 남은 돈</div>
                <div class="hero-metric-value">{won(calc["remaining_this_month"])}</div>
                <div class="hero-metric-note">수입 - 고정비 - 지출</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown(
            f"""
            <div class="hero-metric-card">
                <div class="hero-metric-label">총 자산</div>
                <div class="hero-metric-value">{won(calc["total_assets"])}</div>
                <div class="hero-metric-note">현재 입력한 잔액 기준</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    top_left, top_right = st.columns([1.05, 0.95], gap="large")
    with top_left:
        render_status_panel(calc)
    with top_right:
        render_reality_check(calc)

    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("생존 가능 일수", format_days(calc["survival_days"]))
    c2.metric("이번 달 예상 수입", won(calc["income"]))
    c3.metric("고정비 총액", won(calc["fixed_total"]))
    c4.metric("변동 지출 총액", won(calc["variable_total"]))

    st.markdown(
        f"""
        <div class="soft-card">
            <h3>가장 많이 쓴 카테고리</h3>
            <p class="insight-title">{calc['top_category']}</p>
            <p class="mini-note">이번 달 기록된 변동 지출 기준이야.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tabs[1]:
    st.subheader("현재 자산 입력")
    st.caption("지금 바로 쓸 수 있거나 받을 가능성이 높은 돈을 적어줘.")
    with st.form("asset_form"):
        new_assets = {}
        cols = st.columns(2)
        for index, name in enumerate(ASSET_FIELDS):
            with cols[index % 2]:
                new_assets[name] = st.number_input(name, min_value=0, value=plain_number(state["assets"].get(name, 0)), step=10_000, format="%d")
        if st.form_submit_button("자산 저장"):
            state["assets"] = new_assets
            persist_browser_state(state, "assets")
            st.success("자산을 이 브라우저에 저장했어.")

with tabs[2]:
    st.subheader("수입 모드 설정")
    st.caption("현재 상황에 가장 가까운 모드를 골라줘. 직접 입력도 가능해.")
    with st.form("income_form"):
        mode = st.radio("수입 모드", list(INCOME_MODES.keys()), index=list(INCOME_MODES.keys()).index(state["income_mode"]), horizontal=False)
        custom_income = state.get("custom_income", 0)
        if mode == "직접 입력 모드":
            custom_income = st.number_input("월 예상 수입", min_value=0, value=plain_number(custom_income), step=50_000, format="%d")
        else:
            st.info(f"선택한 모드의 기본 예상 수입은 {won(INCOME_MODES[mode])}이야.")
        if st.form_submit_button("수입 모드 저장"):
            state["income_mode"] = mode
            state["custom_income"] = plain_number(custom_income)
            persist_browser_state(state, "income")
            st.success("수입 모드를 이 브라우저에 저장했어.")

with tabs[3]:
    st.subheader("고정비 입력")
    st.caption("매달 거의 빠져나가는 돈을 적어줘. 불확실하면 보수적으로 넣는 편이 좋아.")
    with st.form("fixed_form"):
        new_fixed = {}
        cols = st.columns(2)
        for index, name in enumerate(FIXED_FIELDS):
            with cols[index % 2]:
                new_fixed[name] = st.number_input(name, min_value=0, value=plain_number(state["fixed_costs"].get(name, 0)), step=10_000, format="%d")
        if st.form_submit_button("고정비 저장"):
            state["fixed_costs"] = new_fixed
            persist_browser_state(state, "fixed")
            st.success("고정비를 이 브라우저에 저장했어.")

with tabs[4]:
    st.subheader("지출 기록")
    st.caption("오늘 쓴 돈을 가볍게 남겨줘. MVP에서는 이번 달 지출 합계 계산에 바로 반영돼.")
    with st.form("expense_form", clear_on_submit=True):
        e1, e2 = st.columns([0.8, 1.2])
        with e1:
            expense_date = st.date_input("날짜", value=date.today())
            amount = st.number_input("금액", min_value=0, value=0, step=1_000, format="%d")
        with e2:
            category = st.selectbox("카테고리", EXPENSE_CATEGORIES)
            memo = st.text_input("메모", placeholder="예: 점심, 약값, 장보기")
        if st.form_submit_button("지출 추가"):
            if amount <= 0:
                st.warning("금액을 1원 이상 입력해줘.")
            else:
                state["expenses"].append(
                    {
                        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                        "date": expense_date.isoformat(),
                        "amount": plain_number(amount),
                        "category": category,
                        "memo": memo.strip(),
                    }
                )
                persist_browser_state(state, f"expense_{expense_date.isoformat()}_{amount}")
                st.success("지출을 이 브라우저에 저장했어.")

    st.markdown("### 이번 달 지출")
    if not calc["month_expenses"]:
        st.info("아직 이번 달 지출 기록이 없어.")
    else:
        for expense in sorted(calc["month_expenses"], key=lambda item: item.get("date", ""), reverse=True):
            st.markdown(
                f"""
                <div class="expense-item">
                    <div class="expense-top"><span>{expense.get('category', '기타')}</span><span>{won(expense.get('amount', 0))}</span></div>
                    <div class="expense-bottom">{expense.get('date', '')} · {expense.get('memo', '') or '메모 없음'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

with tabs[5]:
    st.subheader("카테고리 분석")
    st.caption("1단계에서는 간단한 순위로만 보여줘. 차트와 월별 비교는 2단계에서 확장하면 좋아.")
    if not calc["category_map"]:
        st.info("분석할 지출 기록이 아직 없어.")
    else:
        sorted_categories = sorted(calc["category_map"].items(), key=lambda item: item[1], reverse=True)
        max_value = max(value for _, value in sorted_categories) or 1
        for category, amount in sorted_categories:
            percent = int((amount / max_value) * 100)
            st.markdown(
                f"""
                <div class="soft-card" style="margin-bottom:12px; padding:16px 18px;">
                    <div class="check-row" style="border-bottom:0; padding:0 0 8px;"><span class="check-label">{category}</span><span class="check-value">{won(amount)}</span></div>
                    <div class="bar-wrap" style="background:#eef2f8; margin:0;"><div class="bar-fill" style="width:{percent}%; background:#071d49;"></div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

with tabs[6]:
    st.subheader("데이터 관리")
    st.caption("개인 데이터는 서버 파일에 저장하지 않고, 지금 접속한 브라우저의 localStorage에만 저장돼.")

    backup_name = f"jjol-jima-backup-{date.today().isoformat()}.json"
    st.download_button(
        "백업 JSON 다운로드",
        data=json.dumps(normalize_state(state), ensure_ascii=False, indent=2),
        file_name=backup_name,
        mime="application/json",
    )

    st.markdown("### 백업 불러오기")
    uploaded_file = st.file_uploader("백업 JSON 파일 선택", type=["json"])
    if uploaded_file is not None:
        if st.button("백업 데이터로 복원"):
            try:
                restored = normalize_state(json.loads(uploaded_file.getvalue().decode("utf-8")))
            except (UnicodeDecodeError, json.JSONDecodeError):
                st.error("백업 파일을 읽지 못했어. JSON 파일인지 확인해줘.")
            else:
                st.session_state.state = restored
                state = st.session_state.state
                persist_browser_state(state, "restore")
                st.success("백업 데이터를 이 브라우저에 복원했어. 대시보드가 곧 새 값으로 계산돼.")

    st.markdown("### 전체 초기화")
    confirm_reset = st.checkbox("정말로 이 브라우저에 저장된 쫄지마 데이터를 지울게.")
    if st.button("전체 초기화", disabled=not confirm_reset):
        st.session_state.state = default_state()
        state = st.session_state.state
        clear_browser_state()
        st.success("이 브라우저의 쫄지마 데이터를 초기화했어.")

st.markdown("<p class='mini-note'>은행 연동과 API는 사용하지 않아. 입력 데이터는 Streamlit 서버 파일이 아니라 이 브라우저의 localStorage에 저장돼.</p>", unsafe_allow_html=True)









