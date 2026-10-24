# -*- coding: utf-8 -*-
"""生成 phyxexp 参赛 PPT（终版，11 页，侧重实用性与时代叙事）。"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

PRIMARY = RGBColor(0x1F, 0x38, 0x64)
ACCENT  = RGBColor(0xF5, 0x85, 0x18)
GRAY    = RGBColor(0x40, 0x40, 0x40)
LIGHT   = RGBColor(0xED, 0xF1, 0xF7)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
GREEN   = RGBColor(0x2E, 0x7D, 0x32)
RED     = RGBColor(0xC0, 0x39, 0x2B)
BLUE2   = RGBColor(0x4C, 0x78, 0xA8)
FONT = "Microsoft YaHei"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def style(run, size=18, bold=False, color=GRAY, name=FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {})
        rPr.append(ea)
    ea.set('typeface', name)


def add_text(slide, x, y, w, h, lines, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space_after=8):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    first = True
    for ln in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        p.space_after = Pt(space_after)
        if isinstance(ln, str):
            ln = (ln, 18, False, GRAY)
        text, size, bold, color = ln
        r = p.add_run(); r.text = text
        style(r, size, bold, color)
    return tb


def add_title(slide, text, sub=None):
    band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
    band.fill.solid(); band.fill.fore_color.rgb = PRIMARY
    band.line.fill.background(); band.shadow.inherit = False
    tf = band.text_frame
    tf.margin_left = Inches(0.6); tf.margin_top = Inches(0.1); tf.margin_bottom = Inches(0.06)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = text
    style(r, 26, True, WHITE)
    if sub:
        p2 = tf.add_paragraph()
        r2 = p2.add_run(); r2.text = sub
        style(r2, 12, False, RGBColor(0xD5, 0xDE, 0xEC))
    ln = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.25), Inches(2.4), Inches(0.07))
    ln.fill.solid(); ln.fill.fore_color.rgb = ACCENT
    ln.line.fill.background(); ln.shadow.inherit = False


def add_card(slide, x, y, w, h, header, body_lines, header_color=PRIMARY, body_size=12.5):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    card.fill.solid(); card.fill.fore_color.rgb = LIGHT
    card.line.color.rgb = RGBColor(0xC9, 0xD4, 0xE4); card.line.width = Pt(1)
    card.shadow.inherit = False
    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.18); tf.margin_right = Inches(0.18)
    tf.margin_top = Inches(0.14); tf.margin_bottom = Inches(0.1)
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = header
    style(r, 16, True, header_color)
    p.space_after = Pt(5)
    for ln in body_lines:
        p2 = tf.add_paragraph()
        p2.space_after = Pt(4)
        r2 = p2.add_run(); r2.text = ln
        style(r2, body_size, False, GRAY)
    return card


def add_quote(slide, text, y=6.35, color=ACCENT, size=17):
    add_text(slide, 0.7, y, 12.0, 0.7, [(text, size, True, color)])


# ============ 1 封面 ============
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
bg.fill.solid(); bg.fill.fore_color.rgb = PRIMARY; bg.line.fill.background(); bg.shadow.inherit = False
add_text(s, 0.9, 1.9, 11.5, 1.4, [("phyxexp", 66, True, WHITE)])
add_text(s, 0.9, 3.25, 11.5, 0.9, [("让实验数据处理，值得信任", 30, True, ACCENT)])
add_text(s, 0.9, 4.35, 11.5, 1.8, [
    ("第四届开放原子大赛 · 图1赛道：开源基础软件与解决方案", 16, False, RGBColor(0xD5,0xDE,0xEC)),
    ("约束，本身就是可信度的来源", 18, True, WHITE),
], space_after=12)

# ============ 2 时代之变 ============
s = prs.slides.add_slide(BLANK)
add_title(s, "时代在变：人该做的，是创造")
add_text(s, 0.75, 1.75, 11.9, 3.1, [
    ("数据爆炸：实验、传感器、AI 每天都在产生海量数据。", 19, False, GRAY),
    ("机器人解放了体力劳动；AI 该解放的，是「重复的脑力劳动」。", 19, False, GRAY),
    ("重复的数据处理，正在吞噬本该用于思考的时间。", 19, False, GRAY),
], space_after=18)
add_text(s, 0.75, 5.45, 11.9, 1.3, [
    ("创造力，才是第一生产力。", 34, True, PRIMARY),
])

# ============ 3 学生困境 ============
s = prs.slides.add_slide(BLANK)
add_title(s, "一个普通学生的实验报告")
add_card(s, 0.7, 1.8, 3.8, 3.4, "算不完", [
    "一组数据要拟合、算不确定度、",
    "修约、画图，动辄几小时。",
    "",
    "时间被表格和计算占满。",
], RED)
add_card(s, 4.85, 1.8, 3.8, 3.4, "算不对", [
    "有效数字、A 类 / B 类、",
    "误差传递，一步错，全盘错。",
    "",
    "而错误往往到交作业才发现。",
], ACCENT)
add_card(s, 9.0, 1.8, 3.8, 3.4, "算完也不知对不对", [
    "截距异常、残差有趋势，",
    "没有人提醒你。",
    "",
    "结果对不对，全凭运气。",
], RED)
add_quote(s, "学生把精力耗在「算」上，而不是「想」上。")

# ============ 4 免费 AI 的问题 ============
s = prs.slides.add_slide(BLANK)
add_title(s, "免费 AI 能算，但不能信")
add_card(s, 0.7, 1.8, 2.95, 3.3, "会编数", [
    "直接给一个点估计，",
    "数值无来源、无推导。",
], RED, 12)
add_card(s, 3.8, 1.8, 2.95, 3.3, "有效数字乱", [
    "给你 15 位小数，",
    "没有修约、没有 k=2。",
], RED, 12)
add_card(s, 6.9, 1.8, 2.95, 3.3, "没有误差预算", [
    "说不清误差主要来自",
    "哪个测量量。",
], RED, 12)
add_card(s, 10.0, 1.8, 2.8, 3.3, "不可复现", [
    "再问一次，",
    "答案可能就变了。",
], RED, 12)
add_quote(s, "能算 ≠ 算对 ≠ 可证明")

# ============ 5 我们的答案 ============
s = prs.slides.add_slide(BLANK)
add_title(s, "我们的答案：受约束 Skill")
add_text(s, 0.75, 1.65, 11.9, 1.0, [
    ("不是让 AI 更会算，而是——不让它算。", 26, True, PRIMARY),
])
add_card(s, 0.7, 3.0, 3.8, 2.7, "白名单工具链", [
    "数值只能来自",
    "审查过的工具。",
    "其余一律拒绝。",
], BLUE2)
add_card(s, 4.85, 3.0, 3.8, 2.7, "强制规范", [
    "JJF 1059.1-2012 +",
    "有效数字修约 + k=2。",
    "不用记规则。",
], GREEN)
add_card(s, 9.0, 3.0, 3.8, 2.7, "可溯源", [
    "run_id + 输入哈希 +",
    "重放逐位一致。",
    "每一步都能复核。",
], ACCENT)
add_quote(s, "约束 = 可信度")

# ============ 6 对学生的意义（核心） ============
s = prs.slides.add_slide(BLANK)
add_title(s, "对学生，它意味着什么")
add_card(s, 0.6, 1.75, 2.95, 3.5, "省时间", [
    "一条命令，拟合 +",
    "不确定度 + 误差预算",
    "+ 图，全出。",
    "",
    "几小时 → 几秒钟。",
], BLUE2, 12)
add_card(s, 3.7, 1.75, 2.95, 3.5, "不犯错", [
    "规范自动执行，",
    "有效数字、修约不用记。",
    "",
    "从「怕算错」到「敢交」。",
], GREEN, 12)
add_card(s, 6.8, 1.75, 2.95, 3.5, "能复核", [
    "每一步可溯源，",
    "老师可查、自己可回看。",
    "",
    "结果不再是黑箱。",
], ACCENT, 12)
add_card(s, 9.9, 1.75, 2.9, 3.5, "会分析", [
    "自动告诉你",
    "误差主要来自哪个量。",
    "",
    "报告「误差分析」有据可写。",
], PRIMARY, 12)
add_quote(s, "把「算」交给工具，把「想」还给学生。")

# ============ 7 与一般 AI 的差异 ============
s = prs.slides.add_slide(BLANK)
add_title(s, "同一份数据，两种结果", "伏安法测电阻 · 真实运行结果")
rows = [
    ("", "免费 AI", "phyxexp（受约束）"),
    ("电阻 R", "9.848571428571425 Ω（15位）", "9.85 ± 0.04 Ω（k=2）"),
    ("不确定度", "±0.5 Ω（拍脑袋）", "±0.02 Ω（偏导传播）"),
    ("误差预算", "无", "误差主要来自 dn（97.4%）"),
    ("残差图", "无", "有（随机、无趋势）"),
    ("可复现", "否", "是（run_id + 重放一致）"),
]
tbl = s.shapes.add_table(len(rows), 3, Inches(0.7), Inches(1.75), Inches(12.0), Inches(4.1)).table
tbl.columns[0].width = Inches(2.2)
tbl.columns[1].width = Inches(4.6)
tbl.columns[2].width = Inches(5.2)
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        cell = tbl.cell(ri, ci)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = Inches(0.08); cell.margin_right = Inches(0.08)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
        r = p.add_run(); r.text = val
        if ri == 0:
            style(r, 15, True, WHITE)
            cell.fill.solid(); cell.fill.fore_color.rgb = PRIMARY
        else:
            style(r, 13.5, ci == 2, GRAY if ci == 0 else (RED if ci == 1 else GREEN))
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if ci != 2 else RGBColor(0xEE, 0xF6, 0xEE)
add_quote(s, "前者是「一个数」，后者是「一份能交的报告」。", 6.3, PRIMARY, 16)

# ============ 8 场景 ============
s = prs.slides.add_slide(BLANK)
add_title(s, "它怎么走进学生的日常")
add_card(s, 0.7, 1.8, 3.8, 3.5, "学生", [
    "贴数据 / 拍照 / Excel",
    "→ 自动识别实验",
    "→ 一条命令出结果",
    "",
    "不用报单位、不用选公式。",
], BLUE2)
add_card(s, 4.85, 1.8, 3.8, 3.5, "教师", [
    "结果带 run_id 与哈希，",
    "可查「是不是真算的」。",
    "",
    "能区分「真算」与「瞎编」。",
], GREEN)
add_card(s, 9.0, 1.8, 3.8, 3.5, "宿主", [
    "Claude Code / ChatGPT /",
    "命令行，同一套工具链。",
    "",
    "换宿主，不换可信度。",
], ACCENT)
add_quote(s, "识别层自动识别实验，不逼用户报单位。")

# ============ 9 作品形态 ============
s = prs.slides.add_slide(BLANK)
add_title(s, "作品的形态：Skill 插件 + 受约束工具链")
add_card(s, 0.7, 1.8, 3.8, 3.3, "12 实验 + 1 管线", [
    "力 / 电 / 光 / 热，",
    "覆盖普通物理实验。",
    "",
    "含杨氏模量全流程管线。",
], PRIMARY)
add_card(s, 4.85, 1.8, 3.8, 3.3, "可配置", [
    "加实验 =",
    "加一条 JSON。",
    "",
    "跨学科扩展不用改代码。",
], GREEN)
add_card(s, 9.0, 1.8, 3.8, 3.3, "双入口", [
    "SKILL.md（Claude）",
    "+ OpenAPI（ChatGPT）",
    "+ 命令行。",
], ACCENT)
add_quote(s, "对外是插件，对内是流水线。")

# ============ 10 规划 ============
s = prs.slides.add_slide(BLANK)
add_title(s, "现在与未来")
add_card(s, 0.9, 1.9, 5.4, 3.6, "现在", [
    "专注大学物理实验，",
    "把「可信」做扎实。",
    "",
    "让每一个结果都能被复核。",
], BLUE2, 14)
add_card(s, 6.9, 1.9, 5.4, 3.6, "未来", [
    "衍生更多实验场景；",
    "或开发多个 Skill，合并成",
    "更完整的数据处理能力。",
], GREEN, 14)
add_quote(s, "先把一件事做到可信，再谈无限可能。", 6.2, PRIMARY, 16)

# ============ 11 结语 ============
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
bg.fill.solid(); bg.fill.fore_color.rgb = PRIMARY; bg.line.fill.background(); bg.shadow.inherit = False
add_text(s, 0.9, 2.1, 11.5, 1.0, [("解放人，从重复中", 26, True, RGBColor(0xD5,0xDE,0xEC))])
add_text(s, 0.9, 3.1, 11.8, 1.4, [("创造力，才是第一生产力。", 40, True, WHITE)])
add_text(s, 0.9, 4.9, 11.8, 1.4, [
    ("phyxexp —— 让学生把时间花在「想」上，而不是「算」上。", 17, False, RGBColor(0xD5,0xDE,0xEC)),
], space_after=10)

out = "docs/phyxexp-参赛PPT-终版.pptx"
prs.save(out)
print("saved", out, "slides:", len(prs.slides._sldIdLst))
