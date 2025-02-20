import logging
from flask import Flask, render_template, request, send_from_directory
import sys,os
from datetime import datetime
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
# import textwrap
from werkzeug.utils import secure_filename

# 获取当前时间戳，并格式化为字符串
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 配置变量
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'xlsx', 'jpg'}
IMAGE_WIDTH = 1417  # 图片宽度
IMAGE_HEIGHT = 1890  # 图片高度



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# 中文标点符号列表
CHAR_LIST = ["。", "？", "！", "；"] 
# 不适合在行首的标点符号列表
PUNCTUATIONS_NOT_ALLOWED_AT_START = [
    "。", "？", "！", "；", "：", "、", "》", "）", "】", "》", "』", "〞"
]


# 书摘内容区域配置
TEXT_AREA_FONT_SIZE = 75
TEXT_AREA_TEXT_COLOR = (0, 0, 0)
TEXT_AREA_MAX_CHARS_PER_LINE = 12
TEXT_AREA_MARGIN = 200
TEXT_AREA_LEFT_MARGIN = 200
TEXT_AREA_TOP_MARGIN = 400
TEXT_AREA_LINE_SPACING = 50

# 书名区域配置
TITLE_FONT_SIZE = 55
TITLE_TEXT_COLOR = (0, 0, 0)
TITLE_MARGIN = 200
TITLE_LEFT_MARGIN = 200
TITLE_BOTTOM_MARGIN = 400

# 作者信息区域配置
AUTHOR_FONT_SIZE = 150
AUTHOR_TEXT_COLOR = (100, 100, 100)
AUTHOR_RIGHT_MARGIN = 10
AUTHOR_TOP_MARGIN = 100
AUTHOR_LINE_SPACING = 15

# 检查文件扩展名
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 确保上传文件夹存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 确保输出文件夹存在
if not os.path.exists(app.config['OUTPUT_FOLDER']):
    os.makedirs(app.config['OUTPUT_FOLDER'])

def check_image_size(image_path, target_width, target_height):
    
    file_name, file_extension = os.path.splitext(os.path.basename(image_path))
    if file_extension.lower() not in ['.jpg', '.jpeg', '.png']:
        return None

    img = Image.open(image_path)
    width, height = img.size

    if width < target_width or height < target_height:
        # app.logger.error("图片尺寸不合格")
        return None

    # 如果图片尺寸大于指定尺寸，则裁剪图片
    left = (width - target_width) / 2
    top = (height - target_height) / 2
    right = (width + target_width) / 2
    bottom = (height + target_height) / 2

    # 裁剪图片
    cropped_img = img.crop((left, top, right, bottom))

    processed_image_path = os.path.join(
        app.config['UPLOAD_FOLDER'], 
        f"{timestamp}_{file_name}_processed_image{file_extension}"
    )
    cropped_img.save(processed_image_path)

    # 如果尺寸匹配，返回图片对象
    return processed_image_path

# 加载Excel文件
def load_excel(file_path):
    df = pd.read_excel(file_path, header=None)
    return df

# 自动换行处理
def wrap_text(text, max_chars_per_line):
    wrapped_lines = []  # 存储换行后的文本行
    current_line = ""   # 当前行的文本

    for char in text:
        current_line += char  # 将字符添加到当前行

        # 如果当前字符是 CHAR_LIST 中的标点符号，换行并添加空行
        if char in CHAR_LIST:
            wrapped_lines.append(current_line)  # 换行
            wrapped_lines.append("")  # 添加额外的空行
            current_line = ""  # 清空当前行

        # 检查当前行是否包含不适合行首的标点符号
        elif current_line and current_line[0] in PUNCTUATIONS_NOT_ALLOWED_AT_START:
            # 将当前行的第一个标点符号移到上一行的末尾
            if wrapped_lines:
                wrapped_lines[-1] += current_line[0]
            current_line = current_line[1:]  # 移除当前行的标点符号

        # 如果当前行字符数已超过最大限制，进行换行
        if len(current_line) >= max_chars_per_line:
            # 按照 CHAR_LIST 中的标点符号换行
            for char in CHAR_LIST:
                if char in current_line:
                    part_before_char = current_line.split(char, 1)[0]
                    part_after_char = current_line.split(char, 1)[1]
                    if part_before_char:
                        wrapped_lines.append(part_before_char + char)  # 保留标点符号并换行
                    current_line = part_after_char
                    break
            else:
                # 如果没有找到标点符号，则直接换行
                wrapped_lines.append(current_line)
                current_line = ""  # 清空当前行

    # 将剩余部分添加为最后一行
    if current_line:
        wrapped_lines.append(current_line)

    # 处理不适合行首的标点符号
    for i in range(1, len(wrapped_lines)):
        if wrapped_lines[i] and wrapped_lines[i][0] in PUNCTUATIONS_NOT_ALLOWED_AT_START:
            wrapped_lines[i - 1] += wrapped_lines[i][0]  # 将当前行的标点符号移到上一行
            # wrapped_lines[i] = wrapped_lines[i][1:]  # 移除当前行的标点符号
            del wrapped_lines[i]
            break  
    return "\n".join(wrapped_lines)


