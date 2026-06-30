
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data_loader import load_csv

st.set_page_config(
    page_title="Спортмастер — Аналитика заказов",
    page_icon="📊",
    layout="wide"
)

def load_css(path):
    with open(path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("assets/styles.css")

st.markdown("""
<div style="padding-bottom:1rem;">
<h1 style="margin-bottom:0;">📊 Аналитический дашборд «Спортмастер»</h1>
<p style="color:#6B7280;font-size:18px;">
Аналитика заказов, кликов и поведения пользователей
</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Загрузите CSV-файл", type=["csv"])

if uploaded_file is None:
    st.info("Загрузите CSV-файл для начала анализа.")
    st.stop()

df = load_csv(uploaded_file)
df["time"] = pd.to_datetime(df["time"], errors="coerce")
df["Дата"] = df["time"].dt.date

with st.sidebar:
    st.header("⚙️ Фильтры")

    versions = sorted(df["site_version"].dropna().unique())
    selected_versions = st.multiselect(
        "Версия сайта",
        versions,
        default=versions
    )

    events = sorted(df["title"].dropna().unique())
    selected_events = st.multiselect(
        "Тип события",
        events,
        default=events
    )

filtered = df[
    df["site_version"].isin(selected_versions)
    & df["title"].isin(selected_events)
]

shows = (filtered["title"]=="banner_show").sum()
clicks = (filtered["title"]=="banner_click").sum()
orders_df = filtered[(filtered["title"]=="order") | (filtered["target"]==1)]
orders = len(orders_df)
conversion = orders/clicks*100 if clicks else 0

st.markdown("## 📈 Ключевые показатели")

c1,c2,c3,c4 = st.columns(4)

c1.metric("👁 Показы", f"{shows:,}".replace(","," "))
c2.metric("🖱 Клики", f"{clicks:,}".replace(","," "))
c3.metric("🛒 Заказы", f"{orders:,}".replace(","," "))
c4.metric("🎯 Конверсия", f"{conversion:.2f}%")

left,right = st.columns(2)

with left:
    funnel = pd.DataFrame({
        "Этап":["Показы","Клики","Заказы"],
        "Количество":[shows,clicks,orders]
    })
    fig = px.funnel(
        funnel,
        x="Количество",
        y="Этап",
        color="Этап",
        title="Воронка продаж"
    )
    fig.update_layout(
        template="plotly_white",
        height=430,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    device = filtered.groupby("site_version").size().reset_index(name="События")
    fig = px.bar(
        device,
        x="site_version",
        y="События",
        color="site_version",
        title="Сравнение версий сайта"
    )
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Версия сайта",
        height=430,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

col1,col2 = st.columns([2,1])

with col1:
    trend = orders_df.groupby("Дата").size().reset_index(name="Заказы")
    fig = px.line(
        trend,
        x="Дата",
        y="Заказы",
        markers=True,
        title="Динамика заказов"
    )
    fig.update_layout(template="plotly_white", height=420)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    events_df = filtered.groupby("title").size().reset_index(name="Количество")
    fig = px.pie(
        events_df,
        names="title",
        values="Количество",
        hole=0.55,
        title="Структура событий"
    )
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("## 🧠 Краткие выводы")

best_site = (
    filtered.groupby("site_version")
    .size()
    .sort_values(ascending=False)
    .index[0]
)

top_event = (
    filtered.groupby("title")
    .size()
    .sort_values(ascending=False)
    .index[0]
)

st.success(f"""
• Всего обработано **{len(filtered):,}** событий.

• Наиболее активная версия сайта: **{best_site}**.

• Самое частое событие: **{top_event}**.

• Конверсия кликов в заказ составляет **{conversion:.2f}%**.
""".replace(",", " "))

st.markdown("## 📋 Предпросмотр данных")

preview_rows = st.slider(
    "Сколько строк показать?",
    min_value=100,
    max_value=5000,
    value=500,
    step=100
)

st.dataframe(
    filtered.head(preview_rows),
    use_container_width=True,
    height=500
)

st.caption(f"Показано {preview_rows} строк из {len(filtered):,}".replace(",", " "))

st.download_button(
    "⬇ Скачать отфильтрованные данные CSV",
    filtered.to_csv(index=False).encode("utf-8-sig"),
    "filtered_sportmaster_data.csv",
    "text/csv"
)