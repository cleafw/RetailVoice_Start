from user.RetailVoice import open_sensecraft_voice, open_rerouter_voice_service

if __name__ == "__main__":
    open_rerouter_voice_service()  # 打开 reRouter 本地语音识别服务
    open_sensecraft_voice()         # 打开 SenseCraft Voice 语音识别系统

