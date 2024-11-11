
# -*- coding: utf-8 -*-
from setuptools import setup

# name, description, version등의 정보는 일반적인 setup.py와 같습니다.
setup(name="Youtube downloader",
      description="Youtube downloader application",
      version="0.0.1",
      # 설치시 의존성 추가
      setup_requires=["py2app"],
      app=["app.py"],
      options={
        "py2app": {
            "argv_emulation": True,
            "includes": ["yt_dlp", "tkinter"],
            "packages": ["yt_dlp"],  # 필요한 패키지 추가
            "iconfile": "app_icon.icns",
          }
      })