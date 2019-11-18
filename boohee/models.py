from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, String

Base = declarative_base()


class Food(Base):
    __tablename__ = 'food'
    id = Column(Integer, primary_key=True)

    name = Column(String(200), nullable=True)  # 名称
    image = Column(String(200), nullable=True)  # 图片
    thumb = Column(String(200), nullable=True)  # 缩略图
    pinyin = Column(String(200), nullable=False)  # 拼音
    nickname = Column(String(50), nullable=True)  # 别名
    calorie = Column(String(50), nullable=True)  # 热量
    view_group = Column(String(50), nullable=True)  # 小分组 id
    view_group_name = Column(String(50), nullable=True)  # 小分组名
    group = Column(String(50), nullable=True)  # 大分组id
    group_name = Column(String(50), nullable=True)  # 大分组名
    light = Column(String(200), nullable=True)  # 红绿灯
    comment = Column(Text)  # 评价
    source = Column(String(50), nullable=True)  # 来源
    instruction = Column(Text)  # 详细说明
    html = Column(Text)
    not_found = Column(Integer, nullable=False, default=0)


class RelatedFood(Base):
    __tablename__ = 'related_food'
    id = Column(Integer, primary_key=True)
    food_id = Column(Integer, nullable=False)
    related_food_id = Column(Integer, nullable=False)


class FoodIngredient(Base):
    __tablename__ = 'food_ingredient'
    id = Column(Integer, primary_key=True)
    food_id = Column(Integer, nullable=False)
    ingredient_id = Column(Integer, nullable=False)
    ingredient_type = Column(String(50), nullable=True)
    ingredient_name = Column(String(200), nullable=True)
    ingredient_pinyin = Column(String(200), nullable=True)
    amount = Column(String(50), nullable=True)


class FoodNutrition(Base):
    __tablename__ = 'food_nutrition'
    id = Column(Integer, primary_key=True)
    food_id = Column(Integer, nullable=False)
    nutrition_type = Column(String(50), nullable=True)
    amount = Column(String(50), nullable=True)


class FoodWidgetUnit(Base):
    __tablename__ = 'food_widget_unit'
    id = Column(Integer, primary_key=True)
    food_id = Column(Integer, nullable=False)
    unit = Column(String(50), nullable=True)
    value = Column(String(50), nullable=True)
    is_standard = Column(Integer, nullable=False)
