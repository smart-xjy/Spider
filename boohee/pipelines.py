# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from boohee.models import Food, RelatedFood, FoodIngredient, FoodNutrition, FoodWidgetUnit


class BooheePipeline(object):
    def __init__(self, db_driver, db_user, db_password, db_host, db_port, db_name):
        self.session = None
        self.db_driver = db_driver
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_driver=crawler.settings.get('DB_DRIVER'),
            db_user=crawler.settings.get('DB_USER'),
            db_password=crawler.settings.get('DB_PASSWORD'),
            db_host=crawler.settings.get('DB_HOST'),
            db_port=crawler.settings.get('DB_PORT'),
            db_name=crawler.settings.get('DB_NAME'),
        )

    def open_spider(self, spider):
        engine = create_engine(
            "{db_driver}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8".format(
                db_driver=self.db_driver,
                db_user=self.db_user,
                db_password=self.db_password,
                db_host=self.db_host,
                db_port=self.db_port,
                db_name=self.db_name,
            )
        )
        session = sessionmaker(bind=engine)
        self.session = session()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        try:
            existed_food = self.session.query(Food).filter(Food.pinyin == item['pinyin']).first()
            food = Food() if existed_food is None else existed_food

            food.name = item['name'] if 'name' in item else ''
            food.image = item['image'] if 'image' in item else ''
            food.thumb = item['thumb'] if 'thumb' in item else ''
            food.pinyin = item['pinyin']
            food.nickname = item['nickname'] if 'nickname' in item else ''
            food.calorie = item['calorie'] if 'calorie' in item else ''
            food.view_group = int(item['view_group']) if 'view_group' in item else None
            food.view_group_name = item['view_group_name'] if 'view_group_name' in item else ''
            food.group = int(item['group']) if 'group' in item else None
            food.group_name = item['group_name'] if 'group_name' in item else ''
            food.light = item['light'] if 'light' in item else ''
            food.comment = item['comment'] if 'comment' in item else ''
            food.source = item['source'] if 'source' in item else ''
            food.instruction = item['instruction'] if 'instruction' in item else ''
            if food.pinyin == 'chaodoufusong2':
                food.instruction = '<p> 1. 嫩豆腐片去表皮，切成黄豆大小的粒；<br>2. 将豆腐粒放入沸水锅中焯一下，捞出沥干；<br>3. 虾米用开水浸泡后，切成细粒；<br>4. 鸡肉洗净，煮熟，切成粒；<br>5. 熟火腿切成细粒；<br>6. 猪瘦肉洗净，煮熟，切成粒；<br>7. 水发香菇切成粒；<br>8. 炒锅置旺火，下入熟猪油，烧至六成热，将豆腐粒落锅炸至略黄时，倒入漏勺中沥去油；<br>9. 炒锅内留底油25克，回置火上，投入葱白末煸香，烹入黄酒，下入豆腐粒、熟鸡肉粒、熟火腿粒、猪肉粒、虾米粒、香菇粒等；<br>10. 再加入酱油、精盐、白糖、味精和温水50毫升炒至汤汁稠浓，淋上熟猪油即成。 </p>'
            food.html = item['html'] if 'html' in item else ''
            food.not_found = item['not_found'] if 'not_found' in item else 0
            if existed_food is None:
                self.session.add(food)
                self.session.flush()
                self.session.refresh(food)
            else:
                self.session.merge(food)

            # 处理相关食物
            for related_food in item['related_food']:
                related_food_obj = self.session.query(Food).filter(Food.pinyin == related_food['pinyin']).first()
                if not related_food_obj:
                    related_food_obj = Food(pinyin=related_food['pinyin'], name=related_food['name'])
                    self.session.add(related_food_obj)
                    self.session.flush()
                    self.session.refresh(related_food_obj)
                    related_food_rel = RelatedFood(food_id=food.id, related_food_id=related_food_obj.id)
                    self.session.add(related_food_rel)
                else:
                    # 先查询关联，防止重复添加
                    related_food_rel = self.session.query(RelatedFood).filter(RelatedFood.food_id == food.id)\
                        .filter(RelatedFood.related_food_id == related_food_obj.id).first()
                    if related_food_rel is None:
                        related_food_rel = RelatedFood(food_id=food.id, related_food_id=related_food_obj.id)
                        self.session.add(related_food_rel)

            # 处理食品配料
            for ingredient in item['ingredients']:
                ingredient_obj = self.session.query(Food).filter(Food.pinyin == ingredient['pinyin']).first()
                if not ingredient_obj:
                    ingredient_obj = Food(pinyin=ingredient['pinyin'], name=ingredient['name'])
                    self.session.add(ingredient_obj)
                    self.session.flush()
                    self.session.refresh(ingredient_obj)
                    food_ingredient_rel = FoodIngredient(food_id=food.id, ingredient_id=ingredient_obj.id,
                                                         ingredient_type=ingredient['ingredient_type'],
                                                         ingredient_name=ingredient['name'],
                                                         ingredient_pinyin=ingredient['pinyin'],
                                                         amount=ingredient['amount']
                                                         )
                    self.session.add(food_ingredient_rel)
                else:
                    # 先查询关联，防止重复添加
                    food_ingredient_rel = self.session.query(FoodIngredient).filter(FoodIngredient.food_id == food.id) \
                        .filter(FoodIngredient.ingredient_id == ingredient_obj.id).first()
                    if food_ingredient_rel is None:
                        food_ingredient_rel = FoodIngredient(food_id=food.id, ingredient_id=ingredient_obj.id,
                                                             ingredient_type=ingredient['ingredient_type'],
                                                             ingredient_name=ingredient['name'],
                                                             ingredient_pinyin=ingredient['pinyin'],
                                                             amount=ingredient['amount']
                                                             )
                        self.session.add(food_ingredient_rel)

            # 处理营养信息
            for nutrition in item['nutrition']:
                nutrition_obj = FoodNutrition(food_id=food.id, nutrition_type=nutrition['nutrition_type'],
                                              amount=nutrition['amount'])
                self.session.add(nutrition_obj)
            # 处理度量单位
            for widget_unit in item['widget_unit']:
                widget_unit_obj = FoodWidgetUnit(food_id=food.id, unit=widget_unit['unit'],
                                                 value=widget_unit['value'],
                                                 is_standard=widget_unit['is_standard'])
                self.session.add(widget_unit_obj)
            self.session.commit()
        except Exception as e:
            spider.logger.info('Exception: {0}'.format(str(e)))
            self.session.rollback()
        return item
