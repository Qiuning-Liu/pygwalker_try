import streamlit as st
import pandas as pd
from pygwalker.api.streamlit import init_streamlit_comm, StreamlitRenderer
import io
import openpyxl

def read_file(uploaded_file, sheet_name=None):
    if uploaded_file.name.endswith('.csv'):
        # CSV 文件处理
        encodings = ['utf-8', 'gbk', 'gb18030', 'big5', 'utf-8-sig', 'latin1']
        for encoding in encodings:
            try:
                file_content = uploaded_file.getvalue().decode(encoding)
                if not file_content.strip():
                    st.error("上传的文件是空的。请确保文件包含数据。")
                    return None
                df = pd.read_csv(io.StringIO(file_content))
                st.sidebar.success(f"成功使用 {encoding} 编码读取 CSV 文件")
                return df
            except UnicodeDecodeError:
                continue
            except pd.errors.EmptyDataError:
                st.error("CSV 文件中没有可解析的列。请检查文件格式是否正确。")
                return None
        st.error("无法找到正确的编码方式，请检查 CSV 文件编码")
        return None
    elif uploaded_file.name.endswith(('.xlsx', '.xls')):
        # Excel 文件处理
        try:
            xls = pd.ExcelFile(uploaded_file)
            sheet_names = xls.sheet_names
            if sheet_name is None or sheet_name not in sheet_names:
                sheet_name = st.sidebar.selectbox("选择要读取的 sheet", sheet_names)
            df = pd.read_excel(xls, sheet_name=sheet_name)
            st.sidebar.success(f"成功读取 Excel 文件的 '{sheet_name}' sheet")
            return df
        except Exception as e:
            st.error(f"读取 Excel 文件时发生错误: {str(e)}")
            return None
    else:
        st.error("不支持的文件格式。请上传 CSV 或 Excel 文件。")
        return None

def main():
    # 设置页面标题和布局
    st.set_page_config(page_title="数据可视化应用", layout="wide")

    # 调整左侧边栏宽度
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            width: 300px;
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            width: 300px;
            margin-left: -300px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 文件上传
    uploaded_file = st.sidebar.file_uploader("选择一个 CSV 或 Excel 文件", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        df = read_file(uploaded_file)
        if df is not None and not df.empty:
            # 显示数据预览
            st.subheader("数据预览")
            st.dataframe(df.head())

            # 使用 pygwalker 创建可视化
            st.subheader("数据可视化")
            renderer = StreamlitRenderer(df, spec="./gw_config.json", debug=False)
            renderer.render_explore()
        elif df is not None and df.empty:
            st.error("读取的数据为空。请检查文件内容。")
    else:
        st.info("请在左侧边栏上传一个 CSV 或 Excel 文件以开始分析。")

if __name__ == "__main__":
    main()