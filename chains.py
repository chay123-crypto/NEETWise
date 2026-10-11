from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from config import CHAPTER_MAP
from chunk_stats import chunk_id,rerank_with_feedback

CHAPTER_MAP_BY_FILENAME = {
    path.replace("\\", "/").rsplit("/", 1)[-1].casefold(): chapter
    for path, chapter in CHAPTER_MAP.items()
}

def misconception_detection(inputs,retriever,ce,llm):
    retrieved_chunks=retriever.invoke(inputs)
    chunks=[(inputs,chunk.page_content) for chunk in retrieved_chunks]
    scores=ce.predict(chunks)
    
    ranking=sorted(zip(scores,retrieved_chunks),key=lambda x:x[0],reverse=True)[:3]
    top_chunks=[c for _,c in ranking]
    best_score=ranking[0][0]
    if best_score < -5:
        return iter(["What do you mean?"])
    
    context="\n\n".join([c.page_content for c in top_chunks])
    prompt=f"""You are a determined NCERT tutor checking a student's understanding.
    The student wrote: "{inputs}"
    Address the student directly in second person.
    Evaluate using ONLY the NCERT context provided.

    STEP 1 - Check if the statement is factually correct as per NCERT:
    - Are the key facts right? (correct products, correct process, correct numbers)
    STEP 2 - Give feedback:
    - If correct: start with "You are correct." then briefly confirm why.
    - If wrong: Say explicitly wrong and explain what is wrong and give the correct NCERT explanation concisely.
    - If partially correct: acknowledge what is right first, then correct what is wrong.
    STRICT RULES:
    - Do not say "correct" and then contradict it in the next line.
    - Do NOT penalize for incomplete answers or informal writing.
    - Do NOT look for philosophical implications or edge cases.
    - But DO correct clearly wrong facts — wrong products, wrong numbers, wrong ploidy.
    - Plain text only,no bullet points, no asterisks.
    Context: {context}
    Feedback:"""

    response=llm.stream(prompt)
    return response

def ask_ncert(ques,retriever,ce,llm,lang='English',answer_mode="Normal"):

    if answer_mode=="Simple":
        prompt="""You are a friendly Biology teacher explaining a 10 year old kid.Use very simple everyday language and fun analogies. Avoid all technical jargon.
    Example: Instead of "sinoatrial node generates action potential", say "the heart has a natural alarm clock that tells it when to beat" Use only the given context.
    Use numbered points only when explaining multi-step processes. Otherwise use plain paragraphs. 
    Do not explicitly add any chapter name or page number inside the answer. Do not say answers like "will be discussed later".
    If not answer in text, say "Not available in NCERT".If the question has no clear subject or topic (e.g. "what happens?", "what happens next?", "then what?"), 
    you MUST respond ONLY with "Please clarify your question." Do NOT try to guess what the student means. Do NOT search the context for a possible answer.
    Do not summarize what you already explained. Do not repeat the same information in a different form.Do not add empty numbered points.
    IMPORTANT:
    You must strictly stick the context given. Do not add any information that is not present in the context, even if it is related or you think it might be helpful.
     Stop once the concept is fully explained. Do not add extra information that is not asked in the question. Do not add information just because it is in the context. Only answer what is asked in the question without repetition.
    Language of answer :{language}
    Answer Mode is {answer_mode}. Follow it strictly.
    If {language} is English, strictly answer in English.
    If {language} is Hinglish, answer in such a way an English Student not fluent in Hindi can still understand in Hindi, like this example:
    "Mitosis ek type ka cell division hai jisme ek diploid cell divide hokar 2 identical diploid daughter cells banata hai. Chromosome number same rehta hai.
    Meiosis mein ek diploid cell divide hokar 4 haploid cells bante hain. Yeh process sexual reproduction ke liye gametes banata hai."
    Never use Devanagari script.
    context : {context}
    question : {question} 
    Answer : """
    
    elif answer_mode=="Normal":
        prompt="""You are an NCERT Tutor.Be clear and answer in detail.
    Answer only from the context given below. Be concise and to the point.
    Use numbered points only when explaining multi-step processes. Otherwise use plain paragraphs. 
    Do not explicitly add any chapter name or page number inside the answer. Do not say answers like "will be discussed later".If the question has no clear subject or topic (e.g. "what happens?", "what happens next?", "then what?"), 
   you MUST respond ONLY with "Please clarify your question." Do NOT try to guess what the student means. Do NOT search the context for a possible answer.If the question is vague or incomplete, respond only with: "Please clarify your question." Nothing else.Do not add empty numbered points.
   .Do not summarize what you already explained. Do not repeat the same information in a different form.
     IMPORTANT:
    Stop once the concept is fully explained. Do not add extra information that is not asked in the question. Do not add information just because it is in the context. Only answer what is asked in the question without repetition.
    Language of answer :{language}
    Answer Mode is {answer_mode}. Follow it strictly.
    If {language} is English, strictly answer in English.
    If {language} is Hinglish, answer in such a way an English Student not fluent in Hindi can still understand in Hindi, like this example:
    "Mitosis ek type ka cell division hai jisme ek diploid cell divide hokar 2 identical diploid daughter cells banata hai. Chromosome number same rehta hai.
    Meiosis mein ek diploid cell divide hokar 4 haploid cells bante hain. Yeh process sexual reproduction ke liye gametes banata hai."
    Never use Devanagari script.
    context : {context}
    question : {question} 
    Answer : """
    prompt=PromptTemplate.from_template(prompt).partial(language=lang,answer_mode=answer_mode)
    retrieved_chunks=retriever.invoke(ques)
    if not retrieved_chunks:
        return iter(["Not available in NCERT. Please ask a valid biology question."]),[]

    pairs=[(ques,chunk.page_content) for chunk in retrieved_chunks]
    final_results=ce.predict(pairs)

    ranked_pair=sorted(zip(final_results,retrieved_chunks), key=lambda x: x[0],reverse=True)[:3]
    top_chunks=[chunk for _,chunk in ranked_pair]
    best_score = ranked_pair[0][0]
    if best_score < -5:
        return iter(["Not available in NCERT. Please ask a valid biology question."]), []
    ranked=rerank_with_feedback(zip(retrieved_chunks,final_results))
    top_chunks=[doc for doc, _, _ in ranked[:3]]
    chain=(
        {'context':lambda _:top_chunks,'question':RunnablePassthrough()} |
        prompt|llm|StrOutputParser()
    )
    answer=chain.stream(ques)
    return answer,top_chunks

def pdf_to_chap(chunks):
    citations=[]
    seen=set()
    for chunk in chunks:
        source = chunk.metadata['source']
        page = chunk.metadata['page']
        filename = str(source).replace("\\", "/").rsplit("/", 1)[-1].casefold()
        chapter = CHAPTER_MAP_BY_FILENAME.get(filename, "Unknown Chapter")
        citation=(chapter,page+1)
        if citation not in seen:
            seen.add(citation)
            citations.append(citation)
    return citations

def answer_with_cite(ques,retriever,ce,llm,lang='English',answer_mode="Normal"):
    answer,chunks=ask_ncert(ques,retriever,ce,llm,lang,answer_mode)
    chunk_ids=[chunk_id(chunk) for chunk in chunks]
    if not chunks: 
        return answer,[],[]   
    citations=pdf_to_chap(chunks)
    return answer,citations,chunk_ids
