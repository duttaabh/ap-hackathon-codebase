# Instructions to run the streamlit application on mac or linux
1. git clone https://github.com/duttaabh/ap-hackathon-codebase.git
2. cd ap-hackathon-codebase/streamlit
3. python -m venv venv
4. source venv/bin/activate
5. pip install -r ../requirements.txt
6. Open the Chatbot.py file and update the following details:
      bot_name = 'xxxxxxxx'
      bot_alias_id = 'xxxxxxxx'
      bot_region = 'xxxxxxx'
7. Finally run - streamlit run Chatbot.py
8. The following prompt will appear upon execution of the previous command
      You can now view your Streamlit app in your browser.

          Network URL: http://xxx.xx.xx.xxx:8501

          External URL: http://x.xx.xx.xx:8501
