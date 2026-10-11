from flask import Flask,request,render_template,Response,stream_with_context,jsonify
from vectorstore import build_or_load
from retriever import llm_load, retrievers_load
from chains import misconception_detection,answer_with_cite
from db_logger import save_feedback,log_interaction,new_message_id
import json
import traceback

app=Flask(__name__)
embeddings,vectorstore,all_docs=build_or_load()
llm=llm_load()
ce,retriever=retrievers_load(all_docs, vectorstore)

@app.route('/')
def home():
    languages=['English','Hinglish']
    mode=['Normal','Simple']
    return render_template("index.html",languages=languages,answer_mode=mode)

@app.route('/misconception',methods=['POST'])
def misconception():
    input=request.form['understanding']
    if not input.strip():
        return jsonify({"error":"No input provided"}),400
    feedback=misconception_detection(input,retriever,ce,llm)
    
    def generate():
        try:
            for token in feedback:
                if hasattr(token, 'content'):
                    yield f"data: {json.dumps({'token':token.content})}\n\n"
                else:
                    yield f"data: {json.dumps({'token':token})}\n\n"
        except Exception as e:
            traceback.print_exc()
            yield f"data: {json.dumps({'token': ' [Server busy, please try again.]'})}\n\n"
        yield "data: [DONE]\n\n"
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route("/explain",methods=['POST'])
def explanation():
    lang=request.form.get('language','English')
    answer_mode=request.form.get('answer_mode','Normal')
    input=request.form['questionInput']
    if not input.strip():
        return jsonify({"error":"No input provided"}),400
    answer,citations,chunk_ids=answer_with_cite(input,retriever,ce,llm,lang=lang,answer_mode=answer_mode)
    languages=['English','Hinglish']
    answer_mode=['Normal','Simple']
    lang=lang if lang in languages else 'English'

    def generate():
        full_answer=""
        show_cites=False
        try:
            for token in answer:
                full_answer+=token
                yield f"data: {json.dumps({'token': token})}\n\n"
            show_cites=bool(citations) and 'clarify' not in full_answer.lower() and 'not available' not in full_answer.lower()
            if show_cites:
                yield f"data: {json.dumps({'citations': citations})}\n\n"
        except Exception as e:
            traceback.print_exc()
            yield f"data: {json.dumps({'token': ' [Server busy, please try again.]'})}\n\n"
        if full_answer.strip():
            try:
                message_id=new_message_id()
                log_interaction(message_id,"explain",input,full_answer,citations if show_cites else [],lang,answer_mode,chunk_ids)
                yield f"data: {json.dumps({'message_id': message_id})}\n\n"
            except Exception as e:
                traceback.print_exc()
        yield "data: [DONE]\n\n"
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route("/feedback",methods=['POST'])
def feedback():
    data=request.get_json(silent=True) or {}
    message_id=data.get('message_id')
    ratings=data.get('ratings',data.get('rating'))
    if not message_id or ratings not in [-1,1]:
        return jsonify({'error':'message id not found or ratings are not correct'}),400
    ok=save_feedback(message_id,ratings,data.get("comment",""))
    return jsonify({"ok":ok}),(200 if ok else 500)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=7860)