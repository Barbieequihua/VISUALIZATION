import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import streamlit as st
st.set_page_config(page_title="Health Insights Dashboard", layout="wide")

st.markdown("""
    <style>
        /* Apuntamos al contenedor del slider y forzamos el color en todos sus estados */
        [data-baseweb="slider"] div[role="slider"] {
            background-color: #6d28d9 !important;
        }
        
        /* Barra de progreso activa */
        [data-baseweb="slider"] > div > div > div:nth-child(2) {
            background-color: #6d28d9 !important;
        }

        /* La bolita del selector */
        [data-baseweb="slider"] button {
            background-color: #6d28d9 !important;
            border: 2px solid #6d28d9 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #ffffff;
    }
    .title-banner {
        background: linear-gradient(90deg, #f5f3ff 0%, #f3e8ff 100%);
        padding: 14px 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid #e9d5ff;
    }
    .title-banner h1 {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #4c1d95 !important;
        margin: 0 !important;
    }
    .title-banner p {
        font-size: 12px !important;
        color: #6b7280 !important;
        margin: 6px 0 0 0 !important;
    }
    </style>
""", unsafe_allow_html=True)


cases = pd.read_csv("Cases_cleanok.csv")
cases['date'] = pd.to_datetime(cases['date'])
cases['year'] = cases['date'].dt.year
cases['cases'] = pd.to_numeric(cases['cases'], errors='coerce').fillna(0)
cases['population'] = pd.to_numeric(cases['population'], errors='coerce').fillna(1)
cases['type'] = cases['type'].str.lower().str.strip()

access = pd.read_csv("Access_cleanok.csv")
long = pd.read_csv("long_covid_clean.csv")

access['date'] = pd.to_datetime(access['Time Period End Date'], errors='coerce')
access['year'] = access['date'].dt.year
year_extracted = access['Time Period End Date'].str.extract(r'(\d{4})')[0]
access['year'] = access['year'].fillna(year_extracted.astype(float))
access['Indicator'] = access['Indicator'].str.lower().str.strip()

long['year'] = long['Time Period Label'].str.extract(r'(\d{4})')[0].astype(int)

st.sidebar.header("Filters")
selected_year = st.sidebar.selectbox("Year Filter", ["2020", "2021", "2020-2021"])
selected_type = st.sidebar.selectbox("Case Type", ["confirmed","death","both"])



st.markdown("""
    <div class="title-banner">
        <h1>COVID-19 Health Insights Dashboard</h1>
        <p>Comprehensive analysis tool evaluating USA covid cases, chronic long-term conditions (2022), and medical service accessibility from 2020 - 2021</p>
    </div>
""", unsafe_allow_html=True)

if selected_year == "2020-2021":

    df_us = cases[(cases['year'].isin([2020, 2021])) & (cases['country'].str.upper()=="US")]
else:
    df_us = cases[(cases['year']==int(selected_year)) & (cases['country'].str.upper()=="US")]

confirmed = df_us[df_us['type'].str.contains("confirmed")]['cases'].sum()
deaths = df_us[df_us['type'].str.contains("death")]['cases'].sum()


df_long_year = long[(long['year']==2022) & (long['Group'].str.contains("Age", case=False))]
ever_df = df_long_year[df_long_year['Indicator'].str.contains("ever experienced", case=False)]
curr_df = df_long_year[df_long_year['Indicator'].str.contains("currently experiencing", case=False)]
act_df  = df_long_year[df_long_year['Indicator'].str.contains("activity limitations", case=False)]

ever_max = ever_df.groupby("Subgroup", as_index=False)["Value"].mean().loc[lambda d: d["Value"].idxmax()] if not ever_df.empty else None
curr_max = curr_df.groupby("Subgroup", as_index=False)["Value"].mean().loc[lambda d: d["Value"].idxmax()] if not curr_df.empty else None
act_max  = act_df.groupby("Subgroup", as_index=False)["Value"].mean().loc[lambda d: d["Value"].idxmax()] if not act_df.empty else None


if selected_year == "2020-2021":
    df_access_f = access[
        (access['year'].isin([2020, 2021])) &
        (access['Group'] == "By State")
    ].copy()
