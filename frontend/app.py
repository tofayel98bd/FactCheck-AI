import streamlit as st
import httpx

# --- ১. পেজ কনফিগারেশন ---
st.set_page_config(page_title="FactCheck AI", page_icon="🕵️‍♂️", layout="centered")

# --- ২. অ্যাডভান্সড কাস্টম CSS ডিজাইন ---
st.markdown("""
<style>
    /* ব্যাকগ্রাউন্ড ও মেইন ফন্ট */
    .stApp {
        background-color: #0E1117;
    }
    
    /* গ্রেডিয়েন্ট টাইটেল */
    .main-title {
        font-size: 50px !important;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    
    /* সাবটাইটেল */
    .sub-title {
        text-align: center;
        color: #A0AEC0;
        font-size: 18px;
        margin-bottom: 40px;
    }
    
    /* ইনপুট বক্সের ডিজাইন */
    .stTextArea textarea {
        border-radius: 15px !important;
        border: 2px solid #2D3748 !important;
        background-color: #1A202C !important;
        color: white !important;
        font-size: 16px !important;
    }
    .stTextArea textarea:focus {
        border-color: #00C9FF !important;
        box-shadow: 0 0 10px rgba(0, 201, 255, 0.5) !important;
    }
    
    /* বাটন ডিজাইন */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #FF416C 0%, #FF4B2B 100%);
        color: white;
        border-radius: 25px;
        padding: 12px;
        font-size: 20px;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(255, 75, 43, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- ৩. হেডার সেকশন ---
st.markdown('<p class="main-title">FactCheck AI 🔍</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">রিয়েল-টাইম এআই-পাওয়ার্ড নিউজ ভেরিফিকেশন সিস্টেম</p>', unsafe_allow_html=True)

# --- ৪. ইনপুট সেকশন ---
claim = st.text_area("যে খবরটি যাচাই করতে চান, তা নিচে লিখুন:", height=130, placeholder="যেমন: আগামী বছর পদ্মা ব্যারেজের নির্মাণ কাজের উদ্বোধন...")

API_URL = "http://127.0.0.1:8000/api/verify-fact"

# --- ৫. বাটন ও এপিআই কানেকশন ---
if st.button("সত্যতা যাচাই করুন 🚀"):
    if claim.strip():
        with st.spinner("🔍 এআই ইন্টারনেট থেকে তথ্য সংগ্রহ করে বিশ্লেষণ করছে... দয়া করে অপেক্ষা করুন।"):
            try:
                # ব্যাকএন্ডে রিকোয়েস্ট পাঠানো
                response = httpx.post(API_URL, json={"claim": claim}, timeout=30.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success("✅ যাচাই সম্পন্ন হয়েছে!")
                    
                    # সুন্দর কার্ড স্টাইলে রেজাল্ট দেখানো
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="📌 ফলাফল (Verdict)", value=data.get("verdict", "অজানা"))
                    with col2:
                        st.metric(label="📊 ট্রাস্ট স্কোর", value=f"{data.get('trust_score', 0)}%")
                    
                    st.markdown("---")
                    st.subheader("📝 বিস্তারিত ব্যাখ্যা")
                    st.info(data.get("explanation", "কোনো ব্যাখ্যা পাওয়া যায়নি।"))
                    
                else:
                    st.error("⚠️ ব্যাকএন্ড সার্ভার থেকে সঠিক উত্তর পাওয়া যায়নি।")
                    
            except Exception as e:
                st.error("❌ এরর: সার্ভারের সাথে কানেক্ট করা যাচ্ছে না। তোমার FastAPI সার্ভার কি চালু আছে?")
    else:
        st.warning("দয়া করে বক্সে কিছু টেক্সট লিখুন!")