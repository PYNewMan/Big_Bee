
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
# Create your views here.
from akcar import models
from django.db.models import Q
import urllib.parse
import numpy as np
import random
import pandas as pd
import pymysql
import json
import pymongo


class Akc_Search(View):

    def get(self,request):
        index_data = {}
        other_data = {}
        list_carid = []
        key = request.GET.get('value')
        try:
            index = models.Akcar2.objects.filter(Q(series__icontains=key) |Q(brand__icontains=key))
            for i in range(len(index)):
                list_carid.append(index[i].car_id)
                search_key = 'search%d'%i
                # index_data[search_key] = {'car_id':index[i].car_id,'brand':index[i].brand,
                #                           'car_params':json.loads(index[i].car_params),
                #                           'pic_url':json.loads(index[i].pic_url)[:2],
                #                           'score_kb':json.loads(index[i].score_kb),'series':index[i].series}
                print(index[i].brand)
                index_data[search_key] = [index[i].car_id,index[i].brand,
                                          json.loads(index[i].car_params),
                                          json.loads(index[i].pic_url)[:4],
                                          json.loads(index[i].score_kb),index[i].series]
                # print(index_data)

            arg_list = []
            for kid in list_carid:
                recomm = Smilimar_car()
                L = recomm.run(str(kid))
                arg_list = arg_list + L

            if len(arg_list) > 5:
                arg_list = arg_list[:5]
            # print(arg_list)
            if arg_list != []:
                for i in range(len(arg_list)):
                    index = models.Akcar2.objects.filter(car_id=arg_list[i])
                    search_key = 'arg_key%d' % i
                    other_data[search_key] = [index[0].car_id, index[0].brand, json.loads(index[0].car_params),
                                              json.loads(index[0].pic_url)[:4],
                                              json.loads(index[0].score_kb), index[0].series]

            # print(other_data)
            # index_data = {'search0':99}
            result = {"code": 200, "data": index_data, "ordata":other_data}
            return JsonResponse(result)

        except Exception as e:
            print(e)
            result = {"code": 404, "data": 'error'}
            return JsonResponse(result)


class Top_Five(View):

    def get(self,request):
        conn = pymongo.MongoClient('localhost', 27017)
        db = conn['car']
        myset = db['akcar']
        list_str = []
        dict_top = {}
        # my_set.find().sort([("age", 1)])
        for i in myset.find().sort([("综合评分",-1)]).skip(471).limit(20):
            # list_top = json.loads(i["pic_url"])[:4]
            # list_top = json.loads(i["综合评分"])
            # json.loads(i['pic_url'])

            index = models.Akcar2.objects.filter(car_id=i['car_id'])
            if index.exists():
                del i['_id']
                list_str.append(i)


        for num in range(10):

            # i = random.randint(0,12)
            top_key = 'top_key%d' % num
            dict_top[top_key]=list_str[num]
            print(dict_top)

        result = {"code": 200, "data": dict_top}
        return JsonResponse(result)

class Ck_Key(View):

    def get(self,request):

        car_id = request.GET.get('car_id')
        print(car_id)
        car = SimilarCarRec(int(car_id))
        l = car.NeighborCar()
        print(l)

        conn = pymongo.MongoClient('localhost', 27017)
        db = conn['car']
        myset = db['akcar']

        list_mongo = []
        for series in l:
            message = myset.find({'series':series})[0]
            del message['_id']
            list_mongo.append(message)

        check_car = myset.find({'car_id':car_id})[0]
        del check_car['_id']
        # print(check_car)
        # l = car.salient_point_sim('操控')
        # print(l)
        # SimilarCarRec.salient_point_sim(key)
        # print(key)

        result = {"code": 200, "data": list_mongo, "ordata":check_car}
        return JsonResponse(result)

class Like_Car(View):

    def get(self,request):

        caruid = request.GET.get('caruid')
        value = request.GET.get('value')
        print(caruid,value)
        car = SimilarCarRec(int(caruid))
        l = car.salient_point_sim(value)
        print(l)

        conn = pymongo.MongoClient('localhost', 27017)
        db = conn['car']
        myset = db['akcar']

        list_mongo = []
        for series in l:
            message = myset.find({'series':series})[0]
            del message['_id']
            list_mongo.append(message)
        print(list_mongo)

        # check_car = myset.find({'car_id':caruid})[0]
        # del check_car['_id']
        # print(check_car)
        # l = car.salient_point_sim('操控')
        # print(l)
        # SimilarCarRec.salient_point_sim(key)
        # print(key)

        # result = {"code": 200, "data": list_mongo, "ordata":check_car}
        result = {"code": 200, "data": list_mongo}
        return JsonResponse(result)

