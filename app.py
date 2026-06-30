import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from collections import Counter
import re

# Set page layout
st.set_page_config(page_title="Advanced Arabic Poetry Dashboard", layout="wide")

st.title("📊 لوحة التحليل المتقدم لبيانات موقع الشعراء")
st.markdown("منصة تفاعلية مدعومة بالـ NLP لاستكشاف بصمة الشعر العربي عبر العصور والجغرافيا.")

# ISO Alpha-3 mapping
country_map = {
    'الجزيرة العربية  "السعودية"': 'SAU', 'سوريا': 'SYR', 'العراق': 'IRQ', 
    'البحرين': 'BHR', 'لبنان': 'LBN', 'مصر': 'EGY', 'السودان': 'SDN', 
    'عمان': 'OMN', 'اليمن': 'YEM', 'الأردن': 'JOR', 'الكويت': 'KWT', 
    'إيران': 'IRN', 'فلسطين': 'PSE', 'الإمارات': 'ARE', 'المغرب': 'MAR'
}

# 1. Load Data
@st.cache_data
def load_data():
    df = pd.read_json("all_poems_database_cleaned.json")
    df = df[df['country'] != 'أحمد شوقي - أمير الشعراء']
    return df

df_raw = load_data()

# ==========================================
# SIDEBAR FILTERS (التصفية التفاعلية)
# ==========================================
st.sidebar.header("🔍 فلاتر التحكم بالبيانات")

# Era Filter
all_eras = ["كل العصور"] + list(df_raw['era'].unique())
selected_era = st.sidebar.selectbox("اختر العصر التاريخي:", all_eras)

# Country Filter
all_countries = ["كل الدول"] + list(df_raw[~df_raw['country'].isin(["Not specified", "غير محدد", "Unknown", ""])]['country'].unique())
selected_country = st.sidebar.selectbox("اختر الدولة الجغرافية:", all_countries)

# Apply Filters to a copy of the dataframe
df = df_raw.copy()
if selected_era != "كل العصور":
    df = df[df['era'] == selected_era]
if selected_country != "كل الدول":
    df = df[df['country'] == selected_country]


# ==========================================
# MAIN METRICS
# ==========================================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="عدد القصائد بالفلاتر الحالية", value=f"{df.shape[0]:,}")
with col2:
    st.metric(label="عدد الشعراء الفريدين", value=f"{df['poet_name'].nunique():,}")
with col3:
    st.metric(label="متوسط عدد الأبيات/القصيدة", value=f"{int(pd.to_numeric(df['number_of_verses'], errors='coerce').mean()):,}" if df.shape[0]>0 else "0")
with col4:
    st.metric(label="الموضوع الأكثر انتشاراً", value=df['poem_sub_theme'].mode()[0] if not df.empty else "لا يوجد")

st.divider()

# ==========================================
# CHARTS & GEOGRAPHY
# ==========================================
tab1, tab2, tab3 = st.tabs(["🗺️ التوزيع الجغرافي والعصور", "🔤 تحليل النصوص (NLP Insight)", "👤 مستكشف الشعراء التفصيلي"])

with tab1:
    left_chart, right_chart = st.columns(2)
    
    with left_chart:
        st.subheader("🗺️ خريطة انتشار الشعراء")
        map_df = df[~df['country'].isin(["Not specified", "غير محدد", "Unknown", ""])].copy()
        if not map_df.empty:
            country_stats = map_df.groupby('country')['poet_name'].nunique().reset_index()
            country_stats.columns = ['country', 'poet_count']
            country_stats['iso_code'] = country_stats['country'].map(country_map)
            country_stats = country_stats.dropna(subset=['iso_code'])
            country_stats['log_poet_count'] = np.log10(country_stats['poet_count'] + 1)
            
            fig_map = px.choropleth(
                country_stats, locations="iso_code", color="log_poet_count",
                hover_name="country", hover_data={"log_poet_count": False, "poet_count": True},
                color_continuous_scale="Blues", template="plotly_dark"
            )
            fig_map.update_traces(marker_line_color="rgba(150, 150, 150, 0.8)", marker_line_width=1.2)
            fig_map.update_geos(scope="asia", center={"lat": 24.0, "lon": 45.0}, lataxis_range=[10, 40], lonaxis_range=[25, 60], showcountries=True)
            fig_map.update_layout(coloraxis_showscale=False, margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("لا توجد بيانات جغرافية تطابق الفلاتر الحالية.")

    with right_chart:
        st.subheader("📈 حجم البيانات حسب العصر")
        if not df.empty:
            era_counts = df['era'].value_counts().reset_index()
            era_counts.columns = ['العصر', 'عدد القصائد']
            fig_era = px.bar(era_counts, x='العصر', y='عدد القصائد', color='العصر', template="plotly_dark")
            st.plotly_chart(fig_era, use_container_width=True)

with tab2:
    st.subheader("🔤 الكلمات الأكثر تكراراً في نصوص القصائد الحالية (NLP)")
    st.markdown("تحليل أولي للكلمات الأكثر استخداماً بناءً على الفلاتر المختارة:")
    
    if not df.empty:
        # Quick tokenization mechanism for top words extraction
        all_text = " ".join(df['full_poem_text'].astype(str).head(500)) # sampling first 500 for performance
        words = re.findall(r'\b\w+\b', all_text)
        # Exclude common short words manually to clean insights
        stop_words_fallback = ["من", "في", "على", "إلى", "أن", "ما", "لا", "الله", "عن", "يا", "و", "ف", "ب"]
        filtered_words = [w for w in words if len(w) > 2 and w not in stop_words_fallback]
        
        word_counts = Counter(filtered_words).most_common(15)
        if word_counts:
            word_df = pd.DataFrame(word_counts, columns=['الكلمة', 'التكرار'])
            fig_words = px.bar(word_df, x='التكرار', y='الكلمة', orientation='h', color='التكرار', color_continuous_scale="Viridis", template="plotly_dark")
            st.plotly_chart(fig_words, use_container_width=True)
    else:
        st.info("لا توجد نصوص كافية للتحليل.")

with tab3:
    st.subheader("👤 محرك البحث عن الشعراء واستكشاف دواوينهم")
    
    # Search box for poet profiles
    poet_search = st.selectbox("اختر أو اكتب اسم الشاعر للاستعلام عنه:", [""] + list(df_raw['poet_name'].unique()))
    
    if poet_search != "":
        poet_data = df_raw[df_raw['poet_name'] == poet_search]
        
        # Display Profile Card
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            st.info(f"**العصر التاريخي:** {poet_data['era'].iloc[0]}")
        with p_col2:
            st.success(f"**البلد / الجغرافيا:** {poet_data['country'].iloc[0]}")
        with p_col3:
            st.metric(label="إجمالي قصائده بالداتا", value=len(poet_data))
            
        st.markdown(f"#### 📜 قائمة بقصائد الشاعر ({poet_search}):")
        st.write(poet_data[['title', 'poem_sub_theme', 'number_of_verses']].reset_index(drop=True))

# ==========================================
# DATA EXPLORER
# ==========================================
st.divider()
st.subheader("🔍 مستكشف الجدول الكامل")
st.dataframe(df[['poem_id', 'poet_name', 'title', 'era', 'poem_sub_theme', 'country']].head(200), use_container_width=True)