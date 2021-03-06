from flask import Flask, url_for, render_template, request, abort
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
from nltk.stem import WordNetLemmatizer 
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import string
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import wordnet
from kbbi import KBBI
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import string


matplotlib.use('agg')
app = Flask(__name__)

wordnet_lemmatizer = WordNetLemmatizer()
tokenizer = RegexpTokenizer(r'[a-z]+')
stop_words = set(stopwords.words('english'))
def preprocess(document):
    document = document.lower() # Convert to lowercase
    words = tokenizer.tokenize(document) # Tokenize
    words = [w for w in words if not w in stop_words] # Removing stopwords
    # Lemmatizing
    for pos in [wordnet.NOUN, wordnet.VERB, wordnet.ADJ, wordnet.ADV]:
        words = [wordnet_lemmatizer.lemmatize(x, pos) for x in words]
    return " ".join(words)
def text_process(mess):
    nopunc = [char for char in mess if char not in string.punctuation]
    nopunc = ''.join(nopunc)
    nopunc= nopunc.lower()
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    output   = stemmer.stem(nopunc)
    return "".join(output)

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/sms', methods=['GET', 'POST'])
def sms():
    if request.method == 'GET':
        return render_template('sms.html', title='SMS')
    elif request.method == 'POST':
        isi_sms = request.form['sms']
        if isi_sms == "":
            return render_template('error.html')
        else :
            cek= isi_sms.split(' ')
            try:
                for i in cek:
                    a= KBBI(i)
                    return render_template('bahasa.html')
                    break
            except:
                isi_sms= preprocess(isi_sms)
                result = model_spam.predict([isi_sms])
                if result == [0]:
                    result = "Non Spam Message"
                elif result == [1]:
                    result = "Spam Message"
                print(result)
                probability_Message = model_spam.predict_proba([isi_sms])
                probability_Message= probability_Message[0]
                labels = ['Non Spam','Spam']
                # visualisasi - pie chart
                plt.close()
                plt.figure(figsize=(5,5))
                plt.title('Probability')
                plt.pie(x=probability_Message, autopct='%1.1f%%',colors=['#a278b5','#f6c3e5'], pctdistance=1.1, labeldistance=1.3)
                plt.legend(labels)
                plt.tight_layout()

                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                graph_url = base64.b64encode(img.getvalue()).decode()
                graph = 'data:image/png;base64,{}'.format(graph_url)

                return render_template('hasil_sms.html', result=result, title="Hasil SMS",graph=graph)
    else:
        abort(404)

@app.route('/tweet', methods= ['GET', 'POST'])
def tweet():
    if request.method == 'GET':
        return render_template('tweet.html',title='Tweet')
    elif request.method == 'POST':
        isi_tweet = request.form['tweet']
        if isi_tweet == "":
            return render_template('error2.html')
        else:
            isi_tweet= text_process(isi_tweet)
            result = model_twitter.predict([isi_tweet])
            result = result[0]
            probability_tweet = model_twitter.predict_proba([isi_tweet])
            probability_tweet = probability_tweet[0]
            labels = ['anger', 'fear', 'happiness', 'love', 'sad']
            # visualisasi - pie chart
            plt.close()
            plt.figure(figsize=(5,5))
            plt.title('Probabilitas')
            plt.pie(x=probability_tweet, autopct='%1.1f%%',colors=['#381460','#b2dffb','#e7a4e4','#a278b5','#f6c3e5'], pctdistance=1.1, labeldistance=1.3)
            plt.legend(labels)
            plt.tight_layout()

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            graph_url = base64.b64encode(img.getvalue()).decode()
            graph = 'data:image/png;base64,{}'.format(graph_url)

            return render_template("hasil_tweet.html", result=result, title="Hasil Tweet", graph=graph)
    else:
        abort(404)

@app.route('/about')
def about():
    return render_template('about.html',title="About")


if __name__ == "__main__":
    model_spam = joblib.load('model_Message_Fiks')
    model_twitter = joblib.load('model_subject_fiks')
    app.run(debug=True)
