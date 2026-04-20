from __future__ import annotations

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="英国留学费用说明",
    page_icon="🇬🇧",
    layout="wide",
)


EXCHANGE_RATES = {
    "近一年最低汇率": 8.9124,
    "近一年最高汇率": 9.8474,
}
EXCHANGE_RATES["最低最高折中价"] = round(
    (EXCHANGE_RATES["近一年最低汇率"] + EXCHANGE_RATES["近一年最高汇率"]) / 2,
    4,
)

RATE_SOURCE_NOTE = (
    "人民币换算默认使用近一年英镑兑人民币的三个参考值："
    "最低 8.9124、最高 9.8474、折中 9.3799。"
)

RENT_INSTALLMENTS = [
    {"项目": "房租定金", "日期": "已支付/待确认", "英镑金额": 250.00},
    {"项目": "Rent Instalment 1", "日期": "22/09/26", "英镑金额": 1797.75},
    {"项目": "Rent Instalment 2", "日期": "01/10/26", "英镑金额": 1797.75},
    {"项目": "Rent Instalment 3", "日期": "08/12/26", "英镑金额": 1797.75},
    {"项目": "Rent Instalment 4", "日期": "05/01/27", "英镑金额": 1797.75},
    {"项目": "Rent Instalment 5", "日期": "02/02/27", "英镑金额": 1797.75},
    {"项目": "Rent Instalment 6", "日期": "02/03/27", "英镑金额": 1797.75},
    {"项目": "Rent Instalment 7", "日期": "13/04/27", "英镑金额": 1198.50},
]


def format_gbp(value: float) -> str:
    return f"£{value:,.2f}"


def format_cny(value: float) -> str:
    return f"¥{value:,.2f}"


def convert_table(amount_gbp: float) -> pd.DataFrame:
    rows = []
    for label, rate in EXCHANGE_RATES.items():
        rows.append(
            {
                "汇率方案": label,
                "汇率": f"1 GBP = {rate:.4f} CNY",
                "人民币金额": format_cny(amount_gbp * rate),
            }
        )
    return pd.DataFrame(rows)


def enrich_currency_table(df: pd.DataFrame, amount_column: str = "英镑金额") -> pd.DataFrame:
    enriched = df.copy()
    for label, rate in EXCHANGE_RATES.items():
        enriched[f"{label}人民币"] = enriched[amount_column].apply(lambda value: round(value * rate, 2))
    return enriched


def show_amount_block(title: str, amount_gbp: float, note: str | None = None) -> None:
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown(f"### {title}")
        st.metric("英镑金额", format_gbp(amount_gbp))
        if note:
            st.markdown(note)
    with right:
        st.dataframe(convert_table(amount_gbp), use_container_width=True, hide_index=True)


def show_original_text(title: str, body: str) -> None:
    with st.expander(f"查看原始说明：{title}", expanded=False):
        st.write(body)


def section_overview() -> None:
    tuition = 24300.0
    rent_total = sum(item["英镑金额"] for item in RENT_INSTALLMENTS)
    visa = 558.0
    ihs = 1552.0
    living_monthly = 800.0
    key_total = tuition + rent_total + visa + ihs

    st.title("英国留学费用交互式说明")
    st.caption("给妈妈看的清晰版，边栏可以切换不同费用项目。")

    st.markdown(
        """
        这个页面把英国留学涉及到的主要费用分开说明，所有英镑项目都会同步展示三档人民币参考价格：

        - 近一年最低汇率
        - 近一年最高汇率
        - 最低与最高之间的折中价
        """
    )

    st.info(RATE_SOURCE_NOTE)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("折后学费", format_gbp(tuition))
    col2.metric("总房租", format_gbp(rent_total))
    col3.metric("签证 + 医疗附加费", format_gbp(visa + ihs))
    col4.metric("主要固定支出合计", format_gbp(key_total))

    summary = pd.DataFrame(
        [
            {"项目": "学费（折后）", "英镑金额": tuition},
            {"项目": "房租总额（含定金）", "英镑金额": rent_total},
            {"项目": "签证费", "英镑金额": visa},
            {"项目": "医疗附加费（IHS）", "英镑金额": ihs},
            {"项目": "生活费参考（每月）", "英镑金额": living_monthly},
        ]
    )
    styled = enrich_currency_table(summary)
    for label in EXCHANGE_RATES:
        styled[f"{label}人民币"] = styled[f"{label}人民币"].apply(format_cny)
    styled["英镑金额"] = styled["英镑金额"].apply(format_gbp)
    st.dataframe(styled, use_container_width=True, hide_index=True)


def section_rent() -> None:
    st.title("房租")
    total_rent = sum(item["英镑金额"] for item in RENT_INSTALLMENTS)
    installment_total = total_rent - 250.0

    st.markdown("房租分为一笔定金和后续分期付款。下面这张表已经把你提供的补充图片内容并进来了。")

    col1, col2, col3 = st.columns(3)
    col1.metric("房租定金", format_gbp(250.0))
    col2.metric("分期房租合计", format_gbp(installment_total))
    col3.metric("房租总额", format_gbp(total_rent))

    rent_df = enrich_currency_table(pd.DataFrame(RENT_INSTALLMENTS))
    display_df = rent_df.copy()
    display_df["英镑金额"] = display_df["英镑金额"].apply(format_gbp)
    for label in EXCHANGE_RATES:
        display_df[f"{label}人民币"] = display_df[f"{label}人民币"].apply(format_cny)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    show_amount_block("房租总额对应人民币", total_rent)
    show_original_text("房租", "房租定金250镑")


