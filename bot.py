from flask import Flask  
from flask import render_template, request, jsonify
import spacy
import apiai
import mysql.connector
from mysql.connector import errorcode
import simplejson as json
import os

# creates a Flask application, named app
app = Flask(__name__)

def updateStateObj(cookie, stateObj):
        cnx = mysql.connector.connect(user=os.environ['SQLUSER'], password=os.environ['SQLPASS'],
                              host='127.0.0.1',database = 'kiwi')
        cursor = cnx.cursor()
        query = 'SELECT id, worry, relationshipA, relationshipB, certainty, last, lastResponse FROM state WHERE id = {}'
        cookieVal = cookie['value'] 
        finalQuery = query.format(cookieVal)
        cursor.execute(finalQuery)
        row = cursor.fetchone()
        stateObj['id']=str(row[0])
        stateObj['worry']=row[1]
        stateObj['relationshipA']=row[2]
        stateObj['relationshipB']=row[3]
        stateObj['certainty']=row[4]
        stateObj['last']=row[5]
        stateObj['lastResponse']=row[6]
        cursor.close()
        cnx.close()
        return 

def createStateObjAndCookie(cookie,stateObj):
  try:
        cnx = mysql.connector.connect(user=os.environ['SQLUSER'], password=os.environ['SQLPASS'],
                              host='127.0.0.1',database = 'kiwi')
        cursor = cnx.cursor()
        query = 'INSERT into state (worry, relationshipA, relationshipB, certainty, last, lastResponse) VALUES ({},{},{},{},{},{})'
        test = ('NULL','NULL','NULL','NULL','NULL','NULL')
        finalQuery = query.format(*test)
        print(finalQuery)
        cursor.execute(finalQuery)
        #cookie['value'] = cursor.lastrowid
        cookie['value'] = cursor.lastrowid
        stateObj['id']=cookie['value']
        stateObj['worry']=''
        stateObj['relationshipA']=''
        stateObj['relationshipB']=''
        stateObj['certainty']=''
        stateObj['last']=''
        stateObj['lastResponse']=''
        cnx.commit()
  except Error as e:
        print(e)
  finally:    
        cursor.close()
        cnx.close()
        return

# a route where we will display a welcome message via an HTML template
@app.route("/")
def hello():  
    message = "hello"
    return render_template('index.html', message=message)

def checkCertainties(stateObj,message):
    nlp = spacy.load('en')
    doc = nlp(message)
    tokens = []
    for token in doc:
        tokens.append(str(token).lower())
    print(tokens)
    certainWords = ["think", "sure", "certain"]
    foundCertainWords = list(set(tokens).intersection(certainWords))
    print(foundCertainWords)    

    if foundCertainWords:
        if len(foundCertainWords) == 1:
            certainWord = foundCertainWords[0]
            certainWord_index = tokens.index(certainWord)
            certainty = ' '.join(tokens[certainWord_index+1:])
            #stateObj['certainty'].append(certainty)
            stateObj['certainty']=certainty
            stateObj['last'] = 'certainty'
            stateObj['lastResponse'] = 'You seem pretty certain that {}. What is the reasoning behind this?'.format(certainty)
            return
        else:
            stateObj['last']='certainty'
            stateObj['lastResponse']='Tell me more about why you are certain about this'
            return
    stateObj['lastResponse='] = 'Tell me about what is on your mind'
    return


    

def checkRelationships(stateObj, message):
    nlp = spacy.load('en')
    doc = nlp(message)
    tokens = []
    print('doc is' ,doc)
    for token in doc:
        tokens.append(str(token).lower())    
    relationshipWords = ["if", "then", "because"]
    foundRelationshipWords = set(tokens).intersection(relationshipWords)
    

    if foundRelationshipWords:
        if "if" in foundRelationshipWords and "then" in foundRelationshipWords:
            if_index = tokens.index("if")
            then_index = tokens.index("then")
            if if_index < then_index:
                a = ' '.join(tokens[if_index+1:then_index])
                b = ' '.join(tokens[then_index+1:])
                stateObj['relationshipA']=a
                stateObj['relationshipB']=b
                print(stateObj['relationshipA'])
                #stateObj['relationships'].append([a,b])
                stateObj['last'] = 'relationship'
                stateObj['lastResponse'] = 'I understand you believe {} implies {}. Maybe we can talk more about this. What do you think the consequence of this is?'.format(a,b)
                return
            else:
                stateObj['last']=''
                stateObj['lastResponse']='That sounded pretty complex. Tell me more about your reasoning'
                return

        if "if" in foundRelationshipWords:
            if_index = tokens.index("if")
            if if_index:
                a = ' '.join(tokens[if_index+1:])
                b = ' '.join(tokens[:if_index])
                #stateObj.relationships.append([a,b])
                stateObj['relationshipA']=a
                stateObj['relationshipB']=b
                stateObj['last'] = 'relationship'
                stateObj['lastResponse'] = 'I understand you believe {} implies {}. Maybe we can talk more about this. What do you think the consequence of this is?'.format(a,b)
                return
            else:
                stateObj['last']=''
                stateObj['lastResponse']='Hmm.. Tell me more about your reasoning'
                return


        if "because" in foundRelationshipWords:
            because_index = tokens.index("because")
            if because_index:
                a = ' '.join(tokens[because_index+1:])
                b = ' '.join(tokens[:because_index])
                stateObj['relationshipA']=a
                stateObj['relationshipB']=b
                stateObj['last'] = 'relationship'
                stateObj['lastResponse'] = 'I understand you believe {} implies {}. Maybe we can talk more about this. What do you think the consequence of this is?'.format(a,b)
                return
            else:
                stateObj['last']=''
                stateObj['lastResponse']='I see, what is the consequence of that?'
                return

        stateObj['lastResponse']='Tell me about your feelings'
        return


