## for speech to text
import speech_recognition as sr
import nltk

def SoundToText(file="", useGoogle=False):
    '''Uses Sphinx builtin. 
    Input is a dic contained as config'''
    if file != "":
        #print(file)
        test = sr.AudioFile(file)
        Recon  = sr.Recognizer()
        with test as source:
            test_au = Recon.record(source)
            
        if not useGoogle:
            text = Recon.recognize_sphinx(test_au, language='en-US')
        else:
            ## google API requires internet connection
            ## https://cloud.google.com/speech-to-text/
            #text = Recon.recognize_google(test_au, language='en-US')
            ## only takes texts < 60 seconds!
            f = open('tony-test-fa962b69f1fb.json', 'r')
            #print(json.loads(f))
            GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()
            text = Recon.recognize_google_cloud(test_au, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
            f.close()
        
        del test
        del test_au
        del Recon
        return {file: text}
    else:
        print('STH is wrong!')
        return ""
    
def text_clean(in_text):
    '''clean and remove some common words'''
    tokenizer = nltk.tokenize.RegexpTokenizer('\w+')
    
    # Tokenizing the text
    tokens = tokenizer.tokenize(in_text)
    # A new list to hold the lowercased words
    words = []
    for word in tokens:
        words.append(word.lower())
        
    # Getting the English stop words from nltk
    sw = nltk.corpus.stopwords.words('english')
    
    # A new list with No Stop words
    words_ns = []

    # Appending to words_ns all words that are in words but not in sw
    for word in words:
        if word not in sw:
            words_ns.append(word)
    # Creating the word frequency distribution
    freqdist = nltk.probability.FreqDist(words_ns)

    # # Plotting the word frequency distribution
    # plt.clf()
    # fig=plt.figure(figsize=(6, 4))
    # plt.subplots_adjust(bottom=0.3)
    # freqdist.plot(10)
    # fig.savefig("Plot/word_freq.pdf", format="pdf")    
    # print(freqdist.most_common(5))
    
    return freqdist.most_common(5)
    # out_text = " ".join(str(x) for x in words_ns)
    # return out_text


def wer(ref, hyp ,debug=False):
    
    '''https://web.archive.org/web/20171215025927/
    http://progfruits.blogspot.com/2014/02/word-error-rate-wer-and-word.html'''
    
    r = ref.split()
    h = hyp.split()
    #costs will holds the costs, like in the Levenshtein distance algorithm
    costs = [[0 for inner in range(len(h)+1)] for outer in range(len(r)+1)]
    # backtrace will hold the operations we've done.
    # so we could later backtrace, like the WER algorithm requires us to.
    backtrace = [[0 for inner in range(len(h)+1)] for outer in range(len(r)+1)]
 
    OP_OK = 0
    OP_SUB = 1
    OP_INS = 2
    OP_DEL = 3
    
    DEL_PENALTY = 1
    # First column represents the case where we achieve zero
    # hypothesis words by deleting all reference words.
    for i in range(1, len(r)+1):
        costs[i][0] = DEL_PENALTY*i
        backtrace[i][0] = OP_DEL
    
    INS_PENALTY = 1
    # First row represents the case where we achieve the hypothesis
    # by inserting all hypothesis words into a zero-length reference.
    for j in range(1, len(h) + 1):
        costs[0][j] = INS_PENALTY * j
        backtrace[0][j] = OP_INS
     
    # computation
    SUB_PENALTY = 1
    for i in range(1, len(r)+1):
        for j in range(1, len(h)+1):
            if r[i-1] == h[j-1]:
                costs[i][j] = costs[i-1][j-1]
                backtrace[i][j] = OP_OK
            else:
                substitutionCost = costs[i-1][j-1] + SUB_PENALTY # penalty is always 1
                insertionCost    = costs[i][j-1] + INS_PENALTY   # penalty is always 1
                deletionCost     = costs[i-1][j] + DEL_PENALTY   # penalty is always 1
                 
                costs[i][j] = min(substitutionCost, insertionCost, deletionCost)
                if costs[i][j] == substitutionCost:
                    backtrace[i][j] = OP_SUB
                elif costs[i][j] == insertionCost:
                    backtrace[i][j] = OP_INS
                else:
                    backtrace[i][j] = OP_DEL
                 
    # back trace though the best route:
    i = len(r)
    j = len(h)
    numSub = 0
    numDel = 0
    numIns = 0
    numCor = 0
    if debug:
        print("OP\tREF\tHYP")
        lines = []
    while i > 0 or j > 0:
        if backtrace[i][j] == OP_OK:
            numCor += 1
            i-=1
            j-=1
            if debug:
                lines.append("OK\t" + r[i]+"\t"+h[j])
        elif backtrace[i][j] == OP_SUB:
            numSub +=1
            i-=1
            j-=1
            if debug:
                lines.append("SUB\t" + r[i]+"\t"+h[j])
        elif backtrace[i][j] == OP_INS:
            numIns += 1
            j-=1
            if debug:
                lines.append("INS\t" + "****" + "\t" + h[j])
        elif backtrace[i][j] == OP_DEL:
            numDel += 1
            i-=1
            if debug:
                lines.append("DEL\t" + r[i]+"\t"+"****")
    if debug:
        lines = reversed(lines)
        for line in lines:
            print(line)
        print("#cor " + str(numCor))
        print("#sub " + str(numSub))
        print("#del " + str(numDel))
        print("#ins " + str(numIns))
    
    wer_result = round( (numSub + numDel + numIns) / (float) (len(r)), 4)
    return wer_result
    #return {'WER':wer_result, 'Cor':numCor, 'Sub':numSub, 'Ins':numIns, 'Del':numDel}