# 生成图片
def create_image(text, title, author, index, input_image_path, output_image_path, font_path):
    image = Image.open(input_image_path)
    draw = ImageDraw.Draw(image)

    # 加载字体
    text_font = ImageFont.truetype(font_path, TEXT_AREA_FONT_SIZE)
    title_font = ImageFont.truetype(font_path, TITLE_FONT_SIZE)
    author_font = ImageFont.truetype(font_path, AUTHOR_FONT_SIZE)

    # 自动换行处理书摘内容
    wrapped_text = wrap_text(text, TEXT_AREA_MAX_CHARS_PER_LINE)

    # 在左上角区域添加书摘内容
    draw.text(
        (TEXT_AREA_LEFT_MARGIN, TEXT_AREA_TOP_MARGIN),
        wrapped_text,
        font=text_font,
        fill=TEXT_AREA_TEXT_COLOR,
        spacing=TEXT_AREA_LINE_SPACING
    )

    # 在左下角偏中间位置添加书名
    title_position = (TITLE_LEFT_MARGIN, image.height - TITLE_BOTTOM_MARGIN - TITLE_FONT_SIZE)
    draw.text(title_position, title, font=title_font, fill=TITLE_TEXT_COLOR)

    # 在右侧偏上位置竖向添加作者信息
    author_position = (image.width - AUTHOR_RIGHT_MARGIN - AUTHOR_FONT_SIZE, AUTHOR_TOP_MARGIN)
    for i, char in enumerate(author):
        draw.text(
            (author_position[0], author_position[1] + i * (AUTHOR_FONT_SIZE + AUTHOR_LINE_SPACING)),
            char,
            font=author_font,
            fill=AUTHOR_TEXT_COLOR,
        )

    # 保存图片
    output_filename = os.path.join(output_image_path, f"{timestamp}_{index}.jpg")
    image.save(output_filename)
    return output_filename

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 获取上传的文件
        excel_file = request.files['file.xlsx']
        image_file = request.files['input_image.jpg']

        # 确保文件类型正确
        if excel_file and allowed_file(excel_file.filename) and image_file and allowed_file(image_file.filename):
            excel_filename = secure_filename(excel_file.filename)
            image_filename = secure_filename(image_file.filename)

            excel_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

            excel_file.save(excel_path)
            image_file.save(image_path)

            # 检查图片尺寸
            processed_image_path = check_image_size(image_path, IMAGE_WIDTH, IMAGE_HEIGHT)
            if processed_image_path is None:
                # 如果图片不合格，提示错误并停止后续操作
                return render_template('index.html', error="图片尺寸不合格，请上传符合尺寸要求的图片。尺寸要求大于或等于1417x1890像素。")

        
            # 加载Excel文件
            df = load_excel(excel_path)

            # 创建存储处理后图片的文件夹
            if not os.path.exists(app.config['OUTPUT_FOLDER']):
                os.makedirs(app.config['OUTPUT_FOLDER'])

            # 遍历每一行数据生成图片
            output_image_paths = []
            for index, row in df.iterrows():
                if index == 0:  # 跳过表头
                    continue
                text = row[0]  # 书摘内容
                title = row[1]  # 书名
                author = row[2]  # 作者信息

                # 使用create_image函数生成图片
                output_image_path = create_image(text, title, author, index, processed_image_path, app.config['OUTPUT_FOLDER'], 'font.ttf')
                output_image_paths.append(output_image_path)

            # 返回生成的图片链接
            return render_template('result.html', output_image_paths=output_image_paths)

    return render_template('index.html')

@app.route('/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == "__main__":
    app.logger.setLevel(logging.DEBUG)  # 设置日志级别为DEBUG
    app.run(debug=True,host='0.0.0.0')
