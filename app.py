import streamlit as st
import pandas as pd
from datetime import datetime
from annotated_text import annotated_text
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gsheetsdb import connect
import time
import random
from math import floor
from ast import literal_eval

def on_change_slowdown():
    # prevent weird race condition when changing too fast (?)
    time.sleep(0.1)
    
df = pd.read_csv("tut_annot_sheet.csv")
df = df.fillna("")
df_rows = len(df)
candidates_sel=""
num_cands=-1
st.markdown("**1. Example Selection**")
st.markdown("Please use the control box below to move through the examples.")

index=0

index = st.number_input("Example Index", min_value=0, max_value=df_rows-1, step=1,key='yo',disabled=False)

row=df.iloc[index]
exp=row['Message']

text, focus_verb_idx = row["Text"], int(row["root_idx"])
man_sent=row['annot_4_sent']
man_verb=row['annot_4_verb']
tlist=text.split()
l1=" ".join(map(str,tlist[0:focus_verb_idx]))
l2=" ".join(map(str,tlist[focus_verb_idx:focus_verb_idx+1]))
l3=" ".join(map(str,tlist[focus_verb_idx+1:]))

st.markdown("**Selected Example:**")
#st.markdown(text)
annotated_text(
    l1,(l2, 'focus verb' ,"#00008B"),l3
)
#st.markdown("Focus verb: "+focus_verb)

st.write("  \n")

try:
    exist_sent=row['sent_met']
    exist_verb=row['verb_met']
except Exception as e:
    bool_sent=2
    bool_verb=2
    exist_sent='uwu'
    exist_verb='uwu'
if exist_sent !='uwu' and exist_verb!='uwu':
    bool_sent=0
    bool_verb=0


sent_met = st.radio(
    "1) Is the above sentence metaphorical?",
    ('Yes, it is Metaphorical', 'No, it is Literal','Invalid'),key='key1',index=bool_sent)

verb_met = st.radio(
    "2) Is the focus verb being used metaphorically?",
    ('Yes, it is being used Metaphorically', 'No, it is being used Literally','Invalid'),key='key2',index=bool_verb)





if verb_met=='Yes, it is being used Metaphorically':
    verb_met='Yes, it is Metaphorical'
elif verb_met=='No, it is being used Literally':
    verb_met='No, it is Literal'

if index==8 or index==9:    
    if verb_met=='No, it is Literal':
        textt='3) Keep the relevant metaphorical substitutes from the candidates below and Remove the others by hitting the X'
    elif verb_met=='Yes, it is Metaphorical':
        textt='3) Keep the relevant literal substitutes from the candidates below and Remove the others by hitting the X'
        
        
    if verb_met==sent_met and verb_met!="Invalid":
        st.markdown('<p class="big-font">'+textt+'</p>', unsafe_allow_html=True)
        
        if verb_met=="No, it is Literal":
            options = eval(row["literal_cands"])
        else:
            options = eval(row["literal_cands"])
        options=options[0:7]
        try:
           
            existing = eval(row["valid_replacements"])
        except Exception as e:
           
            existing = options
            
        candidates_sel = st.multiselect("Candidates", options, default=existing, on_change=on_change_slowdown())
        st.markdown('<p class="big-font">Selected: '+str(candidates_sel)+'</p>', unsafe_allow_html=True)
        #st.markdown("Selected: "+str(candidates_sel))
        st.markdown('<p class="big-font">Out of: '+str(options)+'</p>', unsafe_allow_html=True)
        #st.markdown("Out of: "+str(options))
        
        num_cands=st.number_input("4) _ is the total number of semantically correct suggestions irrespective of metaphoricity?",0,5)

if st.button('Save'):
    exp=exp.split(";")
        
    exp=" \n ".join(exp)
    
    
    if index!=8 and index!=9:
        
        if sent_met==man_sent and verb_met==man_verb:
            st.success("Correct!\n\n " + exp)
        else:
            st.error("Incorrect!\n\n "  + exp)
    else:
        ans=eval(row["metaphorical_cands"])
        casePass=True
        for word in ans:
            if word not in candidates_sel:
                
                casePass=False
        if len(candidates_sel)>5:
            casePass=False
        if index==8:
            exp3="\n\n **Reads** , **Studied** and **Tasted** best preserve the meaning of the original sentence."
            exp2="\n\nOptimal literal candidates: "+str(ans)
            
        else:
            exp2="\n\nOptimal metaphorical candidates: "+str(ans)
            exp3="\n\n **Shipping** , **Delivering** and **Initiating** best reflect the literal use of releasing in the metaphorical sense"
        if num_cands!=2 and num_cands!=3:
            casePass=False
        if sent_met==man_sent and verb_met==man_verb and casePass:
            st.success("Correcto!\n\n " + exp + exp2 + exp3 )
        else:
            st.error("Incorrecto!\n\n "  + exp + exp2 + exp3 )
        