else:
    df_access_f = access[
        (access['year'] == int(selected_year)) &
        (access['Group'] == "By State")
    ].copy()

df_access_f["date"] = pd.to_datetime(df_access_f["date"])

df_access_f = df_access_f.groupby(["Indicator", "Subgroup"], as_index=False)["Value"].mean()


df_del = df_access_f[df_access_f['Indicator'].str.contains("delay", case=False)]
df_not = df_access_f[df_access_f['Indicator'].str.contains("did not", case=False)]


if not df_del.empty:
    del_max = df_del.loc[df_del["Value"].idxmax()]
else:
    del_max = {"Value": 0.0, "Subgroup": "No Data"}

if not df_not.empty:
    not_max = df_not.loc[df_not["Value"].idxmax()]
else:
    not_max = {"Value": 0.0, "Subgroup": "No Data"}
    
# KPIs 
st.markdown("Per year metrics in USA")
kpi_cols = st.columns(7)
labels = ["Confirmed", "Deaths", "Ever Long COVID", "Current Long COVID", "Activity Limits", "Delayed Care", "Omitted Care"]
values = [
    (confirmed, "USA", False),
    (deaths, "USA", False),
    (ever_max["Value"] if ever_max is not None else 0, ever_max["Subgroup"] if ever_max is not None else "", True),
    (curr_max["Value"] if curr_max is not None else 0, curr_max["Subgroup"] if curr_max is not None else "", True),
    (act_max["Value"] if act_max is not None else 0, act_max["Subgroup"] if act_max is not None else "", True),
    (del_max["Value"] if del_max is not None else 0, del_max["Subgroup"] if del_max is not None else "", True),
    (not_max["Value"] if not_max is not None else 0, not_max["Subgroup"] if not_max is not None else "", True)
]

for col, label, (val, subgroup, is_percent) in zip(kpi_cols, labels, values):
    with col:
        val_str = f"{val:,}" if not is_percent else f"{val:.1f}%"
        st.markdown(f"""
        <div style="background:#f9f5ff; padding:10px; border-radius:8px; border-left:4px solid #6d28d9;">
            <div style="font-size:11px; font-weight:600; color:#6d28d9;">{label}</div>
            <div style="font-size:18px; font-weight:700; color:#4c1d95;">{val_str}</div>
            <div style="font-size:9px; color:#6b7280;">{subgroup}</div>
        </div>
        """, unsafe_allow_html=True)


st.subheader("COVID-19 Cases Overview")
st.caption("Breakdown of Confirmed and Fatality cases in USA")


