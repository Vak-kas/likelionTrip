# persona/question.py

def question_logic(questions):
    mbti_counts = {'E': 0, 'I': 0, 'N': 0, 'S': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}

    questions = {key: int(value) for key, value in questions.items()}  # 여기서 모든 값을 정수로 변환
    score = 5
    mbti_counts['E'] += questions['question1']
    mbti_counts['I'] += score - questions['question1']

    mbti_counts['N'] += questions['question2']
    mbti_counts['S'] += score - questions['question2']

    mbti_counts['T'] += questions['question3']
    mbti_counts['F'] += score - questions['question3']

    mbti_counts['J'] += questions['question4']
    mbti_counts['P'] += score - questions['question4']

    mbti_counts['N'] += questions['question5']
    mbti_counts['T'] += questions['question5']
    mbti_counts['S'] += score - questions['question5']
    mbti_counts['F'] += score - questions['question5']

    mbti_counts['I'] += questions['question6']
    mbti_counts['E'] += score - questions['question6']

    mbti_counts['J'] += questions['question7']
    mbti_counts['P'] += score - questions['question7']

    mbti_counts['T'] += questions['question8']
    mbti_counts['P'] += questions['question8']
    mbti_counts['F'] += score - questions['question8']
    mbti_counts['J'] += score - questions['question8']

    mbti_counts['S'] += questions['question9']
    mbti_counts['N'] += score - questions['question9']

    mbti_counts['E'] += questions['question10']
    mbti_counts['I'] += score - questions['question10']

    return mbti_counts
