import markdown
import os
import shelve
import time
# Import the framework
from flask import Flask, g
from flask_restful import Resource, Api, reqparse
import pandas as pd
import csv
from firebase.firebase import FirebaseAuthentication,FirebaseApplication
# Create an instance of Flask
app = Flask(__name__)

# Create the API
api = Api(app)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("devices.db")
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    # """Present some documentation"""

    # # Open the README file
    # with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:

    #     # Read the content of the file
    #     content = markdown_file.read()

    #     # Convert to HTML
    #     return markdown.markdown(content)
        return {'message': 'ok', 'data':'success'}, 200


class HeartRate(Resource):
    # def get(self):
        # shelf = get_db()
        # keys = list(shelf.keys())

        # devices = []

        # for key in keys:
        #     devices.append(shelf[key])

        # return {'message': 'Success', 'data': ''}, 200

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('date', required=True)
        parser.add_argument('time', required=True)
        parser.add_argument('data', required=True)
        # Parse the arguments into an object
        args = parser.parse_args()
        print(args['data'])
        print(args['time'])
        count_time=time.time()
        predict((args['data'].split(",")))
        print(time.time()-count_time)
        return {'message': 'ok', 'data':'success'}, 200


# class StatusStress(Resource):
#     def get(self, identifier):
#         return {'message': 'Device found', 'data': shelf[identifier]}, 200

#     def delete(self, identifier):

#         return '', 204


api.add_resource(HeartRate, '/hearrate')
# api.add_resource(StatusStress, '/statusstress/<string:identifier>')

def root_directory():
    current_path = os.path.abspath(os.getcwd())
    return os.path.abspath(os.path.join(current_path, os.pardir))
def data_directory():
    return os.path.join(root_directory(), "hear_rate - Copy/service/data")
def load_test_set():
    #Loading a hdf5 file is much much faster
    in_file = os.path.join(data_directory(), "final",  "data_temp.csv")
    return pd.read_csv(in_file)
def load_test(pipeline, hrv_features):
    test = load_test_set()
    X_test = test[hrv_features]
    y_prediction = pipeline.predict(X_test)
    return y_prediction[-1]
def RR_to_features(heart_data):
            print(heart_data)
            from hrvanalysis import get_frequency_domain_features,get_time_domain_features, get_poincare_plot_features
            #chuyen heart_rate_list thanh RR_list
            RR_interval = []
            for i in heart_data:
                RR_interval.append(60*1000/int(i))
            
            #tinh ra cac features
            feautures_1 = get_poincare_plot_features(RR_interval)
            SD1 = feautures_1['sd1']
            SD2 = feautures_1['sd2']
            feautures_2 = get_frequency_domain_features(RR_interval)
            LF = feautures_2['lf']
            HF = feautures_2['hf']
            LF_HF = feautures_2['lf_hf_ratio']
            HF_LF = 1/LF_HF
            LF_NU = feautures_2['lfnu']
            HF_NU = feautures_2['hfnu']
            TP = feautures_2['total_power']
            VLF = feautures_2['vlf']
            feautures_3 = get_time_domain_features(RR_interval)
            pNN50 = feautures_3['pnni_50']
            RMSSD = feautures_3['rmssd']
            MEAN_RR = feautures_3['mean_nni']
            MEDIAN_RR = feautures_3['median_nni']
            HR = feautures_3['mean_hr']
            SDRR = feautures_3['sdnn']
            SDRR_RMSSD = SDRR/RMSSD
            SDSD = feautures_3['sdsd']
            row_list = [["MEAN_RR", "MEDIAN_RR", "SDRR","RMSSD","SDSD","SDRR_RMSSD"
                        ,"HR","pNN50","SD1","SD2","VLF","LF","LF_NU","HF","HF_NU"
                        ,"TP","LF_HF","HF_LF"],
                    [MEAN_RR,MEDIAN_RR,SDRR,RMSSD,SDSD,SDRR_RMSSD,HR,pNN50,SD1,SD2
                    ,VLF,LF,LF_NU,HF,HF_NU,TP,LF_HF,HF_LF]]
            with open('service/data/final/data_temp.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(row_list)  
            return row_list[1]

def predict(list_data):
    app = FirebaseApplication('https://smartmachine-ed87d.firebaseio.com/')
    app.put('/','heart_rate',list_data)
    
    list_features = RR_to_features(list_data)
    value_stress = load_test(pipeline, hrv_features)
    list_features.append(value_stress)
    with open('service/data/data_user.csv','r') as file:
        csv_reader = csv.reader(file)
        listData = list(csv_reader)
        listData.append(list_features)
    with open('service/data/data_user.csv','w',newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(listData)
    print(value_stress)
    app = FirebaseApplication('https://smartmachine-ed87d.firebaseio.com/')
    if(value_stress=="time pressure"):
        app.put('/','stress_now',"TPS")
    if(value_stress=="interruption"):
        app.put('/','stress_now',"ITR")
    if(value_stress=="no stress"):
        app.put('/','stress_now',"NS")
    post_fb_now(value_stress)
    return value_stress

def post_fb_now(predict_label):
    global count_time
    global count_no
    global count_tp
    global count_itr
    count_time = count_time+1
    app = FirebaseApplication('https://smartmachine-ed87d.firebaseio.com/')
    c_stress = app.get('/stress/stress0/no_stress',None)
    c_tp = app.get('/stress/stress0/time_pressure',None)
    c_itr = app.get('/stress/stress0/interruption',None)
    if (c_stress+c_tp+c_itr)==720:
        app.put('/stress/stress1','no_stress',c_stress)
        app.put('/stress/stress1','time_pressure',c_tp)
        app.put('/stress/stress1','interruption',c_itr)
        app.put('/stress/stress2','no_stress',app.get('/stress/stress1/no_stress',None))
        app.put('/stress/stress2','time_pressure',app.get('/stress/stress1/time_pressure',None))
        app.put('/stress/stress2','interruption',app.get('/stress/stress1/interruption',None))
    else:
        if predict_label == 'no stress':
            count_no=count_no+1
            app.put('/stress','stress0/no_stress',app.get('/stress/stress0/no_stress',None)+1)
        if predict_label == 'time pressure':
            count_tp = count_tp+1
            app.put('/stress','stress0/time_pressure',app.get('/stress/stress0/time_pressure',None)+1)
        if predict_label == 'interruption':
            count_itr = count_itr+1
            app.put('/stress','stress0/interruption',app.get('/stress/stress0/interruption',None)+1)
    if count_time==15:
        print("send line")
        list_data=app.get('/line',None)
        for i in range(10,1,-1):
            list_data[i]['itr']=list_data[i-1]['itr']
            list_data[i]['tp']=list_data[i-1]['tp']
            list_data[i]['no_stress']=list_data[i-1]['no_stress']
        
        list_data[1]['itr']=count_itr
        list_data[1]['tp']=count_tp
        list_data[1]['no_stress']=count_no
        count_no = 0
        count_tp = 0
        count_itr = 0
        app.put('/','line',list_data)
        count_time=0


from sklearn.externals import joblib
count_time = 0
count_no = 0
count_tp = 0
count_itr = 0
pipeline = joblib.load('service/model_stress.pkl')
features_stress =load_test_set()    
target = 'condition'
hrv_features = list(features_stress)
hrv_features = [x for x in hrv_features if x not in [target]]