def format_number(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    else:
        return str(int(n))

if selected_year == "2020-2021":
    if selected_type == "both":
        df_us_selected = cases[
            (cases['year'].isin([2020, 2021])) &
            (cases['country'].str.upper() == "US") &
            (cases['type'].isin(["confirmed","death"]))
        ].copy()
    else:
        df_us_selected = cases[
            (cases['year'].isin([2020, 2021])) &
            (cases['country'].str.upper() == "US") &
            (cases['type'] == selected_type)
        ].copy()
else:
    if selected_type == "both":
        df_us_selected = cases[
            (cases['year'] == int(selected_year)) &
            (cases['country'].str.upper() == "US") &
            (cases['type'].isin(["confirmed","death"]))
        ].copy()
    else:
        df_us_selected = cases[
            (cases['year'] == int(selected_year)) &
            (cases['country'].str.upper() == "US") &
            (cases['type'] == selected_type)
        ].copy()
df_us_selected['month'] = df_us_selected['date'].dt.to_period("M").dt.to_timestamp()


all_months = pd.date_range(
    df_us_selected['month'].min(),
    df_us_selected['month'].max(),
    freq="MS"
)

df_monthly_control = (
    df_us_selected.groupby("month", as_index=False)["cases"].sum()
    .set_index("month")
    .reindex(all_months, fill_value=0)
    .reset_index()
    .rename(columns={"index": "month"})
    .sort_values("month")
)

months_list = df_monthly_control['month'].tolist()

if "current_year_filter" not in st.session_state:
    st.session_state.current_year_filter = selected_year
    st.session_state.selected_cut = months_list[-1]

if st.session_state.current_year_filter != selected_year:
    st.session_state.current_year_filter = selected_year
    st.session_state.selected_cut = months_list[-1]

st.session_state.selected_cut = pd.to_datetime(st.session_state.selected_cut).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

min_dataset_month = pd.to_datetime(min(months_list)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
max_dataset_month = pd.to_datetime(max(months_list)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

if st.session_state.selected_cut < min_dataset_month:
    st.session_state.selected_cut = min_dataset_month
elif st.session_state.selected_cut > max_dataset_month:
    st.session_state.selected_cut = max_dataset_month

col_left, col_right = st.columns([1, 1.8], gap="large")

with col_right:
    fig = go.Figure()

    if selected_type == "both":
        df_conf = df_us_selected[df_us_selected['type']=="confirmed"].groupby("month", as_index=False)["cases"].sum().sort_values("month")
        df_death = df_us_selected[df_us_selected['type']=="death"].groupby("month", as_index=False)["cases"].sum().sort_values("month")


        df_conf_purple = df_conf[df_conf['month'] <= st.session_state.selected_cut]
        fig.add_trace(go.Scatter(
            x=df_conf_purple['month'], y=df_conf_purple['cases'],
            customdata=df_conf_purple['month'].dt.strftime('%Y-%m-%d'),
            mode="lines+markers", name="Confirmed Cases",
            line=dict(color="#6d28d9", width=2), 
            marker=dict(size=6, color="#6d28d9")
        ))
        
  
        df_conf_gray = df_conf[df_conf['month'] >= st.session_state.selected_cut]
        if len(df_conf_gray) > 1:
            fig.add_trace(go.Scatter(
                x=df_conf_gray['month'], y=df_conf_gray['cases'],
                mode="lines", name="Confirmed (Remaining)",
                line=dict(color="#cbd5e1", width=2, dash="dot"), 
                showlegend=False
            ))

        df_death_purple = df_death[df_death['month'] <= st.session_state.selected_cut]
        fig.add_trace(go.Scatter(
            x=df_death_purple['month'], y=df_death_purple['cases'],
            customdata=df_death_purple['month'].dt.strftime('%Y-%m-%d'),
            mode="lines+markers", name="Deaths", yaxis="y2",
            line=dict(color="#a78bfa", width=2),
            marker=dict(size=6, color="#a78bfa")
        ))
        
        df_death_gray = df_death[df_death['month'] >= st.session_state.selected_cut]
        if len(df_death_gray) > 1:
            fig.add_trace(go.Scatter(
                x=df_death_gray['month'], y=df_death_gray['cases'],
                mode="lines", name="Deaths (Remaining)", yaxis="y2",
                line=dict(color="#e2e8f0", width=2, dash="dot"),
                showlegend=False
            ))
        
        max_vertical_line = float(df_conf['cases'].max()) if not df_conf.empty else 1.0

    else:
  
        df_single = df_us_selected.groupby("month", as_index=False)["cases"].sum().sort_values("month")
        
        df_single_purple = df_single[df_single['month'] <= st.session_state.selected_cut]
        fig.add_trace(go.Scatter(
            x=df_single_purple['month'], y=df_single_purple['cases'],
            customdata=df_single_purple['month'].dt.strftime('%Y-%m-%d'),
            mode="lines+markers", name=f"{selected_type.capitalize()} Cases",
            line=dict(color="#6d28d9", width=2),
            marker=dict(size=6, color="#6d28d9")
        ))
        
        df_single_gray = df_single[df_single['month'] >= st.session_state.selected_cut]
        if len(df_single_gray) > 1:
            fig.add_trace(go.Scatter(
                x=df_single_gray['month'], y=df_single_gray['cases'],
                mode="lines", name=f"{selected_type.capitalize()} (Remaining)",
                line=dict(color="#cbd5e1", width=2, dash="dot"),
                showlegend=False
            ))
        
        max_vertical_line = float(df_single['cases'].max()) if not df_single.empty else 1.0


    fig.add_shape(
        type="line",
        x0=st.session_state.selected_cut, x1=st.session_state.selected_cut,
        y0=0, y1=max_vertical_line,
        line=dict(color="#1e293b", dash="dash", width=1.5)
    )

    if selected_type == "both":
        yaxis_layout = dict(
            title=dict(text="Confirmed Cases", font=dict(color="#6d28d9", size=11, family="Inter")),
            tickfont=dict(color="#6d28d9", size=10), showgrid=False
        )
        yaxis2_layout = dict(
            title=dict(text="Deaths", font=dict(color="#a78bfa", size=11, family="Inter")),
            tickfont=dict(color="#a78bfa", size=10), overlaying="y", side="right", showgrid=False
        )
    else:
        yaxis_layout = dict(
            title=dict(text=f"{selected_type.capitalize()} Cases", font=dict(color="#6e6e6e", size=11, family="Inter")),
            tickfont=dict(color="#6e6e6e", size=10), showgrid=False
        )
        yaxis2_layout = None


    layout_kwargs = dict(
        title=dict(
            text=f"{'Confirmed & Deaths' if selected_type == 'both' else selected_type.capitalize()} cases per month ({selected_year}) in USA",
            font=dict(size=14, family="Inter", color="#1f2937")
        ),
        xaxis=dict(
            title="Month", type="date", tickformat="%b %Y", showgrid=False,
            titlefont=dict(color="#6e6e6e"), tickfont=dict(color="#6e6e6e", size=9),
            tickangle=-30,            
            dtick="M2" if selected_year == "2020-2021" else "M1",
            range=[df_monthly_control['month'].min(), df_monthly_control['month'].max()],
        ),
        yaxis=yaxis_layout,
        height=340,
        margin=dict(l=10, r=10, t=40, b=80), 
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=0.01, yref="container",
            xanchor="center", x=0.5, font=dict(size=10)
        )
    )

    if selected_type == "both" and yaxis2_layout:
        layout_kwargs["yaxis2"] = yaxis2_layout

    fig.update_layout(
   
        legend=dict(
            orientation="h",  
            yanchor="top",
            y=-0.2,          
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=50, b=50, l=50, r=50), 
        
        yaxis=dict(
            title=dict(text="Confirmed Cases", font=dict(color="#6d28d9", size=11)),
            tickfont=dict(color="#6d28d9", size=10),
            showgrid=False,
            side="left"
        ),
        yaxis2=dict(
            title=dict(text="Deaths", font=dict(color="#a78bfa", size=11)),
            tickfont=dict(color="#a78bfa", size=10),
            showgrid=False,
            overlaying="y",
            side="right"
        ),
        xaxis=dict(showgrid=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
  
    st.plotly_chart(fig, use_container_width=True, key=f"chart_cases_{selected_year}_{selected_type}")

    st.caption("Move the slider to see the accumulated cases and medical access breakdown of the month ranges.")

    st.markdown("""
        <style>
            /* Ocultar el título superior/label del slider */
            div[data-testid="stSlider"] > label {
                display: none !important;
            }
            /* Pegar el slider hacia arriba para que quede pegadito a la gráfica */
            div[data-testid="stSlider"] {
                margin-top: -12px !important;
                padding-top: 0px !important;
            }
            /* Barra del pasado recorrida -> Gris corporativo */
            div[data-testid="stSlider"] .st-at {
                background-color: #cbd5e1 !important;
            }
            /* Barra del futuro restante -> Gris muy claro y limpio */
            div[data-testid="stSlider"] .st-ae {
                background-color: #f1f5f9 !important;
            }
            /* Tirador redondo -> Más pequeño (scale 0.8), gris oscuro y borde blanco */
            div[data-testid="stSlider"] .st-ag {
                background-color: #64748b !important;
                border: 2px solid #ffffff !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
                transform: scale(0.8) !important;
            }
            /* Etiquetas de los meses inferiores -> Pequeñas y fuente Inter */
            div[data-testid="stSlider"] .st-ag span {
                font-family: 'Inter', sans-serif !important;
                font-size: 10px !important;
                color: #64748b !important;
            }
        </style>
    """, unsafe_allow_html=True)

    slider_options = [m.strftime('%b %Y') for m in months_list]
    current_index = months_list.index(st.session_state.selected_cut) if st.session_state.selected_cut in months_list else len(months_list)-1


    selected_month_str = st.select_slider(
        label="Cases Timeline Control", 
        options=slider_options,
        value=slider_options[current_index],
        key=f"slider_cases_{selected_year}_{selected_type}"
    )

 
    new_cut_from_slider = months_list[slider_options.index(selected_month_str)]
    
    if st.session_state.selected_cut != new_cut_from_slider:
        st.session_state.selected_cut = new_cut_from_slider
        st.rerun()

with col_left:
    if selected_type == "both":
        val_conf_cut = df_us_selected[
            (df_us_selected['type']=="confirmed") & 
            (df_us_selected['month'] <= st.session_state.selected_cut)
        ]['cases'].sum()

        val_death_cut = df_us_selected[
            (df_us_selected['type']=="death") & 
            (df_us_selected['month'] <= st.session_state.selected_cut)
        ]['cases'].sum()

        comparison_conf, comparison_death = "", ""

        if selected_year == "2021":
            
            val_conf_prev = cases[
                (cases['year'] == 2020) &
                (cases['country'].str.upper() == "US") &
                (cases['type'] == "confirmed") &
                (cases['date'] <= st.session_state.selected_cut.replace(year=2020))
            ]['cases'].sum()

            val_death_prev = cases[
                (cases['year'] == 2020) &
                (cases['country'].str.upper() == "US") &
                (cases['type'] == "death") &
                (cases['date'] <= st.session_state.selected_cut.replace(year=2020))
            ]['cases'].sum()

            perc_conf = ((val_conf_cut - val_conf_prev) / val_conf_prev * 100) if val_conf_prev > 0 else 0
            perc_death = ((val_death_cut - val_death_prev) / val_death_prev * 100) if val_death_prev > 0 else 0

            comparison_conf = f"{perc_conf:.1f}% vs same month 2020"
            comparison_death = f"{perc_death:.1f}% vs same month 2020"

        elif selected_year == "2020-2021":
            
            val_conf_2020 = cases[
                (cases['year'] == 2020) &
                (cases['country'].str.upper() == "US") &
                (cases['type'] == "confirmed") &
                (cases['date'] <= st.session_state.selected_cut)
            ]['cases'].sum()
            val_conf_2021 = cases[
                (cases['year'] == 2021) &
                (cases['country'].str.upper() == "US") &
                (cases['type'] == "confirmed") &
                (cases['date'] <= st.session_state.selected_cut)
            ]['cases'].sum()

            val_death_2020 = cases[
                (cases['year'] == 2020) &
                (cases['country'].str.upper() == "US") &
                (cases['type'] == "death") &
                (cases['date'] <= st.session_state.selected_cut)
            ]['cases'].sum()
            val_death_2021 = cases[
                (cases['year'] == 2021) &
                (cases['country'].str.upper() == "US") &
                (cases['type'] == "death") &
                (cases['date'] <= st.session_state.selected_cut)
            ]['cases'].sum()

            comparison_conf = f"2020: {format_number(val_conf_2020)} | 2021: {format_number(val_conf_2021)}"
            comparison_death = f"2020: {format_number(val_death_2020)} | 2021: {format_number(val_death_2021)}"

        elif selected_year == "2020":
            
            comparison_conf = "Accumulated in 2020"
            comparison_death = "Accumulated in 2020"

        
        st.html(f"""
        <div style="text-align:center; height:340px; display:flex; flex-direction:column; justify-content:center; align-items:center; font-family:'Inter', sans-serif; background: transparent;">
            
            <div style="margin-bottom:12px;">
                <div style="font-size:46px; font-weight:700; color:#6d28d9; line-height:1; letter-spacing:-1px;">
                    {format_number(val_conf_cut)}
                </div>
                <div style="font-size:11px; font-weight:600; color:#6d28d9; text-transform:uppercase; margin-top:4px; letter-spacing:0.5px;">Confirmed Cases</div>
                <div style="font-size:12px; color:#4c1d95; margin-top:6px;">
                    {comparison_conf}
                </div>
            </div>
            
            <div style="border-top:1px solid #e5e7eb; width:40px; margin:4px 0 12px 0;"></div>
            
            <div style="margin-bottom:20px;">
                <div style="font-size:46px; font-weight:700; color:#a78bfa; line-height:1; letter-spacing:-1px;">
                    {format_number(val_death_cut)}
                </div>
                <div style="font-size:11px; font-weight:600; color:#a78bfa; text-transform:uppercase; margin-top:4px; letter-spacing:0.5px;">Deaths</div>
                <div style="font-size:12px; color:#4c1d95; margin-top:6px;">
                    {comparison_death}
                </div>
            </div>
            
            <div style="font-size:14px; font-weight:500; color:#4b5563; line-height:1.3;">
                Metrics accumulated up to <br>
                <span style="color:#6d28d9; font-weight:700; font-size:16px;">
                    {st.session_state.selected_cut.strftime('%b %Y')}
                </span>
            </div>
            
        </div>
        """)
    else:
        
        df_single_type = df_us_selected[df_us_selected['month'] <= st.session_state.selected_cut]
        main_kpi_value = df_single_type['cases'].sum()
        
        comparison_text = ""
        if selected_year == "2021":
            val_2020 = cases[
                (cases['year'] == 2020) &
                (cases['country'].str.upper() == "US") &
                (cases['type'] == selected_type) &
                (cases['date'] <= st.session_state.selected_cut)
            ]['cases'].sum()
            diff = main_kpi_value - val_2020
            perc_change = (diff / val_2020 * 100) if val_2020 > 0 else 0
            trend = "Increase" if diff > 0 else "Decrease"
            comparison_text = f"<div style='font-size:14px; color:#4c1d95; font-weight:500; margin-top:12px;'>{trend} of {abs(perc_change):.1f}% compared with 2020</div>"
        
        elif selected_year == "2020-2021":
            val_2020 = cases[
                (cases['year'] == 2020) &
                (cases['country'].str.upper() == "US") &
                (cases['type'] == selected_type) &
                (cases['date'] <= st.session_state.selected_cut)
            ]['cases'].sum()
            val_2021 = cases[
                (cases['year'] == 2021) &
                (cases['country'].str.upper() == "US") &
                (cases['type'] == selected_type) &
                (cases['date'] <= st.session_state.selected_cut)
            ]['cases'].sum()
            comparison_text = f"""
            <div style='font-size:13px; color:#4c1d95; font-weight:500; margin-top:12px; line-height:1.4;'>
                Combined total up to {st.session_state.selected_cut.strftime('%b %Y')}<br>
                {format_number(main_kpi_value)} cases<br>
                <span style='color:#6b7280; font-size:12px;'>2020: {format_number(val_2020)} | 2021: {format_number(val_2021)}</span>
            </div>
            """.strip()

        st.html(f"""
        <div style="text-align:center; height:320px; display:flex; flex-direction:column; justify-content:center; align-items:center; font-family:'Inter', sans-serif; background: transparent;">
            <div style="font-size:74px; font-weight:700; color:#6d28d9; line-height:1.1; letter-spacing:-2px;">
                {format_number(main_kpi_value)}
            </div>
            <div style="font-size:18px; font-weight:500; color:#4b5563; margin-top:15px; max-width:280px; line-height:1.3;">
                {selected_type.capitalize()} cases up to <br>
                <span style="color:#6d28d9; font-weight:700; font-size:22px;">
                    {st.session_state.selected_cut.strftime('%b %Y')}
                </span>
            </div>
            {comparison_text}
        </div>
        """)



st.subheader("Access to Medical Care")
st.caption("Medical Delay and Omission cases throughout USA states by % of adults")

st.markdown("""
    <div style="background-color:#ede9fe; padding:15px; border-radius:8px; border-left:5px solid #6d28d9;">
        <div style="color:#6d28d9; font-size:14px; font-weight:bold;">Insight 1</div>
        <div style="font-size:16px; color:#4c1d95;">
            COVID-19 led many adults to delay or miss needed care, as hospitals were overwhelmed and patients feared infection.
            These charts show the % of adults affected across states 
        </div>
    </div>
    """, unsafe_allow_html=True)

indicators = [
    "Delayed Medical Care",
    "Did Not Get Needed Care"
]

col1, col2 = st.columns(2)

for ind, col in zip(indicators, [col1, col2]):
    if selected_year == "2020-2021":
        df_ind = access[
            (access["Indicator"].str.contains(ind, case=False)) &
            (access["year"].isin([2020, 2021])) &
            (access["Group"] == "By State")
        ].copy()
    else:
        df_ind = access[
            (access["Indicator"].str.contains(ind, case=False)) &
            (access["year"] == int(selected_year)) &
            (access["Group"] == "By State")
        ].copy()

    df_ind["date"] = pd.to_datetime(df_ind["date"])

    df_ind = df_ind[df_ind["date"] <= st.session_state.selected_cut]
    df_ind = df_ind.groupby("Subgroup", as_index=False)["Value"].mean()


    df_top = df_ind.sort_values("Value", ascending=False).head(3)

    if not df_top.empty:
        max_group = df_top.loc[df_top["Value"].idxmax(), "Subgroup"]
        max_val = df_top["Value"].max()
        df_top["color"] = ["#6d28d9" if v == max_val else "#d1d5db" for v in df_top["Value"]]
        y_max_range = max_val * 1.15
    else:
        max_group = "No Data"
        max_val = 0.0
        df_top["color"] = []
        y_max_range = 10.0

    if ind == "Delayed Medical Care":
        context_text = "as a % of adults who delayed getting medical care"
    else:
        context_text = "as a % of adults who needed care for something other than COVID"

    full_title_html = (
        f"<b>{ind} (Accumulated Avg, {selected_year})</b><br>"
        f"<span style='font-size:11px; color:#6b7280; font-style:italic;'>{context_text}</span>"
    )

    with col:
        if not df_top.empty:
            fig = px.bar(
                df_top,
                x="Subgroup",
                y="Value",
                text="Value",
                color="color",
                title=full_title_html,
                color_discrete_map={"#6d28d9": "#6d28d9", "#d1d5db": "#d1d5db"}
            )

            fig.update_traces(
                texttemplate=[f"<b>{val:.1f}%</b>" if val == max_val else f"{val:.1f}%" for val in df_top["Value"]],
                textposition="outside",
                hovertemplate="%{x}: %{y:.1f}%<extra></extra>"
            )

            fig.update_layout(
                xaxis_title="State",
                yaxis_title="Percentage (%)",
                showlegend=False,
                xaxis=dict(showgrid=False, categoryorder="total descending"),
                yaxis=dict(showgrid=False, range=[0, y_max_range]),
                bargap=0.4,
                height=340,
                margin=dict(t=75, b=40),
                title=dict(x=0.5, xanchor="center", font=dict(size=14, family="Inter", color="#1f2937"))
            )
            
            st.plotly_chart(fig, use_container_width=True, key=f"access_chart_{ind}_{selected_year}")
        else:
            st.info(f"No registration data found for {ind} up to this month.")

    
        if selected_year == "2020":
            st.markdown(f"""
            **Explanation (2020):** The highest share of *{ind.lower()}* was in **{max_group}** ({max_val:.1f}%).  
            Pandemic surges and hospital strain led to postponed or missed care.
            """)
        elif selected_year == "2021":
            st.markdown(f"""
            **Explanation (2021):** The highest share of *{ind.lower()}* was in **{max_group}** ({max_val:.1f}%).  
            The Delta wave renewed hospital strain and restrictions, causing many adults to delay or miss care.
            """)
        else:  # 2020-2021
            st.markdown(f"""
            **Explanation (2020–2021):** The combined share of *{ind.lower()}* was highest in **{max_group}** ({max_val:.1f}%).  
            This reflects the cumulative impact across both years, showing how the pandemic consistently strained access to care.
            """)

st.subheader("Long COVID Analysis")
st.caption("Prevalence of chronic symptoms post covid per age group in % of adults in USA.")


### Long COVID Effects
st.markdown("""
    <div style="background-color:#ede9fe; padding:15px; border-radius:8px; border-left:5px solid #6d28d9;">
        <div style="color:#6d28d9; font-size:14px; font-weight:bold;">Insight 1</div>
        <div style="font-size:16px; color:#4c1d95;">
            Long COVID has been officially tracked in the U.S. since 2022.  
            These charts show the % of adults reporting lasting symptoms or activity limits, by age group.
        </div>
    </div>
    """, unsafe_allow_html=True)

questions = [
    "Ever experienced Long COVID (%)",
    "Currently experiencing Long COVID (%)",
    "Activity limitations from Long COVID (%)"
]

col1, col2, col3 = st.columns(3)

for q, col in zip(questions, [col1, col2, col3]):
    if "Ever" in q:
        original_q = "Ever experienced long COVID, as a percentage of adults who ever had COVID"
        context_text = "as a % of adults who ever had COVID"
    elif "Currently" in q:
        original_q = "Currently experiencing long COVID, as a percentage of all adults"
        context_text = "as a % of all adults"
    else:
        original_q = "Any activity limitations from long COVID, as a percentage of adults who currently have long COVID"
        context_text = "as a % of adults with Long COVID"

    df_q = long[
        (long["Indicator"] == original_q) &
        (long["year"] == 2022) &
        (long["Group"] == "By Age")
    ].copy()

    df_q = df_q.groupby("Subgroup", as_index=False)["Value"].max()
    df_top = df_q.sort_values("Value", ascending=False).head(3)

    max_group = df_top.loc[df_top["Value"].idxmax(), "Subgroup"]
    max_val = df_top["Value"].max()

    df_top["color"] = ["#6d28d9" if v == max_val else "#d1d5db" for v in df_top["Value"]]

    
    full_title_html = (
        f"<b>{q}</b><br>"
        f"<span style='font-size:11px; font-weight:normal; color:#6b7280; font-family:Inter;'>{context_text}</span>"
    )

    fig = px.bar(
        df_top,
        x="Subgroup",
        y="Value",
        text="Value",
        color="color",
        title=full_title_html, 
        color_discrete_map={"#6d28d9": "#6d28d9", "#d1d5db": "#d1d5db"}
    )

    fig.update_traces(
        texttemplate=[
            f"<b>{val:.1f}%</b>" if val == max_val else f"{val:.1f}%"
            for val in df_top["Value"]
        ],
        textposition="outside",
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>"
    )

    y_max_range = max_val * 1.15

    fig.update_layout(
        title=dict(
            font=dict(size=14, family="Inter", color="#1f2937"),
            x=0.5, 
            xanchor="center",
            y=0.93 
        ),
    
        xaxis_title="Age Group",
        yaxis_title="Percentage (%)",
        showlegend=False,
        xaxis=dict(showgrid=False, categoryorder="total descending"),
        yaxis=dict(showgrid=False, range=[0, y_max_range]),
        bargap=0.4,
        height=360,
        margin=dict(t=75, b=40)  
    )

    with col:
        st.plotly_chart(fig, use_container_width=True)

    
        if "Ever" in q:
            st.markdown(f"""
            **Explanation (2022):** The highest prevalence of *ever experiencing Long COVID* was in **{max_group}** ({max_val:.1f}%).  
            Adults in this age range often show higher risk due to chronic conditions and more severe infections.
            """)
        elif "Currently" in q:
            st.markdown(f"""
            **Explanation (2022):** The highest share of *currently experiencing Long COVID* was in **{max_group}** ({max_val:.1f}%).  
            This group often combines high exposure at work and family settings, increasing persistent symptoms.
            """)
        else:
            st.markdown(f"""
            **Explanation (2022):** The highest rate of *activity limitations from Long COVID* was in **{max_group}** ({max_val:.1f}%).  
            Younger adults often report stronger impact on daily life, as even moderate symptoms disrupt study, work, and social activities.
            """)

st.markdown(f"""
<div style="text-align:center; font-size:12px; color:#6b7280; margin-top:20px;">
    Data source: CDC & US Census | Dashboard view: {selected_year}
</div>
""", unsafe_allow_html=True)

st.subheader('Data References')
st.caption('For more information the following sites were used to gather the datasets')

st.markdown("""Reduced Access to Care - Household Pulse Survey - COVID-19. (2025, February 7).
            Cdc.Gov. https://www.cdc.gov/nchs/covid19/pulse/reduced-access-to-care.htm""")
st.markdown("""Long COVID - Household Pulse Survey - COVID-19. (2025, February 7).
            Cdc.Gov.https://www.cdc.gov/nchs/covid19/pulse/long-covid.htm‌""")
st.markdown("""Coronavirus/csv at main · RamiKrispin/coronavirus. (2025).
            GitHub. https://github.com/RamiKrispin/coronavirus/tree/main/csv""")



