from flask import Flask, render_template, request,make_response,jsonify
import numpy as np
import cv2
import pandas as pd
import scipy

from sklearn.preprocessing import LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

#Preparar la red neuronal
def initmodel():
    global mlp 
    global scaler
    global le
    print("Comienzo entrenamiento")
    #recuperar dataset y añadir columna categorica de categoria
    df = pd.read_csv('final.csv')
    df['class_codified'] = le.fit_transform(df["Category"])

    #Seleccionar variables de entrada y salida
    X = df.loc[:,["R_mean","G_mean","B_mean","R_std","G_std","B_std"]]
    Y = df.loc[:,["class_codified"]]

    #Seleccionar coeficientes de escalamiento
    scaler.fit(X)
    #Escalar variables
    X = scaler.transform(X)   
    #Entrenar Modelo 
    mlp.fit(X,Y.values.ravel())
    #Predecir categoria de una imagen
def trainexample(img):
    global mlp 
    global scaler
    global le
    (B, G, R) = cv2.split(img)
    Data = {"MeanR":[],"MeanG":[],"MeanB":[],"StdR":[],"StdG":[],"StdB":[]}

    #Recuperar las estadisticas
    Data["MeanR"].append(np.mean(R))
    Data["MeanG"].append(np.mean(G))
    Data["MeanB"].append(np.mean(B))
    Data["StdR"].append(np.std(R))
    Data["StdG"].append(np.std(G))
    Data["StdB"].append(np.std(B))
    #Pasarlas a dataframe
    stats = pd.DataFrame.from_dict(Data)
    # Estandarizar variables
    X = scaler.transform(stats) 
    prediction = mlp.predict(X)
    #Retornar varible categorica a label
    predictionlabel = le.inverse_transform(prediction)
    return {"tono":predictionlabel[0],"meanR":Data["MeanR"][0],"meanG":Data["MeanG"][0],"meanB":Data["MeanB"][0],"stdR":Data["StdR"][0],"stdG":Data["StdG"][0],"stdB":Data["StdB"][0]}

#Preparar variables de red neuronal
mlp=MLPClassifier(hidden_layer_sizes=(12,12),max_iter=800000,random_state=2)
scaler = StandardScaler()
le = LabelEncoder()
initmodel()

app =Flask(__name__)


#Configurar ruta de inicio
@app.route('/')
def home():
    return render_template('index.html')

#Configurar funcion post de requerimiento de analisis de imagen a python
@app.route('/edges',methods=['POST','GET'])
def edges():
    if request.method == 'POST':
        #Leer imagen desde interfaz a formato de python
        File = request.files['picture'].read()
        npimg = np.fromstring(File, np.uint8)
        img = cv2.imdecode(npimg,cv2.IMREAD_COLOR)
        prediction = trainexample(img)
        return jsonify(prediction)  
    else:
        return "none"


if __name__ == '__main__':
    app.run(debug=True)