def spacyHandleWorries(stateObj, message):
    nlp = spacy.load('en')
    doc = nlp(message)
    noun_chunks = {}
    for chunk in doc.noun_chunks:
        noun_chunks.update({chunk.root.dep_:chunk})

    found = ''
    dependencies = list(noun_chunks.keys())
    if 'dobj' in dependencies:
        found = noun_chunks['dobj']
    elif 'pobj' in dependencies:
        found = noun_chunks['pobj']
    elif 'pcomp' in dependencies:
        found = noun_chunks['pcomp']

    if found:
        #stateObj['worry'].append(found)
        stateObj['worry'] = str(found)
        stateObj['last'] = "worry"
        stateObj['lastResponse'] = "Why are you worried about {}?".format(found)
    else:
        stateObj['lastResponse'] = "I understand you are worried about something, what is it that you are worried about?"
        stateObj['last'] = "worry"     

def updateState(stateObj):
        cnx = mysql.connector.connect(user=os.environ['SQLUSER'], password=os.environ['SQLPASS'],
                              host='127.0.0.1', database="kiwi")
        cursor = cnx.cursor()
        query = 'UPDATE state SET worry = {}, relationshipA = {}, relationshipB = {}, certainty = {}, last = {}, lastResponse = {} WHERE state.id = {}'
        
        if not stateObj['worry']:
          stateObj['worry'] = 'NULL'
        else:
          stateObj['worry'] = "\'"+stateObj['worry']+'\''
        if not stateObj['relationshipA']:
          stateObj['relationshipA'] = 'NULL'
        else:
          stateObj['relationshipA'] = "\'"+stateObj['relationshipA']+'\''
        if not stateObj['relationshipB']:
          stateObj['relationshipB'] = 'NULL'
        else:
          stateObj['relationshipB'] = "\'"+stateObj['relationshipB']+'\''
        if not stateObj['certainty']:
          stateObj['certainty'] = 'NULL'
        else:
          stateObj['certainty'] = "\'"+stateObj['certainty']+'\''
        if not stateObj['last']:
          stateObj['last'] = 'NULL'
        else:
          stateObj['last'] = "\'"+stateObj['last']+'\''
        if not stateObj['lastResponse']:
          stateObj['lastResponse'] = 'NULL'
        else:
          stateObj['lastResponse'] = "\'"+stateObj['lastResponse']+'\''
        
        helpers = (stateObj['worry'],stateObj['relationshipA'],stateObj['relationshipB'],stateObj['certainty'],stateObj['last'],stateObj['lastResponse'],stateObj['id'])
        finalQuery = query.format(*helpers)
        print(finalQuery)
        cursor.execute(finalQuery)
        cnx.commit()
        cursor.close()
        cnx.close()
        return

def matchIntent(stateObj, dialogflowResponse, userMessage):

    intent = dialogflowResponse['result']['metadata']['intentName']
    responseDialog = dialogflowResponse['result']['fulfillment']['messages'][0]['speech']
   
    stateObj['last']=''
 
    if intent == 'Default Welcome Intent' or intent == 'not sure':
        return responseDialog

    if intent == 'Worry':
        spacyHandleWorries(stateObj, userMessage)

    checkRelationships(stateObj, userMessage)

    if not stateObj['relationshipA'] or stateObj['relationshipA'] == 'NULL':
        checkCertainties(stateObj,userMessage)

    updateState(stateObj)
 
    if not stateObj['lastResponse'] or stateObj['lastResponse'] == 'NULL':
      stateObj['lastResponse'] = responseDialog

    if stateObj['lastResponse'][0] == "'":
      stateObj['lastResponse'] = stateObj['lastResponse'][1:-1]    
    
    stateObj['lastResponse']=stateObj['lastResponse'].replace('my','your')    
    print("HEREERERE" + stateObj['lastResponse'])    

    return stateObj['lastResponse']


def dialogflow(message):    
    ai = apiai.ApiAI(os.environ['APIAI'])
    requestDialog = ai.text_request()
    requestDialog.lang = 'en'  # optional, default value equal 'en'
    requestDialog.session_id = "test"
    requestDialog.query = message
    responseDialog = requestDialog.getresponse()
    jsonResponse = json.loads(responseDialog.read().decode('utf-8'))
    return jsonResponse


@app.route("/test", methods = ['POST'])
def test():
    # read json + reply
    data = request.get_json()
    print(data)
    sampleTxt = 'whaaaat'
    return jsonify(name=sampleTxt)

# Task - grab cookie
@app.route("/message", methods = ['POST'])
def apiEndpoint():
    data = request.get_json()
    stateObj={}
    cookie = {'value':''}
    if 'kiwi-cookie' in request.cookies:
      print("cookie found")
      print(request.cookies)
      cookie['value'] = request.cookies['kiwi-cookie']
      updateStateObj(cookie,stateObj);
    else:
      print("cookie not found")
      createStateObjAndCookie(cookie,stateObj)
    
    print(stateObj)
    userMessage = data['userMessage']
    dialogflowResponse = dialogflow(userMessage);
    print(dialogflowResponse)
    apiResponse = matchIntent(stateObj,dialogflowResponse,userMessage)
    print(apiResponse)
    response = app.response_class(
        response=json.dumps(apiResponse),
        status=200,
        mimetype='application/json'
    )
    value = str(cookie['value'])
    print(type(value))
    response.set_cookie('kiwi-cookie', value)
    return response




# run the application
if __name__ == "__main__":  
#    app.run(host='0.0.0.0')
    app.run(debug=True)
