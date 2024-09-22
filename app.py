import streamlit as st
import pandas as pd
import numpy as np
from random import sample, shuffle
import copy

st.session_state['fc'] = 0
st.session_state['gen'] = 0

file = st.file_uploader('Upload your flashcards here.', type = ['csv', 'xlsx'], help = '''
First column contains the terms (questions) and second column contains the definitions. No header included in the CSV file.''')
if file is not None:
    try:
        fc = pd.read_excel(file, header = None)
    except:
        fc = pd.read_csv(file, header = None)
    st.session_state['fc'] = 1
else:
    # demo flashcards
    checkbox_demo = st.checkbox('Use the demo flashcards.')
    if checkbox_demo:
        fc = pd.read_csv('LatinFlashcards50.csv', header = None)
        st.session_state['fc'] = 1

if st.session_state['fc'] == 1:

    with st.container():
        col0, col1 = st.columns([0.5, 0.5])
        with col0:
            fc.rename({0 : 'Term', 1 : 'Definition'}, axis = 1, inplace = True)
            fc[''] = pd.Series()
            st.write(fc)
            n = len(fc)
            q_all = list(fc['Term'])
            a_all = list(fc['Definition'])
            for i in range(n):
                q_all[i] = q_all[i].replace('$', '\$')
                q_all[i] = q_all[i].replace('>', '\>')
            
        with col1:
            # number of questions
            n_q = st.number_input('Number of Questions', 1, n, value = 20)
            # number of choices 
            n_c = st.number_input('Number of Choices', 3, 6, value = 5)
            if st.session_state['gen'] == 0:
                if 'q_list' not in st.session_state:
                    st.write(f'Click "Generate" to generate {n_q} multiple-choice questions with {n_c} choices each.')
                    button_generate = st.button('Generate')
                    if button_generate:
                        st.session_state['gen'] = 1
                else:
                    st.session_state['gen'] = 1

if st.session_state['gen'] == 1:

    # questions
    if 'q_list' not in st.session_state:
        st.session_state['q_list'] = sample(q_all, n_q)
        q_list = st.session_state['q_list']
    else:
        q_list = st.session_state['q_list']

    # correct answers
    ca_list = []
    for i in range(n_q):
        idx = q_all.index(q_list[i])
        ca_list.append(a_all[idx])

    # st.write('Questions')
    # st.write(q_list)
    # st.write('Correct Answers')
    # st.write(ca_list)

    # remaining answers
    ra_list = [[a for a in a_all if a != ca_list[i]] for i in range(n_q)]

    if 'wa_list' not in st.session_state:
        # wrong answers
        wa_list = []
        for i in range(n_q):
            wa = sample(ra_list[i], n_c - 1)
            wa_list.append(wa)
        st.session_state['wa_list'] = wa_list

        # correct and wrong answers
        cwa_list = copy.deepcopy(wa_list)
        
        for i in range(n_q):
            cwa_list[i].append(ca_list[i])
            shuffle(cwa_list[i])
        st.session_state['cwa_list'] = cwa_list
            
    else:
        wa_list = st.session_state['wa_list']
        cwa_list = st.session_state['cwa_list']
        
    # st.write('Wrong Answers')
    # st.write(wa_list)

    # st.write('Correct and Wrong Answers')
    # st.write(cwa_list)

    # print everything
    input_list = []
    for i in range(n_q):
        st.write(f'{i+1}. ' + q_list[i])
        input_ans = st.radio(label = f'QuestionN{i+1}',
                             options = cwa_list[i],
                             index = None,
                             label_visibility = 'collapsed')
        input_list.append(input_ans)
        
    # st.write(input_list)
    # st.write(ca_list)

    if None in input_list:
        done = False
        st.write('You are not yet done.')
    else:
        done = True
        submit = st.button('Submit')

    if done == True and submit:

        # wrong questions
        wq_list = []
        for i in range(n_q):
            if input_list[i] != ca_list[i] and input_list[i] != None:
                wq_list.append([i, q_list[i]])

        # score
        n_wq = len(wq_list)
        st.write(f'Number of wrong questions: {n_wq}')
        for i in range(n_wq):
            st.write(f'Q{wq_list[i][0]+1}: {wq_list[i][1]}')
        score = (1-(n_wq/n_q))*100
        st.write(f'Score: {score}%')

        if score > 99:
            st.write('Good job!')
        else:
            st.write('Try again! Replace your answers and click Submit.')            

