
from django.core.mail import send_mail

from veh_eng.celery import app

@app.task
def send_active_email(email,url):

    print('--start send email--')
    subject = '朝克的车场激活邮件'
    html_message = """
    <p>尊敬的用户 老子是朝克</p>
    <p>洒家的激活url为<a href='%s' target='blank'>点击激活</a></p>
    """%(url)
    send_mail(subject,'','1298542398@qq.com',
        html_message=html_message,recipient_list=[email])