def section_visa() -> None:
    st.title("签证费")
    show_amount_block("签证费用", 558.0, "原文：签证费用558镑")
    st.markdown("另外还有一项固定人民币支出：**体检费用 550 人民币**。")
    show_original_text("签证和体检", "签证费用558镑\n体检费用550人民币")


def section_ihs() -> None:
    st.title("医疗附加费")
    show_amount_block(
        "医疗附加费（IHS）",
        1552.0,
        "2年共1552镑。对于学生签证，费用为776英镑/年。",
    )
    show_original_text(
        "医疗附加费",
        "医疗附加费 （IHS）：2年共1552镑，这是用于让你在英国享受国民医疗服务体系（NHS）的费用，"
        "对于学生签证，费用为776英镑/年。这笔费用会根据你的课程时长自动计算。",
    )


def section_tuition() -> None:
    st.title("学费")
    discounted = 24300.0
    original = 27000.0
    first_term = discounted * 0.6
    second_term = discounted * 0.4

    col1, col2, col3 = st.columns(3)
    col1.metric("折后学费", format_gbp(discounted))
    col2.metric("原价", format_gbp(original))
    col3.metric("优惠幅度", "10%")

    show_amount_block(
        "一年学费（折后）",
        discounted,
        "原价27000镑一年，西浦优惠10%，9月缴纳。学生可以选择全额付款，或分期付款。",
    )

    installment_df = pd.DataFrame(
        [
            {"缴费方式": "第一学期支付 60%", "英镑金额": first_term},
            {"缴费方式": "第二学期支付 40%", "英镑金额": second_term},
        ]
    )
    installment_df = enrich_currency_table(installment_df)
    display_df = installment_df.copy()
    display_df["英镑金额"] = display_df["英镑金额"].apply(format_gbp)
    for label in EXCHANGE_RATES:
        display_df[f"{label}人民币"] = display_df[f"{label}人民币"].apply(format_cny)

    st.markdown("### 分期付款参考")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    show_original_text(
        "学费",
        "学费：24300镑，原价27000镑一年，西浦优惠10%，9月缴纳（9月汇率最贵）"
        "学生可以选择全额付款，或分期付款，第一学期支付60%，第二学期支付40%。",
    )


def section_living() -> None:
    st.title("生活费")
    monthly_low = 650.0
    monthly_plan = 800.0

    col1, col2 = st.columns(2)
    with col1:
        show_amount_block("一个月生活费参考（650镑）", monthly_low)
    with col2:
        show_amount_block("一个月生活费计划（800镑）", monthly_plan)

    living_df = pd.DataFrame(
        [
            {"方案": "按 650 镑 / 月", "英镑金额": monthly_low, "备注": "正常吃喝，不娱乐，不买东西"},
            {"方案": "按 800 镑 / 月", "英镑金额": monthly_plan, "备注": "目前更稳妥的预算"},
            {"方案": "按 650 镑 / 月，9个月", "英镑金额": monthly_low * 9, "备注": "用于对照存款证明公式"},
            {"方案": "按 800 镑 / 月，9个月", "英镑金额": monthly_plan * 9, "备注": "如果按自己的计划估算"},
        ]
    )
    living_df = enrich_currency_table(living_df)
    display_df = living_df.copy()
    display_df["英镑金额"] = display_df["英镑金额"].apply(format_gbp)
    for label in EXCHANGE_RATES:
        display_df[f"{label}人民币"] = display_df[f"{label}人民币"].apply(format_cny)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    show_original_text(
        "生活费",
        "生活费：据jj说他弟弟在那个村里一个月正常吃喝不娱乐不买东西六百五十镑左右，"
        "他说我要800镑，但我觉得可以先用一个月做个实验",
    )


