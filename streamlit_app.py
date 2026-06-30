"""
Streamlit Cloud 入口文件
重定向到 unified_app.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_app import main

if __name__ == "__main__":
    main()
