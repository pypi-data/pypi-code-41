from pykson import JsonObject, Pykson, IntegerField, StringField, ObjectListField, ListField, DateField, DateTimeField, TimestampSecondsField, ObjectField, JsonField, \
    TypeHierarchyAdapter

#
# class Score(JsonObject):
#     score = IntegerField()
#     course = StringField()
#
#     def __str__(self):
#         return str(self.course) + ": " + str(self.score)
#
#
# class Student(JsonObject):
#
#     first_name = StringField(serialized_name="fn")
#     last_name = StringField()
#     age = IntegerField()
#     birth = DateField(serialized_name='b')
#     birth_time = TimestampSecondsField(serialized_name='bt')
#     # scores = ListField(int)
#     # scores = ObjectListField(Score)
#     score = Score()
#
#     def __str__(self):
#         return "first name:" + str(self.first_name) + ", last name: " + str(self.last_name) + ", birth: " + str(self.birth_time) + ", age: " + str(self.age) + ", score: " + str(self.score)
#
#
# # print(JsonObject.get_fields(Student))
#
#
# # json_text = '{"fn":"ali", "last_name":"soltani", "age": 25, "scores": [ 20, 19]}'
# # json_text = '{"fn":"ali", "last_name":"soltani", "b":"2015-10-21", "bt": 1553717064, "age": 25, "scores": [ {"course": "algebra", "score": 20}, {"course": "statistics", "score": 19} ]}'
# json_text = '{"fn":"ali", "last_name":"soltani", "b":"2015-10-21", "bt": 1553717064, "age": 25, "score": {"course": "algebra", "score": 20}}'
# item = Pykson.from_json(json_text, Student)
#
# print(item)
# print(type(item))
#
# print(Pykson.to_json(item))


# print(type('ss') == str)



#
# from pykson import Pykson, JsonObject, IntegerField, StringField, ObjectField


class Score(JsonObject):
    score = IntegerField(serialized_name='s')
    course = StringField(serialized_name='c')
    data = JsonField(serialized_name='d')


class School(JsonObject):
    name = StringField(serialized_name='n')


class Student(JsonObject):

    first_name = StringField(serialized_name="fn")
    last_name = StringField(serialized_name="ln")
    age = IntegerField(serialized_name="a")
    school = ObjectField(School, serialized_name="sc")
    scores = ObjectListField(Score, serialized_name="s")


# json_text = '{"fn":"John", "ln":"Smith", "a": 25, "sc": {"n": "MIT"}, "s": [{"s": 100, "c":"Algebra", "d": {"m" :"Metod"}}]}'
# student = Pykson().from_json(json_text, Student)
# print(Pykson().to_json(student))
# a = student.scores[0]
# student.school


class Course(JsonObject):
    name = StringField(serialized_name='n')


class MathCourse(Course):
    teacher_name = StringField(serialized_name='tn')

    def __str__(self):
        return str(self.name) + ' ' + str(self.teacher_name)

    def __repr__(self):
        return self.__str__()


class FootballCourse(Course):
    coach_name = StringField(serialized_name='cn')

    def __str__(self):
        return str(self.name) + ' ' + str(self.coach_name)

    def __repr__(self):
        return self.__str__()


class Semester(JsonObject):
    course1 = ObjectField(Course, serialized_name="c1")
    course2 = ObjectField(Course, serialized_name="c2")

    def __str__(self):
        return '{c1:' + str(self.course1) + ', c2:' + str(self.course2)+'}'

    def __repr__(self):
        return self.__str__()

pson = Pykson()
pson.register_type_hierarchy_adapter(TypeHierarchyAdapter(
    Course,
    't',
    {
        'm': MathCourse,
        'f': FootballCourse
    }
))

semester = [Semester(course1=MathCourse(teacher_name='tavakoli', name='math'),
                    course2=FootballCourse(coach_name='ghomali', name='football'))]
semester_json = pson.to_json(semester)
print(semester_json)
d_semester = pson.from_json(semester_json, Semester)
print(d_semester)


m_course = [MathCourse(teacher_name='tavakoli', name='math'), FootballCourse(coach_name='ghomali', name='football')]
m_json = pson.to_json(m_course)
print(m_json)
d_m_course = pson.from_json(m_json, Course)
print(d_m_course)
print(type(d_m_course))


# class NormalizedOHLCAggregatedIntradayTrade(pykson.JsonObject):
#     SIDE_NONE = 0
#     SIDE_BUY = 1
#     SIDE_SELL = 2
#
#     time_point = pykson.TimestampMillisecondsField(serialized_name='tp')
#     open_price = pykson.FloatField(serialized_name='o')
#     high_price = pykson.FloatField(serialized_name='h')
#     low_price = pykson.FloatField(serialized_name='l')
#     close_price = pykson.FloatField(serialized_name='c')
#     volume = pykson.FloatField(serialized_name='v')
#     trade_count = pykson.IntegerField(serialized_name='tc')
#     sell_trade_volume = pykson.FloatField(serialized_name='stv')
#     sell_trade_count = pykson.IntegerField(serialized_name='stc')
#     buy_trade_volume = pykson.FloatField(serialized_name='btv')
#     buy_trade_count = pykson.IntegerField(serialized_name='btc')
#
#
# class NormalizedOrderBookRow(pykson.JsonObject):
#     ask_count = pykson.IntegerField(serialized_name='ac')
#     ask_price = pykson.FloatField(serialized_name='ap')
#     ask_volume = pykson.FloatField(serialized_name='av')
#     bid_volume = pykson.FloatField(serialized_name='bv')
#     bid_price = pykson.FloatField(serialized_name='bp')
#     bid_count = pykson.IntegerField(serialized_name='bc')
#
#
# class NormalizedOrderBook(pykson.JsonObject):
#     row1 = pykson.ObjectField(NormalizedOrderBookRow, serialized_name='r1')
#     row2 = pykson.ObjectField(NormalizedOrderBookRow, serialized_name='r2')
#     row3 = pykson.ObjectField(NormalizedOrderBookRow, serialized_name='r3')
#     row4 = pykson.ObjectField(NormalizedOrderBookRow, serialized_name='r4')
#     row5 = pykson.ObjectField(NormalizedOrderBookRow, serialized_name='r5')
#
#
# class NormalizedIntradayAggregatedData(pykson.JsonObject):
#     time_point = pykson.TimestampMillisecondsField(serialized_name='tp')
#     ohlcv_trade = pykson.ObjectField(NormalizedOHLCAggregatedIntradayTrade, serialized_name='t')
#     order_book = pykson.ObjectField(NormalizedOrderBook, serialized_name='b')
#
#
# class NormalizedDayAggregated(pykson.JsonObject):
#     day = pykson.DateField(serialized_name='d')
#     aggregated_data = pykson.ObjectListField(NormalizedIntradayAggregatedData, serialized_name='ad')
#
# import requests
# resp = requests.get('http://127.0.0.1:8000/crawler/intraday/IRO1BMLT0001/from/2019-03-16/to/2019-03-19/data_points_normalized/5m/')
# resp_data = Pykson.from_json(resp.text, NormalizedDayAggregated)
# print(resp_data)