def section_deposit(subsection: str) -> None:
    st.title("存款证明")

    if subsection == "需要存多少":
        tuition = 24300.0
        non_london_living = 1136.0 * 9
        london_living = 1483.0 * 9
        safety_buffer = 3000.0

        scenarios = pd.DataFrame(
            [
                {
                    "方案": "非伦敦地区：一年学费 + 9个月生活费",
                    "英镑金额": tuition + non_london_living,
                    "备注": "24300 + 1136 x 9",
                },
                {
                    "方案": "非伦敦地区：再加 3000 镑缓冲",
                    "英镑金额": tuition + non_london_living + safety_buffer,
                    "备注": "更稳妥",
                },
                {
                    "方案": "伦敦地区：一年学费 + 9个月生活费",
                    "英镑金额": tuition + london_living,
                    "备注": "24300 + 1483 x 9",
                },
                {
                    "方案": "伦敦地区：再加 3000 镑缓冲",
                    "英镑金额": tuition + london_living + safety_buffer,
                    "备注": "更稳妥",
                },
            ]
        )
        scenarios = enrich_currency_table(scenarios)
        display_df = scenarios.copy()
        display_df["英镑金额"] = display_df["英镑金额"].apply(format_gbp)
        for label in EXCHANGE_RATES:
            display_df[f"{label}人民币"] = display_df[f"{label}人民币"].apply(format_cny)
        st.markdown("### 存款金额参考")
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "方案": st.column_config.TextColumn("方案", width="large"),
                "英镑金额": st.column_config.TextColumn("英镑金额", width="small"),
                "备注": st.column_config.TextColumn("备注", width="medium"),
                "近一年最低汇率人民币": st.column_config.TextColumn("近一年最低汇率人民币", width="medium"),
                "近一年最高汇率人民币": st.column_config.TextColumn("近一年最高汇率人民币", width="medium"),
                "最低最高折中价人民币": st.column_config.TextColumn("最低最高折中价人民币", width="medium"),
            },
        )
        st.markdown("另外，原文还提到：**西浦 2+2 的同学一般建议存 35 - 40 万人民币。**")
        show_original_text(
            "存多少钱",
            "存款证明：存款金额得是一年学费加上9个月的生活费。目前是抽查形式，流水单、存单、存折都能用。"
            "西浦2+2的同学一般建议存35 - 40万人民币。\n\n"
            "存多少钱：原则上，存款金额不能低于入学第一年的学费加上学校所在地区的生活费。"
            "英国各地区每月生活费标准不同，伦敦地区每月1483英镑，非伦敦地区每月1136英镑。"
            "考虑到汇率变动，建议在这个基础上加3000英镑左右。简单来说，就是："
            "存款金额 = 一年学费 + 9个月生活费。",
        )

    elif subsection == "存定期还是活期":
        st.markdown(
            """
            ### 存款形式

            - 活期和定期都可以
            - 不过建议存定期
            - 一般存 3 个月定期比较好
            - 存款不限币种，英镑、人民币都没问题
            """
        )
        show_original_text(
            "存定期还是活期，币种有要求吗？",
            "活期和定期都可以，不过建议存定期，一般存3个月定期比较好。"
            "存款不限币种，英镑、人民币都没问题。",
        )

    elif subsection == "保证金要存多久":
        st.markdown(
            """
            ### 保证金存期

            - 官方规定：必须连续存满至少 28 天
            - 为了保险起见：最好满足 1 个月存期
            - 9 月正课的学生：最晚 6 月存
            - 建议存期：3 个月
            - 可以选择“到期自动约转”
            """
        )
        show_original_text(
            "保证金要存多久",
            "官方规定保证金必须连续存满至少28天，为了保险起见，最好满足1个月存期。"
            "9月正课的学生最晚6月存，存期3个月，选择“到期自动约转”。",
        )

    elif subsection == "什么时候开存款证明":
        st.markdown(
            """
            ### 开具时间

            - 得在存款满 28 天之后
            - 并且在递交签证日之前的 1 个月（31 天）内开具才有效
            - 原文建议：西浦同学拿到 CAS 后去开就行
            """
        )
        show_original_text(
            "什么时候开存款证明",
            "得在存款满28天之后，并且在递交签证日之前的1个月（31天）内开具才有效。"
            "西浦同学拿到CAS（7.15期末成绩出来后一周出录取通知）后去开就行。",
        )

    else:
        st.markdown(
            """
            ### 银行选择

            中国银行、工商银行、建设银行、农业银行等大型银行都可以。
            """
        )
        show_original_text(
            "存什么银行好",
            "中国银行、工商银行、建设银行、农业银行等大型银行都可以。",
        )


st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(187, 215, 238, 0.55), transparent 28%),
            linear-gradient(180deg, #f7f4ef 0%, #eef4f7 100%);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16324f 0%, #224b69 100%);
    }
    [data-testid="stSidebar"] * {
        color: #f8fafc;
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.76);
        border: 1px solid rgba(22, 50, 79, 0.08);
        border-radius: 18px;
        padding: 14px;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.sidebar.title("费用导航")
section = st.sidebar.radio(
    "请选择要看的项目",
    [
        "总览",
        "房租",
        "签证费",
        "医疗附加费",
        "学费",
        "生活费",
        "存款证明",
    ],
)

deposit_subsection = "需要存多少"
if section == "存款证明":
    deposit_subsection = st.sidebar.radio(
        "存款证明细分选项",
        [
            "需要存多少",
            "存定期还是活期",
            "保证金要存多久",
            "什么时候开存款证明",
            "存什么银行好",
        ],
    )

st.sidebar.markdown("---")
st.sidebar.caption("说明：英镑项目全部按三档汇率自动换算成人民币。")
st.sidebar.caption(RATE_SOURCE_NOTE)


if section == "总览":
    section_overview()
elif section == "房租":
    section_rent()
elif section == "签证费":
    section_visa()
elif section == "医疗附加费":
    section_ihs()
elif section == "学费":
    section_tuition()
elif section == "生活费":
    section_living()
else:
    section_deposit(deposit_subsection)