class SimilarCarRec:
    '''
    相似车型模块

    提供两个方法:
            第一种 NeighborCar():
		        选择与当前车型相似的五款车;
	        第二种 salient_point_sim(self, salient_point):
		        选择与当前车型相似并且有用户倾向的五款车
    '''

    def __init__(self, car_id, database='pro_file'):
        '''
        1. NeighborCar(): 找出用户喜欢的这款车的相似车型,5辆.
           salient_point_sim(self, salient_point): 找出用户喜欢的相似车型,返回用户所选择关注点的5辆, 比如用户喜好'外观',则返回相似车型中外观得分最高的5辆.

	           salient_point:'外观','内饰','空间','舒适','油耗','动力','操控','性价比'


        2. 模块用法例:
            car = SimilarCarRec('44880',database)
            l = car.NeighborCar()
            print(l)
                返回:
                    ['2018款长安CS75 1.5T PHEV进取型',
                    '2018款传祺GE3 530 互联网尊享版',
                    '2017款凯迪拉克CT6 Plug-in 30E 精英型(停产)',
                    '2018款唐DM DM 2.0T 四驱智联创领型 7座 国V',
                    '2018款荣威MARVEL X 后驱版']

            l = car.salient_point_sim('外观')
            print(l)
                返回:
                    ['2018款长安CS75 1.5T PHEV进取型',
                    '2018款力帆650 EV 舒适型',
                    '2018款传祺GE3 530 智享版',
                    '2018款云度π1 360 智派型',
                    '2019款微蓝 互联智慧型']


        3. 当前所用sql表: Akcar2

        :param car_id:用户当前所选择的车辆的car_id(car_id 可以是 str, 也可以是int)
        :param database:当前所选择的mysql database

        ///////////////////////这段注释没有用处
        ID矩阵行需=2D矩阵列
        current_car:用户目前已经选择的车的评分列表
        neighbor_car_2d:所有车评分的二维数组
        neighbor_car_ID:所有车ID的列表(包括current_car_id)
        !!!!!!!!!!!!1如果当前车没有评分,随机选择一款给予推荐!!!!!!!!!!!
        ///////////////////////
        '''
        self.mysql = pymysql.connect(port=3306, host='127.0.0.1', user='root', password='123456', database=database,
                                     charset='utf8')
        self.cur = self.mysql.cursor()
        current_car = self.__user_choiced_car_score(car_id)
        if current_car == None:
            current_car = self.__user_choiced_car_score(random.choice(self.__choice_rand_car()))
        neighbor_car_2d = self.__every_car_score()
        neighbor_car_ID = self.__every_car_id()
        self.__current_car = np.array(current_car)
        self.__neighbor_car_2d = np.array(neighbor_car_2d)
        self.__neighbor_car_ID = np.array(neighbor_car_ID)

    def __choice_rand_car(self):
        sel = 'select car_id,score_kb from Akcar2;'
        self.cur.execute(sel)
        car_det = self.cur.fetchall()
        car_id_list = []
        for car in car_det:
            car_dic = json.loads(car[1])
            try:
                if car_dic['暂无车型口碑，期待您的分享!'] == None:
                    continue
            except:
                car_id = json.loads(car[0])
                car_id_list.append(car_id)
        car_id_list = tuple(car_id_list)
        return car_id_list

    def __every_car_id(self):
        sel = 'select car_id,score_kb from Akcar2;'
        self.cur.execute(sel)
        every_car = self.cur.fetchall()

        car_id_list = []
        for car in every_car:
            car_dic = json.loads(car[1])
            try:
                if car_dic["暂无车型口碑，期待您的分享!"] == None:
                    continue
            except:
                car_id = json.loads(car[0])
                car_id_list.append(car_id)
        return car_id_list

    def __user_choiced_car_score(self, car_id):
        car_id = str(car_id)
        sel = 'select score_kb from Akcar2 where car_id=(%s);'
        self.cur.execute(sel, [car_id])
        tuple_car_score = self.cur.fetchall()
        tuple_car_score = json.loads(tuple_car_score[0][0])
        try:
            if tuple_car_score["暂无车型口碑，期待您的分享!"] == None:
                return None
        except:
            try:
                tuple_car_score['油耗'] = tuple_car_score.pop('续航')
            except:
                pass
            return [float(tuple_car_score['外观'][:3]), float(tuple_car_score['内饰'][:3]),
                    float(tuple_car_score['空间'][:3]), float(tuple_car_score['舒适'][:3]),
                    float(tuple_car_score['油耗'][:3]), float(tuple_car_score['动力'][:3]),
                    float(tuple_car_score['操控'][:3]), float(tuple_car_score['性价比'][:3])]

    def __every_car_score(self):
        sel = 'select score_kb from Akcar2;'
        self.cur.execute(sel, )
        neighbor_car_2d = self.cur.fetchall()
        neighbor_car = []
        for car_score in neighbor_car_2d:
            car_score_dic = json.loads(car_score[0])
            try:
                car_score_dic['油耗'] = car_score_dic.pop('续航')
            except:
                pass
            try:
                if car_score_dic["暂无车型口碑，期待您的分享!"] == None:
                    continue
            except:
                now_car = [float(car_score_dic['外观'][:3]), float(car_score_dic['内饰'][:3]),
                           float(car_score_dic['空间'][:3]), float(car_score_dic['舒适'][:3]),
                           float(car_score_dic['油耗'][:3]), float(car_score_dic['动力'][:3]),
                           float(car_score_dic['操控'][:3]), float(car_score_dic['性价比'][:3])]
                neighbor_car.append(now_car)

        return neighbor_car

    def NeighborCar(self):
        neighbor_car_mat = self.__find_neighbor_car()
        neighbor_car_list = list(neighbor_car_mat[:5])
        sel = 'select series from Akcar2 where car_id in (%s,%s,%s,%s,%s);'
        self.cur.execute(sel, [int(neighbor_car_list[0]), int(neighbor_car_list[1]),
                               int(neighbor_car_list[2]), int(neighbor_car_list[3]),
                               int(neighbor_car_list[4]), ])
        car_name = self.cur.fetchall()
        car_name_list = [car_name[0][0], car_name[1][0], car_name[2][0], car_name[3][0], car_name[4][0]]
        return list(car_name_list)

    def __find_neighbor_car(self):
        score = list()
        for neighbor_car in self.__neighbor_car_2d:
            sim_mat = np.sqrt(np.abs(self.__current_car ** 2 - neighbor_car ** 2))
            mat_sum = np.sum(sim_mat)
            score.append(mat_sum)
        score = np.array(score)
        score_index = np.argsort(score)
        score_index = score_index[2:22]
        neighbor_car_mat = self.__neighbor_car_ID[score_index]
        return neighbor_car_mat

    def salient_point_sim(self, salient_point):
        neighbor_car_mat = self.__find_neighbor_car()
        car_id_list = []
        all_score_list = []
        sel_all_score = 'select score_kb from Akcar2 where car_id in (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,' \
                        '%s,%s,%s,%s,%s);'
        for id in neighbor_car_mat:
            car_id_list.append(str(id))
        self.cur.execute(sel_all_score, car_id_list)
        car_score = self.cur.fetchall()

        for one_car_score in car_score:
            car_score_dic = json.loads(one_car_score[0])
            try:
                car_score_dic['油耗'] = car_score_dic.pop('续航')
            except:
                pass
            score_list = [float(car_score_dic['外观'][:3]), float(car_score_dic['内饰'][:3]),
                          float(car_score_dic['空间'][:3]), float(car_score_dic['舒适'][:3]),
                          float(car_score_dic['油耗'][:3]), float(car_score_dic['动力'][:3]),
                          float(car_score_dic['操控'][:3]), float(car_score_dic['性价比'][:3])]
            all_score_list.append(score_list)
        all_score_list = np.array(all_score_list, dtype=np.float)
        all_score_list = all_score_list.transpose()
        num = 0
        if salient_point == '外观':
            num = 0
        elif salient_point == '内饰':
            num = 1
        elif salient_point == '空间':
            num = 2
        elif salient_point == '舒适':
            num = 3
        elif salient_point == '油耗' or salient_point == '续航':
            num = 4
        elif salient_point == '动力':
            num = 5
        elif salient_point == '操控':
            num = 6
        elif salient_point == '性价比':
            num = 7
        return self.__recommended_vehicle(all_score_list, neighbor_car_mat, num)

    def __recommended_vehicle(self, all_score_list, neighbor_car_mat, num):
        rank = all_score_list[num]
        rank_num = np.argsort(-rank)[1:6]
        res = list(neighbor_car_mat[rank_num])
        re = []
        for id in res:
            re.append(str(id))
        sel = 'select series from Akcar2 where car_id in (%s,%s,%s,%s,%s);'
        self.cur.execute(sel, re)
        car_json = self.cur.fetchall()
        re.clear()
        for car in car_json:
            re.append(car[0])
        return re



