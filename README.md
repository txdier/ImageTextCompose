# ImageTextCompose

## 运行方式


### 创建虚拟环境，并安装依赖库
```shell
python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

### Flask直接运行

```python
python3 app.py
```

### Gunicorn
```shell
pip install gunicorn

gunicorn -w 4 --access-logfile 'access.log' --error-logfile 'error.log' -b 0.0.0.0:5000 app:app

```
**（可选）创建 gunicorn.conf.py 配置文件**
如果你有复杂的配置需求，可以将 Gunicorn 的设置放在一个单独的配置文件 gunicorn.conf.py 中。例如：
```py
# gunicorn.conf.py
workers = 4
bind = "0.0.0.0:5000"
accesslog = "access.log"
errorlog = "error.log"
```

然后可以这样启动：

```bash
gunicorn -c gunicorn.conf.py app:app
```