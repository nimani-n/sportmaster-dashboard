import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Аналитика заказов и кликов", layout="wide")

st.title("📊 Аналитика заказов и кликов")
st.caption("Интерактивный Python-dashboard: показы баннеров, клики, покупки, mobile/desktop и динамика заказов.")

REQUIRED_COLUMNS = {"site_version", "time", "title", "target"}

uploaded_file = st.file_uploader("Загрузите CSV-файл product_apr", type=["csv"])

if uploaded_file is None:
    st.info("Загрузите CSV с колонками: site_version, time, title, target")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception:
    uploaded_file.seek(0)
    df = pd.read_csv(uploaded_file, sep=";")

missing = REQUIRED_COLUMNS - set(df.columns)
if missing:
    st.error(f"В файле не хватает колонок: {', '.join(missing)}")
    st.write("Найденные колонки:", list(df.columns))
    st.stop()

# Подготовка данных
df = df.copy()
df["time"] = pd.to_datetime(df["time"], errors="coerce")
df["date"] = df["time"].dt.date

st.sidebar.header("Фильтры")
site_options = sorted(df["site_version"].dropna().unique())
selected_sites = st.sidebar.multiselect("Версия сайта", site_options, default=site_options)

event_options = sorted(df["title"].dropna().unique())
selected_events = st.sidebar.multiselect("Тип события", event_options, default=event_options)

filtered = df[df["site_version"].isin(selected_sites) & df["title"].isin(selected_events)]

shows = len(filtered[filtered["title"] == "banner_show"])
clicks = len(filtered[filtered["title"] == "banner_click"])
orders_df = filtered[(filtered["title"] == "order") | (filtered["target"] == 1)]
orders = len(orders_df)
conversion = (orders / clicks * 100) if clicks else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Показы баннеров", f"{shows:,}".replace(",", " "))
c2.metric("Клики по баннерам", f"{clicks:,}".replace(",", " "))
c3.metric("Покупки", f"{orders:,}".replace(",", " "))
c4.metric("Конверсия клик → покупка", f"{conversion:.1f}%".replace(".", ","))

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Путь клиента: показы → клики → покупки")
    funnel_df = pd.DataFrame({
        "Этап": ["Показы", "Клики", "Покупки"],
        "Количество": [shows, clicks, orders],
    })
    fig = px.funnel(funnel_df, x="Количество", y="Этап", title="Воронка событий")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Клики по версиям сайта")
    clicks_site = filtered[filtered["title"] == "banner_click"].groupby("site_version").size().reset_index(name="Клики")
    fig = px.bar(clicks_site, x="site_version", y="Клики", text="Клики", title="Mobile vs Desktop: клики")
    st.plotly_chart(fig, use_container_width=True)

left2, right2 = st.columns(2)

with left2:
    st.subheader("Продажи по версиям сайта")
    orders_site = orders_df.groupby("site_version").size().reset_index(name="Покупки")
    fig = px.bar(orders_site, x="site_version", y="Покупки", text="Покупки", title="Mobile vs Desktop: покупки")
    st.plotly_chart(fig, use_container_width=True)

with right2:
    st.subheader("Динамика заказов")
    orders_day = orders_df.dropna(subset=["date"]).groupby("date").size().reset_index(name="Покупки")
    fig = px.line(orders_day, x="date", y="Покупки", markers=True, title="Количество заказов по датам")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Предпросмотр данных")
st.dataframe(filtered.head(100), use_container_width=True)
