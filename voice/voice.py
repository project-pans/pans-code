import speech_recognition as sr
import pyttsx3 
import pyaudio
import struct
import pvporcupine
import mysql.connector
from datetime import datetime

food = []
f = open("food.txt", "r")
for line in f:
    food.append(line.strip())
f.close()

mydb = mysql.connector.connect(
    host="localhost", user="user", password="password", database="pans_data"
)
mycursor = mydb.cursor()
      
mic = sr.Microphone() 
engine = pyttsx3.init()
engine.setProperty('rate',145)
keywords = ["alexa", "ok google", "hey siri"]
#print(pvporcupine.KEYWORDS)
handle = pvporcupine.create(keywords=keywords)


porcupine = None
pa = None
audio_stream = None
operation = None

try:
    porcupine = pvporcupine.create(keywords=keywords)

    pa = pyaudio.PyAudio()

    audio_stream = pa.open(
                    rate=porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=porcupine.frame_length)

    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            engine.say("Hello, how can I help you?") 
            engine.runAndWait()
            
            while(1):    
                try:
                    r = sr.Recognizer()
                    with sr.Microphone() as source2:
                        r.adjust_for_ambient_noise(source2, duration=0.2)
                        audio2 = r.listen(source2)

                        MyText = r.recognize_google(audio2)
                        MyText = MyText.lower()
                        print(MyText)
                        if "add" in MyText:
                            found = False
                            for word in MyText.split():
                                if word in food:
                                    found = True
                                    sql = "SELECT quantity FROM items_item WHERE name = %s"
                                    val = (word,)
                                    mycursor.execute(sql, val)
                                    quantity = mycursor.fetchone()

                                    if quantity is None:
                                        sql = "INSERT INTO items_item (name, quantity, date, weight_num) VALUES (%s, %s, %s, %s)"
                                        val = (word, 1, datetime.now(), 0)
                                    else:
                                        sql = "UPDATE items_item SET quantity = %s WHERE name = %s"
                                        val = (quantity[0] + 1, word)
                                    mycursor.execute(sql, val)
                                    mydb.commit()
                                    engine.say("Item added to list") 
                                    engine.runAndWait()
                            if found == False:
                                engine.say("Please repeat the item name to add")
                                engine.runAndWait()
                                audio2 = r.listen(source2)
                                MyText = r.recognize_google(audio2)
                                MyText = MyText.lower()
                                food.append(MyText)
                                sql = "INSERT INTO items_item (name, quantity, date, weight_num) VALUES (%s, %s, %s, %s)"
                                val = (MyText, 1, datetime.now(), 0)
                                mycursor.execute(sql, val)
                                mydb.commit()
                                with open('food.txt', 'w') as f:
                                    for item in food:
                                        f.write("%s\n" % item)
                                engine.say("Item added to list") 
                                engine.runAndWait()
                            break
                        elif "remove" in MyText or "delete" in MyText:
                            for word in MyText.split():
                                if word in food:
                                    sql = "SELECT quantity FROM items_item WHERE name = %s"
                                    val = (word,)
                                    mycursor.execute(sql, val)
                                    quantity = mycursor.fetchone()
                                    if quantity[0] == 1:
                                        sql = "DELETE FROM items_item WHERE name = %s"
                                        val = (word,)
                                    elif quantity is not None:
                                        sql = "UPDATE items_item SET quantity = %s WHERE name = %s"
                                        val = (quantity[0] - 1, word)
                                    mycursor.execute(sql, val)
                                    mydb.commit()
                                    engine.say("Item removed from list") 
                                    engine.runAndWait()
                            break
                        else:
                            engine.say("Please repeat your request using the words add or remove")
                            engine.runAndWait()
                            continue
                except sr.RequestError as e:
                    print("Could not request results; {0}".format(e))
                    
                except sr.UnknownValueError:
                    print("unknown error occured")
finally:
    if porcupine is not None:
        porcupine.delete()

    if audio_stream is not None:
        audio_stream.close()

    if pa is not None:
            pa.terminate()