#定义推荐相似车类
class Smilimar_car(object):
    def __init__(self):
        self.db = pymysql.connect(
            host='localhost',
            user='root',
            passwd='123456',
            db='pro_file',
            port=3306,
            charset='utf8'
        )
        self.cursor = self.db.cursor()
    #从Akcar2数据库中导入数据
    def get_data(self):
        sql_ = 'select car_id,score_kb from Akcar2;'
        df = pd.read_sql(sql_, self.db)
        return df
    #处理数据
    def handle_data(self,data):
        data_DF = pd.DataFrame(data)
        array = data_DF.values
        num = data_DF.shape[0]
        item = {}
        for i in range(num):
            #获取字典
            dict_ = {}
            dict_1 ={}
            Acar_id =json.loads(str(array[i][0]))
            Acar_id_str = str(Acar_id)
            dict_ = json.loads(str(array[i][1]))
            #过滤无口啤车型数据
            if dict_ == {'暂无车型口碑，期待您的分享!': None}:
                # item[Acar_id_str] = 0
                continue
            #数据去除单位处理
            dict_1['外观'] = dict_['外观'][:-2]
            dict_1['动力'] = dict_['动力'][:-2]
            dict_1['性价比'] = dict_['性价比'][:-2]
            dict_1['操控'] = dict_['操控'][:-2]
            # dict_1['油耗'] = dict_['油耗'][:-2]
            dict_1['空间'] = dict_['空间'][:-2]
            dict_1['舒适'] = dict_['舒适'][:-2]
            dict_1['动力'] = dict_['动力'][:-2]
            dict_1['综合评分'] = dict_['综合评分'][:-2]
            item[Acar_id_str] = dict_1
        ratings_matrix = pd.DataFrame(item).T
        ratings_fillzero = ratings_matrix.fillna(0)
        return ratings_fillzero
    def similar_list(self,ratings_fillzero,car_id):
        index_list = ratings_fillzero.index.values
        ratings_list = ratings_fillzero.values.astype(float)
        # print(ratings_list)

        if car_id in index_list:
            print('****已匹配****')
            L = []
            for index_rating in range(len(ratings_list)):
                x = ratings_fillzero.loc[car_id].values.astype(float)
                y = ratings_list[index_rating]
                similar_score = np.corrcoef(x, y)[0,1]
                L.append(round(similar_score,3))
            array_ = np.array(L)
            #数组控制置0处理
            array_[np.isnan(array_)] = 0
            L = array_.tolist()
            # print(L)
            return self.recomm_car(L,index_list,car_id)
        else:
            print('找不到您查的车型,请输入其它型号')
            return []

    def recomm_car(self,L,index_list,car_id):
        array = np.array(L)
        list1 = []
        sorted_indices = array.argsort()[::-1]
        # print(sorted_indices)
        recomm_sum_list = sorted_indices[:11]
        for index in recomm_sum_list:
            recomm_carId = index_list[index]
            if recomm_carId == car_id:
                continue
            list1.append(recomm_carId)
        return list1

    def run(self,car_id):
        data = self.get_data()
        ratings_fillzero = self.handle_data(data)
        L = self.similar_list(ratings_fillzero,car_id)
        return L

# if __name__ == '__main__':
#     recomm = Smilimar_car()
#     L = recomm.run('46195')











