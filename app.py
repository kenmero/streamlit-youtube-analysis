import streamlit as st
import base64
from apiclient.errors import HttpError


def app():
    if 'search_btn' not in st.session_state:
        st.session_state.search_btn = False
    message = st.empty()

    st.write('<center><h1>Youtube動画分析</h1></center>', unsafe_allow_html=True)
    with st.container():
        with st.sidebar:
            st.subheader('クエリと閾値の設定')
            with st.form('query'):
                st.write('### クエリの入力')
                keyword = st.text_input('検索キーワードを入力してください。')

                st.write('### 閾値の設定')
                con1 = st.container()
                num, criteria = con1.columns([6, 4])
                subscriber_count = num.number_input('登録者数', value=100000)
                select_criteria = criteria.selectbox('条件', ['以上', '以下'])
                if select_criteria == '以上':
                    mt = True
                    lt = False
                else:
                    mt = False
                    lt = True

                btn = st.form_submit_button('検索')
                if not st.session_state.search_btn:
                    if btn:
                        if not keyword:
                            message.error('検索キーワードを入力してください。')
                        else:
                            st.session_state.search_btn = btn
                else:
                    if not keyword:
                        message.error('検索キーワードを入力してください。')
                        st.session_state.search_btn = False

    t_youtube, t_demo = st.tabs(['動画分析', 'デモ'])
    ################################
    # Youtube解析
    ################################
    with t_youtube:
        with st.container():
            try:
                st.markdown(f"""
                ### 選択中のパラメータ
                - 検索クエリ:  {keyword}
                - 登録者数の閾値:  {subscriber_count}
                - 閾値の条件:  {select_criteria}
                """)
                if st.session_state.search_btn:
                    st.markdown('### 分析結果')
                    # # MOCK
                    # import pandas as pd
                    # df = pd.read_csv('sample.csv')
                    # st.dataframe(df, use_container_width=True)
                    df = youtube.get(keyword, subscriber_count, mt, lt)
                    st.dataframe(df, use_container_width=True)

                    st.markdown('### 動画再生')
                    with st.form('movie'):
                        video_id = st.text_input('動画IDを入力してください')
                        url = f'https://youtu.be/{video_id}'
                        video_field = st.empty()
                        video_field.markdown('こちらに動画が表示されます')

                        btn = st.form_submit_button('ビデオ表示')
                        if btn:
                            try:
                                video_field.video(url)
                            except Exception:
                                st.error('動画の読み込みに失敗しました。')
            except HttpError as e:
                st.error(f'APIの利用上限に達した可能性があります。エラー内容：{e}')                              
            except Exception as e:
                st.error(f'現在利用できません。エラー内容：{e}')
    ################################
    # デモ
    ################################
    with t_demo:
        with st.container():
            with open('./img/demo.gif', 'rb') as f:
                contents = f.read()
                data_url = base64.b64encode(contents).decode('utf-8')

            with st.container():
                st.write(
                    f'<img src="data:image/gif;base64,{data_url}" alt=demo gif>',
                    unsafe_allow_html=True,
            )
if __name__ == '__main__':
    st.set_page_config('Youtube解析', layout='wide', page_icon='👤')
    from utils import youtube
    app()