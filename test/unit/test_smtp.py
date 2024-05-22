from app.router.user_manager import send_email


def test_semd_email():
    token = "test-token"
    to_email = "2544054211@qq.com"
    send_email(
        subject="确认您的注册账号",
        message=f"请点击以下链接以确认您的注册账号: http://localhost:3000/auth/verify-register/{token}",
        to_email=to_email,
    )
