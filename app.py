import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import textwrap

# 配置变量
EXCEL_FILE = "file.xlsx"  # Excel文件路径
FONT_PATH = "font.ttf"  # 支持中文的字体文件路径
INPUT_IMAGE_PATH = "input_image.jpg"  # 原始图片路径
IMAGE_WIDTH = 1417  # 图片宽度
IMAGE_HEIGHT = 1890  # 图片高度
CHAR_LIST = ["。", "？", "！", "；"]  # 中文标点符号列表

# 书摘内容区域配置
TEXT_AREA_FONT_SIZE = 75  # 字体大小
TEXT_AREA_TEXT_COLOR = (0, 0, 0)  # 文字颜色（黑色）
TEXT_AREA_MAX_CHARS_PER_LINE = 12  # 每行最大字符数
TEXT_AREA_MARGIN = 200  # 边界
TEXT_AREA_LEFT_MARGIN = 200  # 左边界
TEXT_AREA_TOP_MARGIN = 400  # 上边界
TEXT_AREA_LINE_SPACING = 50  # 行间距

# 书名区域配置
TITLE_FONT_SIZE = 55  # 字体大小
TITLE_TEXT_COLOR = (0, 0, 0)  # 文字颜色（黑色）
TITLE_MARGIN = 200  # 边界
TITLE_LEFT_MARGIN = 200  # 左边界
TITLE_BOTTOM_MARGIN = 400  # 下边界

# 作者信息区域配置
AUTHOR_FONT_SIZE = 150  # 字体大小
AUTHOR_TEXT_COLOR = (100, 100, 100)  # 文字颜色（灰色）
AUTHOR_RIGHT_MARGIN = 10  # 右边界
AUTHOR_TOP_MARGIN = 100  # 上边界
AUTHOR_LINE_SPACING = 15  # 行间距

# 加载Excel文件
def load_excel(file_path):
    df = pd.read_excel(file_path, header=None)  # 无表头，直接读取数据
    return df

# 自动换行处理
def wrap_text(text, max_chars_per_line):
    wrapped_lines = []
    current_line = ""
    for char in text:
        current_line += char
        # 如果当前字符是中文句号，或者当前行字符数达到最大值，则换行
        if char in CHAR_LIST or len(current_line) >= max_chars_per_line:
            wrapped_lines.append(current_line)
            # 如果当前字符是中文句号，额外添加一个换行符
            if char in CHAR_LIST:
                wrapped_lines.append("")  # 添加一个空行
            current_line = ""
    # 添加最后一行
    if current_line:
        wrapped_lines.append(current_line)
    return "\n".join(wrapped_lines)

# 生成图片
def create_image(text, title, author, index):
    # 每次生成图片时都重新加载原始图片
    image = Image.open(INPUT_IMAGE_PATH)
    draw = ImageDraw.Draw(image)

    # 加载字体
    text_font = ImageFont.truetype(FONT_PATH, TEXT_AREA_FONT_SIZE)
    title_font = ImageFont.truetype(FONT_PATH, TITLE_FONT_SIZE)
    author_font = ImageFont.truetype(FONT_PATH, AUTHOR_FONT_SIZE)

    # 自动换行处理书摘内容
    wrapped_text = wrap_text(text, TEXT_AREA_MAX_CHARS_PER_LINE)

    # 在左上角区域添加书摘内容
    draw.text(
        (TEXT_AREA_LEFT_MARGIN, TEXT_AREA_TOP_MARGIN),  # 起始位置
        wrapped_text,                                   # 换行后的文本
        font=text_font,                                 # 字体
        fill=TEXT_AREA_TEXT_COLOR,                      # 文字颜色
        spacing=TEXT_AREA_LINE_SPACING                  # 行间距
    )

    # 在左下角偏中间位置添加书名
    title_position = (TITLE_LEFT_MARGIN, IMAGE_HEIGHT - TITLE_BOTTOM_MARGIN - TITLE_FONT_SIZE)
    draw.text(title_position, title, font=title_font, fill=TITLE_TEXT_COLOR)

    # 在右侧偏上位置竖向添加作者信息
    author_position = (IMAGE_WIDTH - AUTHOR_RIGHT_MARGIN - AUTHOR_FONT_SIZE, AUTHOR_TOP_MARGIN)
    for i, char in enumerate(author):
        draw.text(
            (author_position[0], author_position[1] + i * (AUTHOR_FONT_SIZE + AUTHOR_LINE_SPACING)),
            char,
            font=author_font,
            fill=AUTHOR_TEXT_COLOR,
        )

    # 保存图片
    output_filename = f"{title}_{index}.jpg"
    image.save(output_filename)
    print(f"已生成图片: {output_filename}")

# 主函数
def main():
    # 加载Excel文件
    df = load_excel(EXCEL_FILE)

    # 遍历每一行数据
    for index, row in df.iterrows():
        if index == 0:  # 跳过表头
            continue
        text = row[0]  # 第一列：书摘内容
        title = row[1]  # 第二列：书名
        author = row[2]  # 第三列：作者信息

        # 生成图片
        create_image(text, title, author, index)

if __name__ == "__main__":
    main()